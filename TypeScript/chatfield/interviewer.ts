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
  Interrupt,
  INTERRUPT,
  GraphInterrupt,
  GraphValueError,
} from './langgraph/langgraph.server';

import { RunnableConfig } from "@langchain/core/runnables";
import { interrupt } from './interrupt/interrupt.server';

import {
  BaseMessage,
  HumanMessage,
  AIMessage,
  SystemMessage,
  ToolMessage
} from '@langchain/core/messages'
// Note: toolsCondition still needs direct import from langgraph/prebuilt
// as our wrapper doesn't re-export /prebuilt submodule
// @ts-ignore - module resolution issue
import { toolsCondition } from '@langchain/langgraph/prebuilt'
import { ChatOpenAI } from '@langchain/openai'
import { z } from 'zod'
import { v4 as uuidv4 } from 'uuid'
import { Interview } from './interview'
import { wrapInterviewWithProxy } from './interview-proxy'
import { mergeInterviews, mergeHasDigested } from './merge'
import { TemplateEngine } from './template-engine'

export type EndpointSecurityMode = 'strict' | 'warn' | 'disabled'

/**
 * State type for LangGraph conversation
 */
const InterviewState = Annotation.Root({
  messages: Annotation<BaseMessage[]>({
    default: () => [],
    reducer: addMessages,
  }),
  interview: Annotation<Interview | null>({
    default: () => null,
    reducer: (a: Interview | null, b: Interview | null) => mergeInterviews(a, b),
  }),
  hasDigestedConfidentials: Annotation<boolean>({
    default: () => false,
    reducer: mergeHasDigested,
  }),
  hasDigestedConcludes: Annotation<boolean>({
    default: () => false,
    reducer: mergeHasDigested,
  })
})

type InterviewStateType = typeof InterviewState.State


/**
 * Interviewer class that orchestrates conversations using LangGraph
 */
export class Interviewer {
  interview: Interview  // Made public for test access
  graph: any  // Made public for test access
  config: any  // Made public for test access
  llm: ChatOpenAI  // Made public for test access
  checkpointer: MemorySaver  // Made public for test access
  templateEngine: TemplateEngine

  private readonly DANGEROUS_ENDPOINTS = [
    'api.openai.com',
    'api.anthropic.com',
  ];

  constructor(interview: Interview, options?: {
    threadId?: string;
    llm?: any,
    llmId?: any,
    temperature?: number | null,
    baseUrl?: string,
    apiKey?: string,
    endpointSecurity?: EndpointSecurityMode,
  }) {
    // Isomorphic:
    // TypeScript has options parameter, Python uses all kwargs.
    const threadId = options?.threadId;
    const llm = options?.llm;
    let   llmId = options?.llmId;
    let   temperature = options?.temperature;
    let   baseUrl = options?.baseUrl;
    const apiKey = options?.apiKey;
    const endpointSecurity = options?.endpointSecurity;

    this.interview = interview
    this.templateEngine = new TemplateEngine()
    this.checkpointer = new MemorySaver()
    this.config = { configurable: { thread_id: threadId || uuidv4() } };

    // Initialize LLM (use mock if provided)
    if (llm) {
      this.llm = llm;
    } else {
      // Isomorphic:
      // TypeScript has logic to set up Browser environments.
      // Python no-ops.
      const win = this.getWindow();
      if (win) {
        // Browser environment
        if (!baseUrl || baseUrl.trim() === '') {
          throw new Error(`No baseUrl in browser environment`);
        }
      } else {
        // Server environment
        // OPENAI_BASE_URL already works due to the underlying OpenAI client.
      }

      llmId = llmId || 'openai:gpt-4o';
      temperature = temperature || 0.0;
      if (['openai:o3-mini', 'openai:o3'].includes(llmId)) {
        temperature = null;
      }

      // Isomorphic:
      // Both languages use ChatOpenAI directly from their respective packages.
      // Both throw if the 'openai:' prefix is missing.
      if (! llmId.startsWith('openai:')) {
        throw new Error(`LLM ID must start with "openai:", got ${llmId}`);
      } else {
        llmId = llmId.slice('openai:'.length);
      }

      const llmConfig: any = {
        apiKey: apiKey,
        modelName: llmId,
        temperature: temperature,
        configuration: {
          baseURL: baseUrl,
        }
      }
      this.llm = new ChatOpenAI(llmConfig)
    }

    // Isomorphic:
    // Both languages implement security modes.
    // Both languages default to "disabled" as servers.
    // But in a browser, the default is "strict".
    const isBrowser = this.getWindow() !== null
    let securityMode = endpointSecurity || ( isBrowser ? 'strict' : 'disabled' );
    this.detectDangerousEndpoint(this.llm, securityMode);
    this.setupGraph()
  }

  private setupGraph() {
    const theBob = this.interview._bob_role_name

    // Build the state graph - matching Python structure
    const builder = new StateGraph(InterviewState)
      .addNode('initialize', this.initialize.bind(this))
      .addNode('think', this.think.bind(this))
      .addNode('listen', this.listen.bind(this))
      .addNode('tools', this.tools.bind(this))
      .addNode('digest_confidentials', this.digest_confidentials.bind(this))
      .addNode('digest_concludes', this.digest_concludes.bind(this))
      .addNode('teardown', this.teardown.bind(this))

      .addEdge(START, 'initialize')
      .addEdge('initialize', 'think')

      .addConditionalEdges('think', this.routeFromThink.bind(this))

      .addEdge('listen', 'think')

      .addConditionalEdges('tools', this.routeFromTools.bind(this), ['think', 'digest_confidentials', 'digest_concludes'])
      .addConditionalEdges('digest_confidentials', this.routeFromDigest.bind(this), ['tools', 'think'])
      .addConditionalEdges('digest_concludes', this.routeFromDigest.bind(this), ['tools', 'think'])
      .addEdge('teardown', END)

    // Compile the graph
    this.graph = builder.compile({ checkpointer: this.checkpointer })
  }

  private getWindow(): any {
    if (typeof window !== 'undefined') {
      return window;
    }

    if (typeof global !== 'undefined' && (global as any).window !== undefined) {
      return (global as any).window;
    }

    return null;
  }

  private detectDangerousEndpoint(llm: any, mode: EndpointSecurityMode): void {
    /**
     * Check for dangerous API endpoints based on security mode.
     *
     * Args:
     *   llm: The LLM instance to check
     *   mode: Security mode ('strict', 'warn', or 'disabled')
     *
     * Throws:
     *   Error: If mode is 'strict' and a dangerous endpoint is detected
     */

    // Isomorphic:
    // Extract hostname from LLM instance.
    // Python uses llm.openai_api_base
    // TypeScript uses llm.clientConfig?.baseURL
    let hostname: string | null = null
    const baseUrl = llm.clientConfig?.baseURL
    if (baseUrl) {
      try {
        const parsed = new URL(baseUrl)
        hostname = parsed.hostname
      } catch (e) {
        // Invalid URL, treat as null
      }
    }

    // Isomorphic:
    // Callback function to handle dangerous endpoint detection
    const onDangerousEndpoint = (message: string) => {
      if (mode === 'disabled') {
        console.log(`Endpoint: ${message}`)
      } else if (mode === 'warn') {
        console.warn(`WARNING: ${message}. Your API key may be exposed to end users.`)
      } else if (mode === 'strict') {
        throw new Error(
          `SECURITY ERROR: ${message}. ` +
          `This may expose your API key to end users. Use a backend proxy instead.`
        )
      }
    }

    // Isomorphic:
    // Browser-specific logic (TypeScript only)
    // Enforce: Cannot disable security in browser
    const isBrowser = this.getWindow() !== null
    if (isBrowser && mode === 'disabled') {
      throw new Error(
        'SECURITY ERROR: Cannot disable endpoint security checks in browser environment. ' +
        'Use endpointSecurity: "warn" for development or use a proxy.'
      )
    }

    if (baseUrl === null || baseUrl === undefined) {
      // Default endpoint.
      return onDangerousEndpoint('No explicit endpoint configured')
    }

    if (hostname === null) {
      // Relative URL, treated as safe.
      return
    }

    for (const endpoint of this.DANGEROUS_ENDPOINTS) {
      if (hostname === endpoint) {
        const message = `Detected official API endpoint: ${endpoint}`
        return onDangerousEndpoint(message)  // Found a match, no need to check other endpoints
      }
    }

    console.log(`Safe endpoint: ${hostname}`)
  }

  private async initialize(state: InterviewStateType) {
    console.log(`Initialize> ${this.interview._name}`)
    // Populate the state with the real interview object
    return { interview: this.interview }
  }

  private async think(state: InterviewStateType) {
    console.log(`Think> ${this.getStateInterview(state)._name}`)
    
    let newSystemMessage: BaseMessage | null = null
    
    // Add system message if this is the start
    const priorSystemMessages = (state.messages || []).filter((msg: BaseMessage) => msg instanceof SystemMessage)
    if (priorSystemMessages.length === 0) {
      console.log(`Start conversation in thread: ${this.config.configurable.thread_id}`)
      const systemPrompt = this.mkSystemPrompt(state)
      newSystemMessage = new SystemMessage(systemPrompt)
    }

    // Determine which LLM to use - matching Python logic
    const latestMessage = state.messages && state.messages.length > 0
                             ?  state.messages[state.messages.length - 1]
                             : null;
    
    let llm;
    if (latestMessage instanceof SystemMessage) {
      // No tools right after system message
      llm = this.llm
    } else if (latestMessage instanceof ToolMessage && latestMessage.content === 'Success') {
      // No tools right after a successful tool call.
      llm = this.llm
    } else {
      const updateTool = this.llmUpdateTool(state)
      llm = this.llm.bindTools([updateTool])
    }
    
    // Build messages for LLM
    const newSystemMessages = newSystemMessage ? [newSystemMessage] : []
    const allMessages = [...newSystemMessages, ...(state.messages || [])]
    const response = await llm.invoke(allMessages)
    
    // Return net-new messages
    const newMessages = [...newSystemMessages, response]
    return { messages: newMessages }
  }

  private llmUpdateTool(state: InterviewStateType) {
    // Return an llm-bindable tool with the correct definition, schema, etc.

    // Build updater schema for each field.
    // TODO: This could omit fields already set as an optimization.
    const argsSchema: Record<string, any> = {}

    const interviewFieldNames = Object.keys(this.interview._chatfield.fields)
    for (const fieldName of interviewFieldNames) {
      const fieldMetadata = this.interview._chatfield.fields[fieldName];
      const isConclude = fieldMetadata?.specs?.conclude;
      if (isConclude) {
        console.log(`Skip conclude field ${fieldName} in update tool`);
        continue;
      }

      const fieldSchema = this.buildFieldSchema(fieldName, fieldMetadata)
      argsSchema[fieldName] = fieldSchema.nullable().optional()  // Optional for update
    }

    const interview = this.getStateInterview(state);
    const toolName = `update_${interview._id()}`;
    const toolDesc = `Record valid information shared by the ${interview._bob_role_name} about the ${interview._name}`;

    // I think the wrapper function can no-op because the Tool node will do the real work.
    const wrapperFunc = async (input: any, config:any) => {
      console.log(`Wrapper func called with input and config`, input, config);
      throw new Error(`Wrapper function should not be called. Did Langchain call this automatically?`);
    }

    const schema = z.object(argsSchema); // .describe(toolDesc);
    const langchainTool = {name:toolName, description:toolDesc, schema:schema};
    return langchainTool;
  }

  private llmConcludeTool(state: InterviewStateType) {
    // Return an llm-bindable tool with the correct definition, schema, etc.

    // Build a schema for each field.
    const argsSchema: Record<string, any> = {}

    const interviewFieldNames = Object.keys(this.interview._chatfield.fields)
    for (const fieldName of interviewFieldNames) {
      const fieldMetadata = this.interview._chatfield.fields[fieldName];
      const isConclude = fieldMetadata?.specs?.conclude;
      if (! isConclude) {
        console.log(`Skip non-conclude field in conclude args: ${fieldName}`);
        continue;
      }

      const fieldSchema = this.buildFieldSchema(fieldName, fieldMetadata);

      // Conclude fields are non-nullable, non-optional.
      argsSchema[fieldName] = fieldSchema; // .nullable().optional()
    }

    const interview = this.getStateInterview(state);
    const toolName = `conclude_${interview._id()}`;
    const toolDesc = (
      `Record key required information` +
      ` about the ${interview._name}` +
      ` by summarizing, synthesizing, or recalling` +
      ` the conversation so far with the ${interview._bob_role_name}`
    );

    const schema = z.object(argsSchema); // .describe(toolDesc);
    const langchainTool = {name:toolName, description:toolDesc, schema:schema};
    return langchainTool;
  }

  // Node
  private async tools(state: InterviewStateType) {
    console.log(`Tools> ${this.getStateInterview(state)._name}`);
    const outputMessages: ToolMessage[] = [];

    // First dump the interview state before anything happens, in order to detect changes later.
    const interview = this.getStateInterview(state);
    const preData = interview.model_dump();

    const { messages } = state;
    const lastMessage = messages[messages.length - 1] as AIMessage;
    const toolCallInvocations = lastMessage.tool_calls!;

    for (const toolCallInvocation of toolCallInvocations) {
      const kwargs = toolCallInvocation.args!;
      const toolCallId = toolCallInvocation.id!;
      const toolCallName = toolCallInvocation.name!;

      const toolMessage = await this.runTool(interview, toolCallId, toolCallName, kwargs);
      outputMessages.push(toolMessage);
    }

    const postData = interview.model_dump()
    
    const stateUpdate:any = {};
    stateUpdate.messages = outputMessages;
    
    // Check if anything changed.
    if (JSON.stringify(preData) !== JSON.stringify(postData)) {
      stateUpdate.interview = interview
    }

    return stateUpdate;
  }

  private async listen(state: InterviewStateType, config:RunnableConfig) {
    const interview = this.getStateInterview(state)
    console.log(`Listen> ${interview._name}`)
    // console.log(`Config:`, config)
    
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
    const update = interrupt(feedback, config)
    
    console.log(`Interrupt result: ${JSON.stringify(update)}`)
    const userInput = (update as any).user_input
    const userMsg = new HumanMessage(userInput)
    
    return { messages: [userMsg] }
  }

  // Helper to get state interview safely - matching Python's _get_state_interview
  private getStateInterview(state: InterviewStateType): Interview {
    if (! state.interview) {
      throw new Error(`Expected state["interview"] to be an Interview instance, got falsy`)
    }

    let interview : Interview = state.interview;

    if (! (interview instanceof Interview)) {
      // I did not think this would be possible. But we can rebuild a proper Interview object
      // from the ._chatfield property.
      // console.log(`State interview is a plain object - rebuilding Interview instance from _chatfield`)
      const cf = (interview as any)._chatfield;
      interview = new Interview(cf.type, cf.desc, cf.roles, cf.fields);
    }

    if (interview.__proxiedInterview) {
      // console.log(`Good proxy for interview from state`);
    } else {
      interview = wrapInterviewWithProxy(interview)
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

  private async runTool(interview: Interview, toolCallId: string, toolCallName:string, kwargs: Record<string, any>): Promise<ToolMessage> {
    console.log(`Run tool: ${toolCallId}> ${JSON.stringify(kwargs)}`)
    // TODO: This should really decide which tool to run. Currently it hard-codes processUpdateTool.
    
    let toolError: any = null;
    try {
      await this.processUpdateTool(interview, kwargs);
    } catch (error: any) {
      toolError = error;
    }
    
    let content: string = ( toolError )
      ? `Error: ${toolError.message}\n\n${toolError.stack || ''}`
      : `Success`;

    const toolMessage = new ToolMessage({
      content: content,

      name: toolCallName,
      tool_call_id: toolCallId,
      additional_kwargs: { error: toolError },
    });

    return toolMessage;
  }

  private async teardown(state: InterviewStateType) {
    const interview = this.getStateInterview(state)
    console.log(`Teardown> ${interview._name}`)
    
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

  /**
   * Generate structured field data for templates - matching Python's mk_fields_data
   */
  private makeFieldsData(interview: Interview, mode: 'normal' | 'conclude' = 'normal', counters?: { hint: number; must: number; reject: number }, fieldNames?: string[]): any[] {
    if (mode !== 'normal' && mode !== 'conclude') {
      throw new Error(`Bad mode: '${mode}'; must be "normal" or "conclude"`)
    }

    const fields: any[] = []  // Note: this should always be in source-code order

    const fieldKeys = fieldNames || Object.keys(interview._chatfield.fields)
    for (const fieldName of fieldKeys.reverse()) {  // Reverse to maintain source order
      const chatfield = interview._chatfield.fields[fieldName]
      if (!chatfield) continue

      // Skip fields based on mode
      if (mode === 'normal' && chatfield.specs?.conclude) {
        continue
      }

      if (mode === 'conclude' && !chatfield.specs?.conclude) {
        continue
      }

      // Count validation rules if counters provided
      if (counters) {
        for (const specName of ['hint', 'must', 'reject'] as const) {
          const predicates = chatfield.specs?.[specName]
          if (predicates && Array.isArray(predicates)) {
            counters[specName] += predicates.length
          }
        }
      }

      // Prepare casts data (matching Python implementation)
      const casts = Object.entries(chatfield.casts || {}).map(([name, castData]: [string, any]) => ({
        name,
        prompt: castData.prompt || ''
      }))

      fields.push({
        name: fieldName,
        desc: chatfield.desc || '',
        casts: casts,
        specs: chatfield.specs || {}
      })
    }

    return fields
  }

  private makeFieldsPrompt(interview: Interview, mode: 'normal' | 'conclude' = 'normal', counters?: { hint: number; must: number; reject: number }): string[] {
    const fields: string[] = []
    const theBob = interview._bob_role_name
    
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
            // Count validation rules if counters provided
            if (counters && rules.length > 0) {
              if (specType === 'hint') {
                counters.hint += rules.length
              } else if (specType === 'must') {
                counters.must += rules.length
              } else if (specType === 'reject') {
                counters.reject += rules.length
              }
            }

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

    return fields
  }

  mkSystemPrompt(state: InterviewStateType): string {
    const interview = this.getStateInterview(state) || this.interview

    // Count validation rules - will be updated by makeFieldsData
    const counters = { hint: 0, must: 0, reject: 0 }
    const fieldsData = this.makeFieldsData(interview, 'normal', counters)

    // Prepare validation labels (matching Python logic)
    let labels = ''
    const hasValidation = counters.must > 0 || counters.reject > 0

    if (hasValidation) {
      if (counters.must > 0 && counters.reject === 0) {
        // Must only
        labels = '"Must"'
      } else if (counters.must === 0 && counters.reject > 0) {
        // Reject only
        labels = '"Reject"'
      } else if (counters.must > 0 && counters.reject > 0) {
        // Both must and reject
        labels = '"Must" and "Reject"'
      }
    }

    // Prepare context for template - matching Python exactly
    const context = {
      form: interview,  // Pass the entire interview object as 'form'
      labels: labels,   // Single labels string, not separate and/or versions
      counters: counters,  // Pass counters object
      fields: fieldsData,  // Structured field data
    }

    // Render template
    return this.templateEngine.render('system-prompt', context)
  }

  /**
   * Process tool input and update interview state - matching Python's implementation
   */
  async processUpdateTool(interview: Interview, kwargs: Record<string, any>) {
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
   * Process one conversation turn.
   *
   * The conversation will continue indefinitely until the application decides
   * to stop. Check interview._done to see if all fields are collected, then
   * call .end() when you want to terminate the conversation and run cleanup.
   *
   * @param userInput - The user's input message (or null/undefined to start/continue)
   * @returns The content of the latest AI message as a string
   */
  async go(userInput?: string | null): Promise<string> {
     // console.log('Go: User input:', userInput)
    
    const currentState = await this.graph.getState(this.config)
    
    let graphInput: any
    if (currentState.values && currentState.values.messages && currentState.values.messages.length > 0) {
       // console.log('Continue conversation:', this.config.configurable.thread_id)
      graphInput = new Command({update:{}, resume:{user_input: userInput}})
    } else {
       // console.log('New conversation:', this.config.configurable.thread_id)
      const threadId = this.config.configurable.thread_id
      const traceUrl = `https://smith.langchain.com/o/92e94533-dd45-4b1d-bc4f-4fd9476bb1e4/projects/p/1991a1b2-6dad-4d39-8a19-bbc3be33a8b6/t/${threadId}`
      console.log(`LangSmith trace: ${traceUrl}`)
      
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
      throw new Error('ERROR: No interrupts received - this should not happen as the graph should always route to listen')
    }

    if (interrupts.length > 1) {
      throw new Error(`Multiple interrupts received: ${interrupts}`)
    }

    return interrupts[0]!
  }

  /**
   * Explicitly end the conversation and run teardown cleanup.
   *
   * This jumps directly to the teardown node to perform any cleanup
   * operations before ending the conversation. Call this method when
   * you want to gracefully terminate the interview and run cleanup logic.
   *
   * The conversation will not automatically end when all fields are collected.
   * Applications must decide when to call this method.
   */
  async end(): Promise<void> {
    console.log('End: Jumping to teardown')
    const graphInput = new Command({ goto: 'teardown' })

    const stream = await this.graph.stream(graphInput, this.config)
    for await (const event of stream) {
      // Just execute teardown, no output needed
    }
  }

  // TODO: digest() method to re-run digest.
  // I think it may need to reset the state hasDigestedConfidentials/hasDigestedConcludes flags

  // Node: Handle confidential fields
  private async digest_confidentials(state: InterviewStateType): Promise<Partial<InterviewStateType>> {
    const interview = this.getStateInterview(state);
    console.log(`Digest Confidentials> ${interview._name}`);
    const fieldsPrompt: string[] = []
    const fieldDefinitions: Record<string, z.ZodTypeAny> = {}
    
    for (const [fieldName, chatfield] of Object.entries(interview._chatfield.fields)) {
      if (chatfield.specs.conclude) {
        // console.log(`Skip conclude field in confidential digest: ${fieldName}`);
        continue
      }
      
      if (chatfield.specs.confidential && !chatfield.value) {
        // This confidential field must be marked "N/A"
        fieldsPrompt.push(`- ${fieldName}: ${chatfield.desc}`)
        const fieldDefinition = this.mkFieldDefinition(interview, fieldName, chatfield)
        fieldDefinitions[fieldName] = fieldDefinition
      } else {
        // Force the LLM to pass null for values we don't need
        // Actually, just do not mention it.
        // fieldDefinitions[fieldName] = z.null().describe('Must be null because the field is already recorded')
      }
    }

    if (fieldsPrompt.length === 0) {
      // No fields to digest.
      return { hasDigestedConfidentials: true }
    }

    const fieldsPromptStr = fieldsPrompt.join('\n')
    
    // Build a special llm object bound to a tool which explicitly requires the proper arguments
    const toolName = `updateConfidential_${interview._id()}`
    const toolDesc = (
      `Record those confidential fields about the ${interview._name} ` +
      `from the ${interview._bob_role_name} ` +
      `which have no relevant information so far.`
    )
    
    const confidentialTool = z.object(fieldDefinitions).describe(toolDesc)
    
    // Prepare context for template
    const context = {
      interview_name: interview._name,
      alice_role_name: interview._alice_role_name,
      bob_role_name: interview._bob_role_name,
      fields_prompt: fieldsPromptStr
    }

    // Render template
    const promptContent = this.templateEngine.render('digest-confidential', context)
    const sysMsg = new SystemMessage(promptContent)

    const llm = this.llm.bindTools([{
      name: toolName,
      description: toolDesc,
      schema: confidentialTool,
    }]);
    
    const allMessages = [...state.messages, sysMsg];
    const llmResponseMessage = await llm.invoke(allMessages);
    
    // LangGraph wants only net-new messages. Its reducer will merge them.
    const newMessages = [sysMsg, llmResponseMessage]
    return { messages: newMessages, hasDigestedConfidentials: true }
  }

  private async digest_concludes(state: InterviewStateType): Promise<Partial<InterviewStateType>> {
    const interview = this.getStateInterview(state);
    console.log(`Digest Concludes> ${interview._name}`);

    const fields = this.makeFieldsPrompt(interview, 'conclude')
    if (fields.length === 0) {
      // No fields to digest.
      return { hasDigestedConcludes: true }
    }

    // Prepare context for template
    const fieldsPrompt = fields.join('\n\n')
    const context = {
      interview_name: interview._name,
      fields_prompt: fieldsPrompt
    }

    // Render template
    const promptContent = this.templateEngine.render('digest-conclude', context)
    const sysMsg = new SystemMessage(promptContent)

    // Define the tool for the LLM to call.
    const concludeTool = this.llmConcludeTool(state);
    const llm = this.llm.bindTools([concludeTool]);
    const allMessages = [...state.messages, sysMsg]
    const llmResponseMessage = await llm.invoke(allMessages)
    
    // LangGraph wants only net-new messages. Its reducer will merge them.
    const newMessages = [sysMsg, llmResponseMessage]
    return { messages: newMessages, hasDigestedConcludes: true }
  }
  
  // Build field schema for a single field - matching Python's approach
  private buildFieldSchema(fieldName: string, fieldMetadata: any): z.ZodTypeAny {
    const castsDefinitions: Record<string, z.ZodTypeAny> = {}
    
    // Always include the base value field
    castsDefinitions.value = z.string().describe(
      `The most typical valid representation of a ${this.interview._name} ${fieldName}`
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
          schema = z.set(z.any()).describe(castPrompt)
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
          throw new Error(`Bad type for cast "${castName}" as ${castType}: must be one of int, float, str, bool, list, set, dict, choice`)
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
      value: z.string().describe(`The most typical valid representation of a ${interview._name} ${fieldName}`),
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
        const schemaFn = okPrimitiveTypes[castType];
        if (!schemaFn) {
          throw new Error(`Bad type for cast ${castName}: ${castType}; must be one of ${Object.keys(okPrimitiveTypes).join(', ')}`);
        }
        castsDefinitions[castName] = schemaFn(castPrompt)
      }
    }
    
    return castsDefinitions
  }

  // Routing methods - matching Python's route_from_think
  private routeFromThink(state: InterviewStateType): string {
    console.log(`Route from think: ${this.getStateInterview(state)._name}`)

    // Use toolsCondition to check for tool calls
    const result = toolsCondition(state as any)
    if (result === 'tools') {
      return 'tools'
    }

    const interview = this.getStateInterview(state)

    // Auto-digest only the first time _enough becomes true
    // if (interview._enough) {
    //   if (!state.hasDigestedConfidentials) {
    //     console.log(`Route: think -> digest_confidentials (first time _enough is true)`)
    //     return 'digest_confidentials'
    //   }
    //   if (!state.hasDigestedConcludes) {
    //     console.log(`Route: think -> digest_concludes (first time _enough is true)`)
    //     return 'digest_concludes'
    //   }
    // }

    return 'listen'
  }

  private routeFromTools(state: InterviewStateType): string {
    const interview = this.getStateInterview(state)
    console.log(`Route from tools: ${interview._name}`)

    // Auto-digest only the first time _enough becomes true
    if (interview._enough) {
      if (!state.hasDigestedConfidentials) {
        console.log(`Route: think -> digest_confidentials (first time _enough is true)`)
        return 'digest_confidentials'
      }
      if (!state.hasDigestedConcludes) {
        console.log(`Route: think -> digest_concludes (first time _enough is true)`)
        return 'digest_concludes'
      }
    }

    return 'think'
  }

  private routeFromDigest(state: InterviewStateType): string {
    const interview = this.getStateInterview(state)
    console.log(`Route from digest_data: ${interview._name}`)

    // Use toolsCondition to check for tool calls
    const result = toolsCondition(state as any)
    if (result === 'tools') {
      console.log(`Route: digest_data -> tools`)
      return 'tools'
    }

    return 'think'
  }

  static debugPrompt(prompt: string, useColor: boolean = true): string {
    /**
     * Make a prompt string more readable for debugging by visualizing whitespace
     * and detecting template interpolation bugs.
     *
     * - Template variables like {var}, {{var}}, {{{var}}} are highlighted as ERRORS
     * - Newlines are shown with colored ↵ symbol
     * - Trailing spaces are highlighted with colored background
     * - Multiple consecutive spaces are shown with colored ␣ symbol
     * - Tabs vs spaces in indentation are visualized
     * - Invisible Unicode characters are detected
     *
     * @param prompt - The prompt string to make visible
     * @param useColor - Whether to use ANSI color codes (default: true)
     * @returns A version of the prompt with visible whitespace and colored highlights
     */

    // ANSI color codes for dark terminal backgrounds
    let RED_BG = ''
    let YELLOW_BG = ''
    let CYAN = ''
    let MAGENTA = ''
    let BLUE = ''
    let ORANGE = ''
    let GRAY = ''
    let RESET = ''
    let BOLD = ''

    if (useColor) {
      // Bright colors for visibility on dark backgrounds
      RED_BG = '\x1b[48;5;196m'      // Bright red background for errors
      YELLOW_BG = '\x1b[48;5;226m'   // Yellow background for warnings
      CYAN = '\x1b[38;5;51m'          // Bright cyan for newlines
      MAGENTA = '\x1b[38;5;201m'      // Bright magenta for multiple spaces
      BLUE = '\x1b[38;5;39m'          // Bright blue for tabs
      ORANGE = '\x1b[38;5;208m'       // Orange for special chars
      GRAY = '\x1b[38;5;242m'         // Gray for space indents
      RESET = '\x1b[0m'
      BOLD = '\x1b[1m'
    }

    const lines = prompt.split('\n')
    const result: string[] = []

    for (const line of lines) {
      let processed = line

      // Detect template interpolation bugs - these should NOT exist in final prompts
      // Look for {var}, {{var}}, {{{var}}} etc.
      const templatePattern = /(\{+[^{}]+\}+)/g
      if (templatePattern.test(processed)) {
        processed = processed.replace(
          /(\{+[^{}]+\}+)/g,
          (match) => `${RED_BG}${BOLD}⚠${match}⚠${RESET}`
        )
      }

      // Detect invisible Unicode characters
      const invisibleChars: Record<string, string> = {
        '\u200b': `${ORANGE}[ZWSP]${RESET}`,      // Zero-width space
        '\u00a0': `${ORANGE}[NBSP]${RESET}`,      // Non-breaking space
        '\u200c': `${ORANGE}[ZWNJ]${RESET}`,      // Zero-width non-joiner
        '\u200d': `${ORANGE}[ZWJ]${RESET}`,       // Zero-width joiner
        '\ufeff': `${ORANGE}[BOM]${RESET}`,       // Byte order mark
        '\u2060': `${ORANGE}[WJ]${RESET}`,        // Word joiner
      }

      for (const [char, replacement] of Object.entries(invisibleChars)) {
        if (processed.includes(char)) {
          processed = processed.replace(new RegExp(char, 'g'), replacement)
        }
      }

      // Handle indentation (before other processing)
      const indentMatch = processed.match(/^([ \t]+)/)
      if (indentMatch) {
        const indent = indentMatch[1]
        const rest = processed.slice(indent ? indent.length : 0)

        // Check for mixed indentation (problematic!)
        if (indent && indent.includes(' ') && indent.includes('\t')) {
          // Mixed spaces and tabs - highlight as error
          let indentVisual = ''
          for (const char of indent) {
            if (char === ' ') {
              indentVisual += `${RED_BG}·${RESET}`
            } else {  // tab
              indentVisual += `${RED_BG}→${RESET}`
            }
          }
          processed = indentVisual + rest
        } else {
          // Pure spaces or pure tabs
          if (indent && indent[0] === ' ') {
            // Spaces - use subtle gray markers
            const indentVisual = `${GRAY}${'·'.repeat(indent!.length)}${RESET}`
            processed = indentVisual + rest
          } else {
            // Tabs - use blue arrows
            const indentVisual = `${BLUE}${'→'.repeat(indent!.length)}${RESET}`
            processed = indentVisual + rest
          }
        }
      }

      // Handle trailing spaces - but check the raw line, not the processed one
      if (line && line.endsWith(' ')) {
        // Find where the trailing spaces start in the processed string
        const rawStripped = line.trimEnd()
        const numTrailing = line.length - rawStripped.length

        // If we've already processed indentation, we need to be careful
        if (processed.includes(RESET)) {
          // Find the actual content after all the formatting
          const parts = processed.split(RESET)
          const lastPart = parts[parts.length - 1]
          if (lastPart && lastPart.endsWith(' '.repeat(numTrailing))) {
            parts[parts.length - 1] = lastPart.slice(0, -numTrailing) + `${YELLOW_BG}${'·'.repeat(numTrailing)}${RESET}`
            processed = parts.join(RESET)
          }
        } else if (processed.endsWith(' ')) {
          const stripped = processed.trimEnd()
          const actualTrailing = processed.length - stripped.length
          processed = stripped + `${YELLOW_BG}${'·'.repeat(actualTrailing)}${RESET}`
        }
      }

      // Replace multiple consecutive spaces (not in indentation)
      // Skip if we already processed indentation
      if (!indentMatch) {
        processed = processed.replace(
          /  +/g,
          (match) => `${MAGENTA}${'␣'.repeat(match.length)}${RESET}`
        )
      } else {
        // For lines with indentation, only process spaces after the indent
        const parts = processed.split(RESET, 2)
        if (parts.length === 2) {
          const indentPart = parts[0]
          let restPart = parts ? parts[1] : ''
          restPart = restPart!.replace(
            /  +/g,
            (match) => `${MAGENTA}${'␣'.repeat(match.length)}${RESET}`
          )
          processed = `${indentPart}${RESET}${restPart}`
        }
      }

      result.push(processed)
    }

    // Join with colored newline indicator
    return result.join(`${CYAN}↵${RESET}\n`)
  }
}