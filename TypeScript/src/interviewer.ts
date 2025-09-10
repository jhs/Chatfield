/**
 * LangGraph-based Interviewer for Chatfield conversations
 * Manages conversation flow and state using LangGraph.js
 */

import { 
  StateGraph, 
  MemorySaver,
  START,
  END,
  Command,
  Annotation,
  addMessages,
  interrupt,
} from '@langchain/langgraph'
import { 
  BaseMessage, 
  HumanMessage, 
  AIMessage, 
  SystemMessage,
  ToolMessage 
} from '@langchain/core/messages'
// @ts-ignore - module resolution issue
import { ToolNode, toolsCondition } from '@langchain/langgraph/prebuilt'
import { ChatOpenAI } from '@langchain/openai'
import { tool } from '@langchain/core/tools'
import { z } from 'zod'
import { v4 as uuidv4 } from 'uuid'
import { Interview } from './interview'
import { wrapInterviewWithProxy } from './interview-proxy'

/**
 * State type for LangGraph conversation
 */
const InterviewState = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    reducer: addMessages,
    default: () => []
  }),
  interview: Annotation<Interview>({
    reducer: (a, b) => mergeInterviews(a, b)
  })
})

type InterviewStateType = typeof InterviewState.State

/**
 * Helper function to detect changes in _chatfield structure
 * Simplified version of Python's DeepDiff check
 */
function checkChatfieldChanges(aChatfield: any, bChatfield: any): boolean {
  // Check for field value changes
  if (aChatfield?.fields && bChatfield?.fields) {
    for (const fieldName in bChatfield.fields) {
      const aField = aChatfield.fields[fieldName]
      const bField = bChatfield.fields[fieldName]
      
      // Check if value has changed from null/undefined to something
      if (aField?.value !== bField?.value) {
        if (bField?.value != null) {
          return true // Found a change
        }
      }
    }
  }
  
  // Check for role changes (alice/bob)
  if (aChatfield?.roles && bChatfield?.roles) {
    // Check alice role
    if (aChatfield.roles.alice?.type !== bChatfield.roles.alice?.type && 
        bChatfield.roles.alice?.type && 
        aChatfield.roles.alice?.type === 'Agent') {
      return true // alice role changed from default
    }
    
    // Check bob role  
    if (aChatfield.roles.bob?.type !== bChatfield.roles.bob?.type && 
        bChatfield.roles.bob?.type &&
        aChatfield.roles.bob?.type === 'User') {
      return true // bob role changed from default
    }
    
    // Check for trait changes
    const aliceTraitsChanged = JSON.stringify(aChatfield.roles.alice?.traits) !== 
                               JSON.stringify(bChatfield.roles.alice?.traits)
    const bobTraitsChanged = JSON.stringify(aChatfield.roles.bob?.traits) !== 
                            JSON.stringify(bChatfield.roles.bob?.traits)
    if (aliceTraitsChanged || bobTraitsChanged) {
      return true
    }
  }
  
  return false // No significant changes detected
}

/**
 * Merge two Interview instances
 * Matches Python's merge_interviews logic exactly
 */
function mergeInterviews(a: Interview, b: Interview): Interview {
  // Ensure we have Interview instances with proper methods
  if (a && !(a instanceof Interview) && (a as any)._chatfield) {
    // Reconstruct Interview from plain object
    a = Object.assign(new Interview(), a)
    // Wrap with proxy to enable field access
    a = wrapInterviewWithProxy(a)
  }
  if (b && !(b instanceof Interview) && (b as any)._chatfield) {
    // Reconstruct Interview from plain object
    b = Object.assign(new Interview(), b)
    // Wrap with proxy to enable field access
    b = wrapInterviewWithProxy(b)
  }
  
  // Match Python lines 28-31: Type checking
  const aType = a?.constructor
  const bType = b?.constructor
  const aSubclass = b && a instanceof (bType as any) && aType !== bType
  const bSubclass = a && b instanceof (aType as any) && aType !== bType
  
  // Match Python lines 33-38: Subclass handling
  if (aSubclass) {
    // console.log('Reduce to subclass:', aType.name)
    return a
  }
  if (bSubclass) {
    // console.log('Reduce to subclass:', bType.name)
    return b
  }
  
  // Match Python lines 39-41: Different types check
  if (aType !== bType) {
    throw new Error(`Cannot reduce ${aType?.name} and ${bType?.name}`)
  }
  
  // Match Python lines 43-48: Check for changes
  // Simple diff for _chatfield - if no changes, return a
  if (a && b) {
    const hasChanges = checkChatfieldChanges(a._chatfield, b._chatfield)
    if (!hasChanges) {
      // console.log('Identical instances')
      return a
    }
    
    // Match Python line 57: Assume B has all the latest information
    // TODO: Python assumes B has latest info. If LangGraph doesn't guarantee ordering, this could be a bug
    return b
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
  llm_with_update!: ChatOpenAI  // Python compatibility
  llm_with_conclude!: ChatOpenAI  // Python compatibility
  llm_with_both!: ChatOpenAI  // Python compatibility
  checkpointer: MemorySaver  // Made public for test access
  private updateWrapper: any  // The update tool
  private concludeWrapper: any  // The conclude tool
  private toolNode: ToolNode  // The ToolNode for processing tools

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
    this.setupGraph()
  }

  private setupGraph() {
    const theAlice = this.interview._alice_role_name()
    const theBob = this.interview._bob_role_name()

    // Build tool schemas for each field
    const toolCallArgsSchema: Record<string, any> = {}
    const concludeArgsSchema: Record<string, any> = {}

    const interviewFieldNames = Object.keys(this.interview._chatfield.fields)
    
    for (const fieldName of interviewFieldNames) {
      const fieldMetadata = this.interview._chatfield.fields[fieldName]
      const isConclude = fieldMetadata.specs?.conclude

      // Build field schema with value and all casts
      const fieldSchema = this.buildFieldSchema(fieldName, fieldMetadata)
      
      if (isConclude) {
        concludeArgsSchema[fieldName] = fieldSchema  // Mandatory for conclude
      } else {
        toolCallArgsSchema[fieldName] = fieldSchema.optional()  // Optional for update
      }
    }

    // Create update tool using @langchain/core/tools pattern
    const updateToolName = `update_${this.interview._id()}`
    const updateToolDesc = `Record valid information shared by the ${theBob} about the ${this.interview._name()}`
    
    // Build the full schema with all fields
    const updateSchema = z.object(toolCallArgsSchema)
    
    // Create wrapper function that calls run_tool - matching Python pattern
    const updateWrapperFunc = async (input: any, config: any) => {
      // In Python, this gets state and tool_call_id injected
      // In JS, we need to handle this differently since ToolNode will call this
      const toolCallId = config?.runId || uuidv4()
      
      // We need access to state, but ToolNode doesn't provide it directly
      // So we'll process directly here and let ToolNode handle state updates
      console.log(`Tool> ${toolCallId}> ${JSON.stringify(input)}`)
      
      try {
        this.process_tool_input(this.interview, input)
        return 'Success'
      } catch (error: any) {
        const errorMsg = `Error: ${error.message}\n\n${error.stack || ''}`
        return errorMsg
      }
    }
    
    this.updateWrapper = tool(
      updateWrapperFunc,
      {
        name: updateToolName,
        description: updateToolDesc,
        schema: updateSchema
      }
    )

    // Create conclude tool
    const concludeToolName = `conclude_${this.interview._id()}`
    const concludeToolDesc = `Record key required information about the ${this.interview._name()} by summarizing, synthesizing, or recalling the conversation so far with the ${theBob}`
    
    const concludeSchema = z.object(concludeArgsSchema)
    
    // Create wrapper function that calls run_tool - matching Python pattern
    const concludeWrapperFunc = async (input: any, config: any) => {
      const toolCallId = config?.runId || uuidv4()
      
      console.log(`Tool> ${toolCallId}> ${JSON.stringify(input)}`)
      
      try {
        this.process_tool_input(this.interview, input)
        return 'Success'
      } catch (error: any) {
        const errorMsg = `Error: ${error.message}\n\n${error.stack || ''}`
        return errorMsg
      }
    }
    
    this.concludeWrapper = tool(
      concludeWrapperFunc,
      {
        name: concludeToolName,
        description: concludeToolDesc,
        schema: concludeSchema
      }
    )

    // Bind tools to LLM - matching Python's approach
    this.llm_with_update = this.llm.bindTools ? this.llm.bindTools([this.updateWrapper]) as ChatOpenAI : this.llm
    this.llm_with_conclude = this.llm.bindTools ? this.llm.bindTools([this.concludeWrapper]) as ChatOpenAI : this.llm
    this.llm_with_both = this.llm.bindTools ? this.llm.bindTools([this.updateWrapper, this.concludeWrapper]) as ChatOpenAI : this.llm
    
    // Create ToolNode with both tools
    this.toolNode = new ToolNode([this.updateWrapper, this.concludeWrapper])

    // Build the state graph - matching Python structure
    const builder = new StateGraph(InterviewState)
      .addNode('initialize', this.initialize.bind(this))
      .addNode('think', this.think.bind(this))
      .addNode('listen', this.listen.bind(this))
      .addNode('tools', this.toolNode)  // Use the ToolNode directly
      .addNode('digest', this.digest.bind(this))
      .addNode('teardown', this.teardown.bind(this))
      .addEdge(START, 'initialize')
      .addEdge('initialize', 'think')
      .addConditionalEdges('think', this.routeFromThink.bind(this))
      .addEdge('listen', 'think')
      .addConditionalEdges('tools', this.routeFromTools.bind(this), ['think', 'digest'])
      .addConditionalEdges('digest', this.routeFromDigest.bind(this), ['tools', 'think'])
      .addEdge('teardown', END)

    // Compile the graph
    this.graph = builder.compile({ checkpointer: this.checkpointer })
  }

  private async initialize(state: InterviewStateType) {
    console.log(`Initialize> ${this.interview._name()}`)
    // Populate the state with the real interview object
    return { interview: this.interview }
  }

  private async think(state: InterviewStateType) {
    console.log(`Think> ${this.getStateInterview(state)._name()}`)
    
    let newSystemMessage: BaseMessage | null = null
    
    // Add system message if this is the start
    const priorSystemMessages = (state.messages || []).filter(msg => msg instanceof SystemMessage)
    if (priorSystemMessages.length === 0) {
      console.log(`Start conversation in thread: ${this.config.configurable.thread_id}`)
      const systemPrompt = this.makeSystemPrompt(state)
      newSystemMessage = new SystemMessage(systemPrompt)
    }

    // Determine which LLM to use - matching Python logic
    let llm = null
    const latestMessage = state.messages && state.messages.length > 0 ? 
                         state.messages[state.messages.length - 1] : null
    
    if (latestMessage instanceof SystemMessage) {
      llm = this.llm // No tools after system message
    } else if (latestMessage instanceof ToolMessage && latestMessage.content === 'Success') {
      llm = this.llm // No tools after successful tool response
    }
    
    llm = llm || this.llm_with_update  // Default to update tools

    // Build messages for LLM
    const newSystemMessages = newSystemMessage ? [newSystemMessage] : []
    const allMessages = [...newSystemMessages, ...(state.messages || [])]
    const response = await llm.invoke(allMessages)
    
    // Return net-new messages
    const newMessages = [...newSystemMessages, response]
    return { messages: newMessages }
  }

  private async listen(state: InterviewStateType) {
    const interview = this.getStateInterview(state)
    console.log(`Listen> ${interview._name()}`)
    
    // Copy state back to interview for interrupt
    this.interview._copy_from(interview)

    // Get the last AI message
    const msg = state.messages && state.messages.length > 0 ? 
                state.messages[state.messages.length - 1] : null
    if (!(msg instanceof AIMessage)) {
      throw new Error(`Expected last message to be an AIMessage, got ${msg?.constructor.name}: ${msg}`)
    }

    // Interrupt to get user input
    const feedback = (msg.content as string).trim()
    const update = interrupt(feedback)
    
    console.log(`Interrupt result: ${JSON.stringify(update)}`)
    const userInput = (update as any).user_input
    const userMsg = new HumanMessage(userInput)
    
    return { messages: [userMsg] }
  }

  // Helper to get state interview safely - matching Python's _get_state_interview
  private getStateInterview(state: InterviewStateType): Interview {
    const interview = state.interview
    if (!interview || !(interview instanceof Interview)) {
      if (!interview) {
        throw new Error(`Expected state["interview"] to be an Interview instance, got undefined`)
      }
      throw new Error(`Expected state["interview"] to be an Interview instance, got ${typeof interview}: ${interview}`)
    }
    
    if (!interview._chatfield.fields || Object.keys(interview._chatfield.fields).length === 0) {
      // No fields defined is okay only for uninitialized interview
      if (interview._chatfield.type === null && interview._chatfield.desc === null) {
        // Uninitialized, which is okay
      } else {
        throw new Error(`Expected state["interview"] to have fields, got empty: ${interview}`)
      }
    }
    return interview
  }

  // Node: run_tool - matching Python's implementation
  private async run_tool(state: InterviewStateType, toolCallId: string, kwargs: Record<string, any>): Promise<Command> {
    console.log(`Tool> ${toolCallId}> ${JSON.stringify(kwargs)}`)
    
    const interview = this.getStateInterview(state)
    const preInterviewModel = interview.model_dump()
    
    let toolMsg: string
    try {
      this.process_tool_input(interview, kwargs)
      toolMsg = 'Success'
    } catch (error: any) {
      toolMsg = `Error: ${error.message}\n\n${error.stack || ''}`
    }
    
    const postInterviewModel = interview.model_dump()
    
    // Prepare the return value
    const stateUpdate: any = {}
    
    // Append a ToolMessage
    const toolMessage = new ToolMessage({
      content: toolMsg,
      tool_call_id: toolCallId
    })
    stateUpdate.messages = [toolMessage]
    
    // Check if anything changed
    if (JSON.stringify(preInterviewModel) !== JSON.stringify(postInterviewModel)) {
      stateUpdate.interview = interview
    }
    
    return new Command({ update: stateUpdate })
  }

  private async teardown(state: InterviewStateType) {
    const interview = this.getStateInterview(state)
    console.log(`Teardown> ${interview._name()}`)
    
    // Copy final state back to the original interview object
    this.interview._copy_from(interview)
    
    return {}
  }

  private routeThink(state: InterviewStateType): string {
     // console.log('Route think edge')
    
    // Check if last message has tool calls
    const lastMessage = state.messages[state.messages.length - 1]
    if (lastMessage instanceof AIMessage && lastMessage.tool_calls && lastMessage.tool_calls.length > 0) {
       // console.log(`Route: think -> tools`)
      return 'tools'
    }
    
    // Check if interview is done
    if (this.interview._done) {
       // console.log('Route: think -> teardown')
      return 'teardown'
    }
    
    return 'listen'
  }

  private makeFieldsPrompt(interview: Interview, mode: 'normal' | 'conclude' = 'normal'): string {
    const fields: string[] = []
    const theBob = interview._bob_role_name()
    
    for (const fieldName of Object.keys(interview._chatfield.fields).reverse()) {
      const field = interview._chatfield.fields[fieldName]
      if (!field) continue
      
      // Skip fields based on mode
      if (mode === 'normal' && field.specs?.conclude) {
        continue // Skip conclude fields in normal mode
      }
      if (mode === 'conclude' && !field.specs?.conclude) {
        continue // Skip normal fields in conclude mode
      }
      
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
        
        // Handle regular array-based specs (must, reject, hint)
        for (const [specType, rules] of Object.entries(field.specs)) {
          // Skip confidential and conclude as they're handled separately
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
    
    return fields.join('\n')
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
   * Process tool input and update interview state - matching Python's implementation
   */
  process_tool_input(interview: Interview, kwargs: Record<string, any>) {
    const definedArgs = Object.keys(kwargs).filter(k => kwargs[k] !== null && kwargs[k] !== undefined)
    console.log(`Tool input for ${definedArgs.length} fields: ${definedArgs.join(', ')}`)
    
    const toolArgs = kwargs  // Rename for clarity below
    for (const [fieldName, llmFieldValue] of Object.entries(toolArgs)) {
      if (llmFieldValue === null || llmFieldValue === undefined) {
        continue
      }

      // Handle both objects with model_dump and plain objects (for testing)
      let llmValues: any
      if (typeof llmFieldValue === 'object' && 'model_dump' in llmFieldValue) {
        llmValues = (llmFieldValue as any).model_dump()
      } else {
        llmValues = llmFieldValue
      }
      
      console.log(`LLM found a valid field: ${fieldName} = ${JSON.stringify(llmValues)}`)
      const chatfield = interview._get_chat_field(fieldName)
      
      if (chatfield?.value) {
        // Field already has a value - could do something sophisticated
        // For now, just overwrite like Python does
      }
      
      // Process all values and rename choice keys
      const allValues: Record<string, any> = {}
      for (const [key, val] of Object.entries(llmValues)) {
        let newKey = key
        newKey = newKey.replace(/^choose_exactly_one_/, 'as_one_')
        newKey = newKey.replace(/^choose_zero_or_one_/, 'as_maybe_')
        newKey = newKey.replace(/^choose_one_or_more_/, 'as_multi_')
        newKey = newKey.replace(/^choose_zero_or_more_/, 'as_any_')
        allValues[newKey] = val
      }
      
      chatfield.value = allValues
    }
  }

  /**
   * Process one conversation turn
   */
  async go(userInput?: string | null): Promise<string | null> {
     // console.log('Go: User input:', userInput)
    
    const currentState = await this.graph.getState(this.config)
    
    let graphInput: any
    if (currentState.values && currentState.values.messages && currentState.values.messages.length > 0) {
       // console.log('Continue conversation:', this.config.configurable.thread_id)
      graphInput = new Command({update:{}, resume:{user_input: userInput}})
    } else {
       // console.log('New conversation:', this.config.configurable.thread_id)
      const messages = userInput ? [new HumanMessage(userInput)] : []
      // Match Python: Don't include interview in initial state - let initialize node populate it
      graphInput = { messages }
    }
    
    const interrupts: string[] = []
    
    // Stream the graph execution
    const stream = await this.graph.stream(graphInput, this.config)
    
    for await (const event of stream) {
       // console.log('Event:', Object.keys(event))
      
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

  // Node: Handle confidential and conclude fields
  private async digest(state: InterviewStateType): Promise<Partial<InterviewStateType>> {
    const interview = state.interview
     // console.log(`Digest> ${interview?._name() || 'No interview'}`)
    
    if (!interview) {
       // console.log('No interview in digest state')
      return {}
    }
    
    // First digest undefined confidential fields. Then digest the conclude fields.
    for (const [fieldName, chatfield] of Object.entries(interview._chatfield.fields)) {
      if (!chatfield.specs.conclude) {
        if (chatfield.specs.confidential) {
          if (!chatfield.value) {
            return this.digestConfidential(state)
          }
        }
      }
    }
    return this.digestConclude(state)
  }
  
  private async digestConfidential(state: InterviewStateType): Promise<Partial<InterviewStateType>> {
    const interview = state.interview
     // console.log(`Digest Confidential> ${interview?._name() || 'No interview'}`)
    
    if (!interview) {
       // console.log('No interview in digestConfidential state')
      return {}
    }
    
    const fieldsPrompt: string[] = []
    const fieldDefinitions: Record<string, z.ZodTypeAny> = {}
    
    for (const [fieldName, chatfield] of Object.entries(interview._chatfield.fields)) {
      if (chatfield.specs.conclude) {
        continue
      }
      
      if (chatfield.specs.confidential && !chatfield.value) {
        // This confidential field must be marked "N/A"
        fieldsPrompt.push(`- ${fieldName}: ${chatfield.desc}`)
        const fieldDefinition = this.mkFieldDefinition(interview, fieldName, chatfield)
        fieldDefinitions[fieldName] = fieldDefinition
      } else {
        // Force the LLM to pass null for values we don't need
        fieldDefinitions[fieldName] = z.null().describe('Must be null because the field is already recorded')
      }
    }
    
    const fieldsPromptStr = fieldsPrompt.join('\n')
    
    // Build a special llm object bound to a tool which explicitly requires the proper arguments
    const toolName = `update_${interview._id()}`
    const toolDesc = (
      `Record those confidential fields about the ${interview._name()} ` +
      `from the ${interview._bob_role_name()} ` +
      `which have no relevant information so far.`
    )
    
    const confidentialTool = z.object(fieldDefinitions).describe(toolDesc)
    const llm = this.llm.bindTools([{
      name: toolName,
      description: toolDesc,
      schema: confidentialTool
    }])
    
    const sysMsg = new SystemMessage(
      `You have successfully recorded good ${interview._name()} fields. ` +
      `Now, before messaging ${interview._bob_role_name()} again, ` +
      `you must perform one more followup update to record ` +
      `that there is no relevant information for ` +
      `the not-yet-defined confidential fields, listed below to remind you. ` +
      `Use the update tool call to record that there is no forthcoming information ` +
      `for these fields. ` +
      `After a successful tool call, you may resume conversation with the ${interview._bob_role_name()} again.` +
      `\n\n` +
      `## Confidential Fields needed for ${interview._name()}\n` +
      `\n` +
      `${fieldsPromptStr}`
    )
    
    const allMessages = [...state.messages, sysMsg]
    const llmResponseMessage = await llm.invoke(allMessages)
    
    // LangGraph wants only net-new messages. Its reducer will merge them.
    const newMessages = [sysMsg, llmResponseMessage]
    return { messages: newMessages }
  }
  
  private async digestConclude(state: InterviewStateType): Promise<Partial<InterviewStateType>> {
    const interview = state.interview
     // console.log(`Digest Conclude> ${interview?._name() || 'No interview'}`)
    
    if (!interview) {
       // console.log('No interview in digestConclude state')
      return {}
    }
    
    const llm = (this as any).llm_with_conclude
    const fieldsPrompt = this.makeFieldsPrompt(interview, 'conclude')
    const sysMsg = new SystemMessage(
      `You have successfully gathered enough information ` +
      `to draw conclusions and record key information from this conversation. ` +
      `You must now record all conclusion fields, defined below.` +
      `\n\n` +
      `## Conclusion Fields needed for ${interview._name()}\n` +
      `\n` +
      `${fieldsPrompt}`
    )
    
    const allMessages = [...state.messages, sysMsg]
    const llmResponseMessage = await llm.invoke(allMessages)
    
    // LangGraph wants only net-new messages. Its reducer will merge them.
    const newMessages = [sysMsg, llmResponseMessage]
    return { messages: newMessages }
  }
  
  // Build field schema for a single field - matching Python's approach
  private buildFieldSchema(fieldName: string, fieldMetadata: any): z.ZodTypeAny {
    const castsDefinitions: Record<string, z.ZodTypeAny> = {}
    
    // Always include the base value field
    castsDefinitions.value = z.string().describe(
      `The most typical valid representation of a ${this.interview._name()} ${fieldName}`
    )
    
    // Add all casts
    const casts = fieldMetadata.casts || {}
    for (const [castName, castInfo] of Object.entries(casts)) {
      const info = castInfo as any
      const castType = info.type
      const castPrompt = info.prompt
      
      let schema: z.ZodTypeAny
      
      switch (castType) {
        case 'int':
          schema = z.number().int().describe(castPrompt)
          break
        case 'float':
          schema = z.number().describe(castPrompt)
          break
        case 'str':
          schema = z.string().describe(castPrompt)
          break
        case 'bool':
          schema = z.boolean().describe(castPrompt)
          break
        case 'list':
          schema = z.array(z.any()).describe(castPrompt)
          break
        case 'set':
          schema = z.array(z.any()).describe(castPrompt)
          break
        case 'dict':
          schema = z.record(z.string(), z.any()).describe(castPrompt)
          break
        case 'choice': {
          // Handle choice types with cardinality
          const castShortName = castName.replace(/^choose_.*_/, '')
          const prompt = castPrompt.replace('{name}', castShortName)
          const choices = info.choices as string[]
          
          let choiceSchema: z.ZodTypeAny = z.enum(choices as [string, ...string[]])
          
          if (info.multi) {
            const minLength = info.null ? 0 : 1
            const maxLength = choices.length
            choiceSchema = z.array(choiceSchema).min(minLength).max(maxLength)
          }
          
          if (info.null) {
            choiceSchema = choiceSchema.nullable()
          }
          
          schema = choiceSchema.describe(prompt)
          break
        }
        default:
          throw new Error(`Cast ${castName} bad type: ${castType}; must be one of int, float, str, bool, list, set, dict, choice`)
      }
      
      castsDefinitions[castName] = schema
    }
    
    // Return the full field schema
    return z.object(castsDefinitions).describe(fieldMetadata.desc || fieldName)
  }

  private mkFieldDefinition(interview: Interview, fieldName: string, chatfield: any): z.ZodTypeAny {
    const castsDefinitions = this.mkCastsDefinitions(chatfield)
    
    // Build the Zod schema for this field
    const fieldSchema = z.object({
      value: z.string().describe(`The most typical valid representation of a ${interview._name()} ${fieldName}`),
      ...castsDefinitions
    }).describe(chatfield.desc)
    
    return fieldSchema
  }
  
  private mkCastsDefinitions(chatfield: any): Record<string, z.ZodTypeAny> {
    const castsDefinitions: Record<string, z.ZodTypeAny> = {}
    
    const okPrimitiveTypes: Record<string, (prompt: string) => z.ZodTypeAny> = {
      'int': (prompt) => z.number().int().describe(prompt),
      'float': (prompt) => z.number().describe(prompt),
      'str': (prompt) => z.string().describe(prompt),
      'bool': (prompt) => z.boolean().describe(prompt),
      'list': (prompt) => z.array(z.any()).describe(prompt),
      'set': (prompt) => z.array(z.any()).describe(prompt),
      'dict': (prompt) => z.record(z.string(), z.any()).describe(prompt),
      'choice': (prompt) => z.string().describe(prompt) // Will be handled specially
    }
    
    const casts = chatfield.casts || {}
    for (const [castName, castInfo] of Object.entries(casts)) {
      const info = castInfo as any
      const castType = info.type
      const castPrompt = info.prompt
      
      if (castType === 'choice') {
        // Handle choice types specially
        const castShortName = castName.replace(/^choose_.*_/, '')
        const prompt = castPrompt.replace('{name}', castShortName)
        const choices = info.choices as string[]
        
        let schema: z.ZodTypeAny = z.enum(choices as [string, ...string[]])
        
        if (info.multi) {
          const minLength = info.null ? 0 : 1
          const maxLength = choices.length
          schema = z.array(schema).min(minLength).max(maxLength)
        }
        
        if (info.null) {
          schema = schema.nullable()
        }
        
        castsDefinitions[castName] = schema.describe(prompt)
      } else {
        const schemaFn = okPrimitiveTypes[castType]
        if (!schemaFn) {
          throw new Error(`Cast ${castName} bad type: ${castType}; must be one of ${Object.keys(okPrimitiveTypes).join(', ')}`)
        }
        castsDefinitions[castName] = schemaFn(castPrompt)
      }
    }
    
    return castsDefinitions
  }

  // Routing methods - matching Python's route_from_think
  private routeFromThink(state: InterviewStateType): string {
    console.log(`Route from think: ${this.getStateInterview(state)._name()}`)
    
    // Use toolsCondition to check for tool calls
    const result = toolsCondition(state as any)
    if (result === 'tools') {
      return 'tools'
    }
    
    const interview = this.getStateInterview(state)
    if (interview._done) {
      return 'teardown'
    }
    
    // Check if we should go to digest phase
    if (interview._enough) {
      console.log(`Route: think -> digest`)
      return 'digest'
    }
    
    return 'listen'
  }
  
  private routeFromTools(state: InterviewStateType): string {
    const interview = this.getStateInterview(state)
    console.log(`Route from tools: ${interview._name()}`)
    
    if (interview._enough && !interview._done) {
      console.log(`Route: tools -> digest`)
      return 'digest'
    }
    
    return 'think'
  }
  
  private routeFromDigest(state: InterviewStateType): string {
    const interview = this.getStateInterview(state)
    console.log(`Route from digest: ${interview._name()}`)
    
    // Use toolsCondition to check for tool calls
    const result = toolsCondition(state as any)
    if (result === 'tools') {
      console.log(`Route: digest -> tools`)
      return 'tools'
    }
    
    return 'think'
  }
}