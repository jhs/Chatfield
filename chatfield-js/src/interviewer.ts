/**
 * LangGraph-based Interviewer for Chatfield conversations
 * Manages conversation flow and state using LangGraph.js
 */

import { 
  StateGraph, 
  MemorySaver,
  START,
  END,
  Annotation,
  interrupt
} from '@langchain/langgraph'
import { 
  BaseMessage, 
  HumanMessage, 
  AIMessage, 
  SystemMessage,
  ToolMessage 
} from '@langchain/core/messages'
import { ChatOpenAI } from '@langchain/openai'
import { tool } from '@langchain/core/tools'
import { z } from 'zod'
import { v4 as uuidv4 } from 'uuid'
import { Interview } from './interview'

/**
 * State type for LangGraph conversation
 */
const InterviewState = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: (x, y) => [...x, ...y],
    default: () => []
  }),
  interview: Annotation<Interview>({
    reducer: (a, b) => mergeInterviews(a, b)
  })
})

type InterviewStateType = typeof InterviewState.State

/**
 * Merge two Interview instances
 */
function mergeInterviews(a: Interview, b: Interview): Interview {
  // For now, just return b (the newer state)
  // TODO: Implement proper merging logic
  if (a && b) {
    // Copy over any new field values from b to a
    for (const fieldName of Object.keys(b._chatfield.fields)) {
      const bValue = b._chatfield.fields[fieldName]?.value
      if (bValue !== undefined && bValue !== null && a._chatfield.fields[fieldName]) {
        a._chatfield.fields[fieldName].value = bValue
      }
    }
    return a
  }
  return b || a
}

/**
 * Interviewer class that orchestrates conversations using LangGraph
 */
export class Interviewer {
  interview: Interview  // Made public for test access
  graph: any  // Made public for test access
  config: any  // Made public for test access
  llm: ChatOpenAI  // Made public for test access
  llm_with_both!: ChatOpenAI  // Added for Python compatibility
  checkpointer: MemorySaver  // Made public for test access
  private llmWithTools!: ChatOpenAI
  private toolName: string

  constructor(interview: Interview, options?: { threadId?: string; llm?: any, llmId?: any }) {
    this.interview = interview
    this.checkpointer = new MemorySaver()
    this.config = {
      configurable: {
        thread_id: options?.threadId || uuidv4()
      }
    }

    // Initialize LLM (use mock if provided)
    if (options?.llm) {
      this.llm = options.llm
    } else {
      this.llm = new ChatOpenAI({
        modelName: options?.llmId || 'gpt-4o',
        temperature: 0.0
      })
    }

    // Setup tools and graph
    this.toolName = `update_${this.interview._name()}`
    this.setupGraph()
  }

  private setupGraph() {
    const theAlice = this.interview._alice_role_name()
    const theBob = this.interview._bob_role_name()

    // Create tool for updating interview fields
    const toolDescription = `Record valid information stated by the ${theBob} about the ${this.interview._name()}`
    
    // Create a simple tool function without complex Zod schemas to avoid deep type issues
    const updateToolFunc = async (args: any) => {
      console.log('Tool called with:', args)
      
      try {
        // Process the tool input
        for (const [fieldName, fieldValue] of Object.entries(args)) {
          if (fieldValue && typeof fieldValue === 'object') {
            console.log(`Setting field ${fieldName}:`, fieldValue)
            if (this.interview._chatfield.fields[fieldName]) {
              this.interview._chatfield.fields[fieldName].value = fieldValue as any
            }
          }
        }
        return 'Success'
      } catch (error: any) {
        return `Error: ${error.message}`
      }
    }

    // Create the tool with simplified schema to avoid TypeScript deep instantiation issues
    const updateTool = {
      name: this.toolName,
      description: toolDescription,
      schema: z.record(z.any()), // Simplified schema
      func: updateToolFunc
    } as any

    // Bind tools to LLM
    this.llmWithTools = this.llm.bindTools ? this.llm.bindTools([updateTool]) as ChatOpenAI : this.llm
    this.llm_with_both = this.llmWithTools  // Python compatibility

    // Build the state graph
    const builder = new StateGraph(InterviewState)
      .addNode('initialize', this.initialize.bind(this))
      .addNode('think', this.think.bind(this))
      .addNode('listen', this.listen.bind(this))
      .addNode('tools', this.toolsNode.bind(this))
      .addNode('teardown', this.teardown.bind(this))
      .addEdge(START, 'initialize')
      .addEdge('initialize', 'think')
      .addConditionalEdges('think', this.routeThink.bind(this))
      .addEdge('listen', 'think')
      .addEdge('tools', 'think')
      .addEdge('teardown', END)

    // Compile the graph
    this.graph = builder.compile({ checkpointer: this.checkpointer })
  }

  private async initialize(state: InterviewStateType) {
    console.log('Initialize:', this.interview._name())
    return {}
  }

  private async think(state: InterviewStateType) {
    console.log('Think:', this.interview._name())
    
    const newMessages: BaseMessage[] = []
    
    // Add system message if this is the start
    if (!state.messages || state.messages.length === 0) {
      console.log('Starting conversation in thread:', this.config.configurable.thread_id)
      const systemPrompt = this.makeSystemPrompt(state)
      newMessages.push(new SystemMessage(systemPrompt))
    }

    // Determine which LLM to use (with or without tools)
    let llm = this.llmWithTools
    const latestMessage = newMessages[newMessages.length - 1] || 
                         (state.messages && state.messages[state.messages.length - 1])
    
    if (latestMessage instanceof SystemMessage) {
      llm = this.llm // No tools after system message
    } else if (latestMessage instanceof ToolMessage && latestMessage.content === 'Success') {
      llm = this.llm // No tools after successful tool response
    }

    // Invoke LLM
    const allMessages = [...(state.messages || []), ...newMessages]
    const response = await llm.invoke(allMessages)
    newMessages.push(response)

    return { messages: newMessages }
  }

  private async listen(state: InterviewStateType) {
    console.log('Listen:', this.interview._name())
    
    // Copy state back to interview
    if (state.interview) {
      this.interview._copy_from(state.interview)
    }

    // Get the last AI message
    const lastMessage = state.messages[state.messages.length - 1]
    if (!(lastMessage instanceof AIMessage)) {
      throw new Error('Expected last message to be AIMessage')
    }

    // Interrupt to get user input
    const feedback = lastMessage.content as string
    const update = interrupt(feedback)
    
    console.log('Interrupt result:', update)
    const userInput = (update as any).user_input
    const userMsg = new HumanMessage(userInput)
    
    return { messages: [userMsg] }
  }

  private async toolsNode(state: InterviewStateType) {
    console.log('Tools node')
    
    // Get the last message (should have tool calls)
    const lastMessage = state.messages[state.messages.length - 1] as AIMessage
    
    if (lastMessage.tool_calls && lastMessage.tool_calls.length > 0) {
      const toolCall = lastMessage.tool_calls[0]
      
      // Process the tool call
      try {
        for (const [fieldName, fieldValue] of Object.entries(toolCall?.args || {})) {
          if (fieldValue && typeof fieldValue === 'object') {
            console.log(`Setting field ${fieldName}:`, fieldValue)
            if (this.interview._chatfield.fields[fieldName]) {
              this.interview._chatfield.fields[fieldName].value = fieldValue
            }
          }
        }
        
        const toolMessage = new ToolMessage({
          content: 'Success',
          tool_call_id: toolCall?.id || ''
        })
        
        return { 
          messages: [toolMessage],
          interview: this.interview
        }
      } catch (error: any) {
        const toolMessage = new ToolMessage({
          content: `Error: ${error.message}`,
          tool_call_id: toolCall?.id || ''
        })
        
        return { messages: [toolMessage] }
      }
    }
    
    return {}
  }

  private async teardown(state: InterviewStateType) {
    console.log('Teardown:', this.interview._name())
    
    // Copy final state back to interview
    if (state.interview) {
      this.interview._copy_from(state.interview)
    }
    
    return {}
  }

  private routeThink(state: InterviewStateType): string {
    console.log('Route think edge')
    
    // Check if last message has tool calls
    const lastMessage = state.messages[state.messages.length - 1]
    if (lastMessage instanceof AIMessage && lastMessage.tool_calls && lastMessage.tool_calls.length > 0) {
      console.log(`Route: think -> tools`)
      return 'tools'
    }
    
    // Check if interview is done
    if (this.interview._done) {
      console.log('Route: think -> teardown')
      return 'teardown'
    }
    
    return 'listen'
  }

  private makeSystemPrompt(state: InterviewStateType): string {
    const interview = state.interview || this.interview
    const collectionName = interview._name()
    const theAlice = interview._alice_role_name()
    const theBob = interview._bob_role_name()
    
    // Build field descriptions
    const fields: string[] = []
    for (const fieldName of Object.keys(interview._chatfield.fields).reverse()) {
      const field = interview._chatfield.fields[fieldName]
      if (!field) continue
      let fieldLabel = fieldName
      if (field.desc) {
        fieldLabel += `: ${field.desc}`
      }
      
      // Add specs if any
      const specs: string[] = []
      if (field.specs) {
        // Handle confidential field specially
        if (field.specs.confidential) {
          specs.push(`    - **Confidential**: Do not inquire about this explicitly nor bring it up yourself. Continue your normal behavior. However, if the ${theBob} ever volunteers or implies it, you must record this information.`)
        }
        
        // Skip conclude fields in normal prompt generation
        if (field.specs.conclude) {
          continue // Skip this field entirely for now (will be handled in conclude phase)
        }
        
        // Handle regular array-based specs (must, reject, hint)
        for (const [specType, rules] of Object.entries(field.specs)) {
          // Skip confidential and conclude as they're handled above
          if (specType === 'confidential' || specType === 'conclude') {
            continue
          }
          
          // Only process if rules is an array
          if (Array.isArray(rules)) {
            for (const rule of rules) {
              // The specType should be capitalized.
              const specLabel = specType.charAt(0).toUpperCase() + specType.slice(1)
              specs.push(`    - ${specLabel}: ${rule}`)
            }
          }
        }
      }
      
      const fieldPrompt = `- ${fieldLabel}`
      if (specs.length > 0) {
        fields.push(fieldPrompt + '\n' + specs.join('\n'))
      } else {
        fields.push(fieldPrompt)
      }
    }
    
    // Build traits
    let aliceTraits = ''
    let bobTraits = ''
    
    const aliceRole = interview._alice_role()
    if (aliceRole.traits && aliceRole.traits.length > 0) {
      aliceTraits = `# Traits and Characteristics about the ${theAlice}\n\n`
      aliceTraits += aliceRole.traits.map(t => `- ${t}`).reverse().join('\n')
    }
    
    const bobRole = interview._bob_role()
    if (bobRole.traits && bobRole.traits.length > 0) {
      bobTraits = `# Traits and Characteristics about the ${theBob}\n\n`
      bobTraits += bobRole.traits.map(t => `- ${t}`).reverse().join('\n')
    }
    
    let withTraits = ''
    let aliceAndBob = ''
    if (aliceTraits || bobTraits) {
      withTraits = ` Participants' characteristics and traits will be described below.`
      aliceAndBob = '\n\n'
      if (aliceTraits) aliceAndBob += aliceTraits
      if (aliceTraits && bobTraits) aliceAndBob += '\n\n'
      if (bobTraits) aliceAndBob += bobTraits
    }
    
    // Add description section if provided
    let descriptionSection = ''
    if (interview._chatfield.desc) {
      descriptionSection = `\n## Description\n${interview._chatfield.desc}\n\n## Fields to Collect\n`
    }
    
    return `You are the conversational ${theAlice} focused on gathering key information in conversation with the ${theBob}, detailed below.${withTraits} As soon as you encounter relevant information in conversation, immediately use tools to record information fields and their related "casts", which are cusom conversions you provide for each field. Although the ${theBob} may take the conversation anywhere, your response must fit the conversation and your respective roles while refocusing the discussion so that you can gather clear key ${collectionName} information from the ${theBob}.${aliceAndBob}

----

# Collection: ${collectionName}
${descriptionSection}
${fields.join('\n\n')}
`
  }

  /**
   * Generate system prompt for the conversation (Python compatibility)
   */
  mk_system_prompt(state: { interview: Interview }): string {
    return this.makeSystemPrompt({ interview: state.interview, messages: [] } as any)
  }

  /**
   * Process tool input and update interview state (Python compatibility)
   */
  process_tool_input(interview: Interview, toolArgs: Record<string, any>) {
    // Process the tool input
    for (const [fieldName, fieldValue] of Object.entries(toolArgs)) {
      if (fieldValue && typeof fieldValue === 'object') {
        // Handle transformation renaming (choose_exactly_one_as_* -> as_one_as_*)
        const processedValue = { ...fieldValue }
        
        // Rename transformation keys
        for (const [key, value] of Object.entries(fieldValue)) {
          if (key.startsWith('choose_exactly_one_')) {
            const newKey = key.replace('choose_exactly_one_', 'as_one_')
            processedValue[newKey] = value
            delete processedValue[key]
          } else if (key.startsWith('choose_zero_or_one_')) {
            const newKey = key.replace('choose_zero_or_one_', 'as_maybe_')
            processedValue[newKey] = value
            delete processedValue[key]
          } else if (key.startsWith('choose_one_or_more_')) {
            const newKey = key.replace('choose_one_or_more_', 'as_multi_')
            processedValue[newKey] = value
            delete processedValue[key]
          } else if (key.startsWith('choose_zero_or_more_')) {
            const newKey = key.replace('choose_zero_or_more_', 'as_any_')
            processedValue[newKey] = value
            delete processedValue[key]
          }
        }
        
        if (interview._chatfield.fields[fieldName]) {
          interview._chatfield.fields[fieldName].value = processedValue
        }
      }
    }
    
    // _done is computed automatically based on field values
  }

  /**
   * Process one conversation turn
   */
  async go(userInput?: string | null): Promise<string | null> {
    console.log('Go: User input:', userInput)
    
    const currentState = await this.graph.getState(this.config)
    
    let graphInput: any
    if (currentState.values && currentState.values.messages && currentState.values.messages.length > 0) {
      console.log('Continue conversation:', this.config.configurable.thread_id)
      graphInput = {
        __command__: {
          update: {},
          resume: { user_input: userInput }
        }
      }
    } else {
      console.log('New conversation:', this.config.configurable.thread_id)
      const messages = userInput ? [new HumanMessage(userInput)] : []
      graphInput = {
        messages,
        interview: this.interview
      }
    }
    
    const interrupts: string[] = []
    
    // Stream the graph execution
    const stream = await this.graph.stream(graphInput, this.config)
    
    for await (const event of stream) {
      console.log('Event:', Object.keys(event))
      
      // Check for interrupts
      for (const [nodeName, nodeOutput] of Object.entries(event)) {
        if (nodeName === '__interrupt__') {
          for (const message of nodeOutput as any[]) {
            interrupts.push(message.value as string)
          }
        }
      }
    }
    
    if (interrupts.length === 0) {
      return null
    }
    
    if (interrupts.length > 1) {
      throw new Error(`Multiple interrupts received: ${interrupts}`)
    }
    
    return interrupts[0] || null
  }
}