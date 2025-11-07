"""LangGraph-based evaluator for Chatfield conversations."""

import re
import uuid
import logging
import traceback
import warnings
from urllib.parse import urlparse

logger = logging.getLogger(__name__)

from pydantic import BaseModel, Field, conset, create_model
from deepdiff import DeepDiff

from typing import Annotated, Any, Dict, Optional, TypedDict, List, Literal, Set
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt, Interrupt
from langgraph.prebuilt import tools_condition
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages

from .interview import Interview
from .template_engine import TemplateEngine
from .merge import merge_interviews, merge_has_digested

# Endpoint security mode type
EndpointSecurityMode = Literal['strict', 'warn', 'disabled']

def encode_field_name(field_name: str) -> str:
    """
    Encode field name to valid Python identifier using URL-encoding-style.

    If the field name is already a valid identifier and not a Python keyword,
    it is returned as-is. Otherwise:
    - Prefixes with 'field_' to handle keywords and leading digits
    - Encodes special characters as _PCTXXXX_ where XXXX is hex code

    This is transparent (you can still read the field name) and guarantees
    perfect round-trip encoding/decoding with no collisions. Supports full unicode.

    Args:
        field_name: Original field name (any unicode characters)

    Returns:
        A valid Python identifier that can be used as a Pydantic field name

    Examples:
        >>> encode_field_name("name")
        'name'
        >>> encode_field_name("email_address")
        'email_address'
        >>> encode_field_name("topmostSubform[0].Page1[0].f1_01[0]")
        'field_topmostSubform_PCT5B_0_PCT5D__PCT2E_Page1_PCT5B_0_PCT5D__PCT2E_f1_01_PCT5B_0_PCT5D_'
        >>> encode_field_name("user.name")
        'field_user_PCT2E_name'
        >>> encode_field_name("class")
        'field_class'
        >>> encode_field_name("field[0]")
        'field_field_PCT5B_0_PCT5D_'
        >>> encode_field_name("rating😊")
        'field_rating_PCT1F60A_'
        >>> encode_field_name("café")
        'field_caf_PCTE9_'
    """
    import keyword

    # Check if field name is already valid identifier and not a keyword
    if field_name.isidentifier() and not keyword.iskeyword(field_name):
        # Check if it only contains ASCII alphanumeric and underscore
        if all(char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_' for char in field_name):
            # Avoid collision: if field name starts with "field_", we must encode it
            if not field_name.startswith('field_'):
                return field_name

    result = []
    for char in field_name:
        # Only allow ASCII alphanumeric and underscore (not unicode letters)
        if char in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_':
            result.append(char)
        else:
            # Encode as _PCTXX_ where XX is hex (at least 2 digits for readability)
            char_code = ord(char)
            hex_code = f'{char_code:X}'
            # Pad to at least 2 digits for consistency
            if len(hex_code) < 2:
                hex_code = '0' + hex_code
            result.append(f'_PCT{hex_code}_')

    # Prefix with 'field_' - handles keywords and leading digits
    return 'field_' + ''.join(result)

def decode_field_name(encoded_name: str) -> str:
    """
    Decode an encoded field name back to original.

    If the encoded name doesn't start with 'field_', it's assumed to be a simple
    identifier that wasn't encoded, so it's returned as-is.

    Supports variable-length hex codes for full unicode support.

    Args:
        encoded_name: Encoded field name (may or may not start with 'field_')

    Returns:
        Original field name

    Examples:
        >>> decode_field_name('name')
        'name'
        >>> decode_field_name('email_address')
        'email_address'
        >>> decode_field_name('field_user_PCT2E_name')
        'user.name'
        >>> decode_field_name('field_class')
        'class'
        >>> decode_field_name('field_field_PCT5B_0_PCT5D_')
        'field[0]'
        >>> decode_field_name('field_rating_PCT1F60A_')
        'rating😊'
        >>> decode_field_name('field_caf_PCTE9_')
        'café'
    """
    # If it doesn't start with 'field_', it wasn't encoded
    if not encoded_name.startswith('field_'):
        return encoded_name

    encoded_name = encoded_name[6:]  # Remove 'field_' prefix

    # Replace _PCTXXXX_ with corresponding character (variable-length hex)
    def replace_hex(match):
        hex_code = match.group(1)
        return chr(int(hex_code, 16))

    # Match _PCT followed by one or more hex digits, then _
    decoded = re.sub(r'_PCT([0-9A-F]+)_', replace_hex, encoded_name)
    return decoded

class State(TypedDict):
    messages: Annotated[List[Any] , add_messages    ]
    interview: Annotated[Interview, merge_interviews]
    has_digested_confidentials: Annotated[bool, merge_has_digested]
    has_digested_concludes    : Annotated[bool, merge_has_digested]


class Interviewer:
    """
    Interviewer that manages conversation flow.
    """

    DANGEROUS_ENDPOINTS = [
        'api.openai.com',
        'api.anthropic.com',
    ]

    def __init__(
        self,
        interview: Interview,
        thread_id: Optional[str] = None,
        llm = None,
        llm_id = None,
        temperature = None,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        endpoint_security: Optional[EndpointSecurityMode] = None
    ):
        # Isomorphic:
        # TypeScript has options parameter, Python uses all kwargs.
        self.interview = interview
        self.template_engine = TemplateEngine()
        self.checkpointer = InMemorySaver()
        self.config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}

        # Initialize LLM
        if llm:
            self.llm = llm
        else:
            # Isomorphic:
            # TypeScript has logic to set up Browser environments.
            # Python no-ops.
            win = False
            if win:
                # Browser environment
                pass
            else:
                # Server environment
                # OPENAI_BASE_URL already works due to the underlying OpenAI client.
                pass

            llm_id = llm_id or 'openai:gpt-4o'
            temperature = temperature or 0.0
            if llm_id in ('openai:o3-mini', 'openai:o3'):
                temperature = None

            # Isomorphic:
            # Both languages use ChatOpenAI directly from their respective packages.
            # Both throw if the 'openai:' prefix is missing.
            if not llm_id.startswith('openai:'):
                raise ValueError(f'LLM ID must start with "openai:", got {llm_id!r}')
            else:
                llm_id = llm_id[len('openai:'):]  # Strip 'openai:' prefix

            llm_config = {
                'model': llm_id,
                'temperature': temperature,
                'base_url': base_url,
                'api_key': api_key,
            }
            self.llm = ChatOpenAI(**llm_config)

        # Isomorphic:
        # Both languages implement security modes.
        # Both languages default to "disabled" as servers.
        # But in a browser, the default is "strict".
        is_browser = False
        security_mode = endpoint_security or 'disabled'
        self._detect_dangerous_endpoint(self.llm, security_mode)
        self._setup_graph()

    def _setup_graph(self):
        """Build the LangGraph state machine - matches TypeScript's setupGraph()."""
        builder = StateGraph(State)

        builder.add_node('initialize', self.initialize)
        builder.add_node('think'     , self.think)
        builder.add_node('listen'    , self.listen)
        builder.add_node('tools'     , self.tools)
        builder.add_node('digest_confidentials', self.digest_confidentials)
        builder.add_node('digest_concludes', self.digest_concludes)
        builder.add_node('teardown'  , self.teardown)

        builder.add_edge             (START       , 'initialize')
        builder.add_edge             ('initialize', 'think')
        builder.add_conditional_edges('think'     , self.route_from_think)
        builder.add_edge             ('listen'    , 'think')
        builder.add_conditional_edges('tools'     , self.route_from_tools, ['think', 'digest_confidentials', 'digest_concludes'])
        builder.add_conditional_edges('digest_confidentials', self.route_from_digest, ['tools', 'think', 'digest_concludes'])
        builder.add_conditional_edges('digest_concludes'    , self.route_from_digest, ['tools', 'think'])
        builder.add_edge             ('teardown'  , END    )

        self.graph = builder.compile(checkpointer=self.checkpointer)

    def _detect_dangerous_endpoint(self, llm, mode: EndpointSecurityMode) -> None:
        """Check for dangerous API endpoints based on security mode.

        Args:
            llm: The LLM instance to check
            mode: Security mode ('strict', 'warn', or 'disabled')

        Raises:
            ValueError: If mode is 'strict' and a dangerous endpoint is detected
        """

        hostname = None
        base_url = llm.openai_api_base
        if base_url:
            parsed = urlparse(base_url)
            hostname = parsed.hostname

        def on_dangerous_endpoint(message: str):
            if mode == 'disabled':
                logger.debug(f'Endpoint: {message}')
            elif mode == 'warn':
                warnings.warn(
                    f'WARNING: {message}. Your API key may be exposed to end users.',
                    UserWarning,
                    stacklevel=2)
            elif mode == 'strict':
                raise ValueError(
                    f'SECURITY ERROR: {message}. '
                    f'This may expose your API key to end users. Use a backend proxy instead.'
                )
        
        # Isomorphic:
        # Browser-specific logic (TypeScript only)
        # Enforce: Cannot disable security in browser

        if base_url is None:
            # Default endpoint.
            return on_dangerous_endpoint(f'No explicit endpoint configured')

        if hostname is None:
            # Relative URL, treated as safe.
            return

        for endpoint in self.DANGEROUS_ENDPOINTS:
            if hostname == endpoint:
                message = f'Detected official API endpoint: {endpoint}'
                return on_dangerous_endpoint(message) # Found a match, no need to check other endpoints

        logger.info(f'Safe endpoint: {hostname}')

    # This exists to fail faster in case of serialization bugs with the LangGraph checkpointer.
    # Hopefully it can go away.
    def _get_state_interview(self, state: State) -> Interview:
        interview = state.get('interview')
        if not isinstance(interview, Interview):
            raise ValueError(f'Expected state["interview"] to be an Interview instance, got {type(interview)}: {interview!r}')
        
        if not interview._chatfield['fields']:
            # No fields defined is okay only for a totally-null, uninitialized interview object.
            # This happens normally in early state, before the initialize node.
            # TODO: For now, instead of exhaustively checking for "not-initialized-ness", I will do some quick duck typing.
            if interview._chatfield['type'] is None and interview._chatfield['desc'] is None:
                # print(f'Interview is uninitialized, which is okay: {interview!r}')
                pass
            else:
                raise Exception(f'Expected state["interview"] to have fields, got empty: {interview!r}')
        return interview

    # Node
    def initialize(self, state:State):
        logger.debug(f'Initialize> {self._get_state_interview(state).__class__.__name__}')

        # Currently there is an empty/null Interview object in the state. Populate that with the real one.
        return {'interview': self.interview}
    
    def llm_update_tool(self, state: State):
        """Return an llm-bindable tool with the correct definition, schema, etc."""
        # Build updater schema for each field.
        # TODO: This could omit fields already set as an optimization.
        args_schema = {}
        
        interview = self._get_state_interview(state)
        interview_field_names = interview._fields()
        for field_name in interview_field_names:
            field_metadata = interview._chatfield['fields'][field_name]
            is_conclude = field_metadata['specs']['conclude']
            if is_conclude:
                # print(f'Skip conclude field {field_name} in update tool')
                continue
            
            field_definition = self.mk_field_definition(interview, field_name, field_metadata)

            # Encode field name to valid Python identifier
            encoded_name = encode_field_name(field_name)
            args_schema[encoded_name] = (Optional[field_definition], Field())

        tool_name = f'update_{interview._id()}'
        tool_desc = f'Record valid information shared by the {interview._bob_role_name} about the {interview._name}'
        UpdateToolArgs = create_model('UpdateToolArgs', **args_schema)

        # This is not identical to the TypeScript implementation.
        # TypeScript allows binding to the object with {name, description, args_schema},
        # but that is not working in Python. For now, use the @tool decorator for a callable
        # which never actually runs.
        
        # return {
        #     'name': tool_name,
        #     'description': tool_desc,
        #     'args_schema': UpdateToolArgs,
        # }

        @tool(tool_name, description=tool_desc, args_schema=UpdateToolArgs)
        def wrapper(**kwargs):
            raise Exception(f'This should not actually run: {tool_name} {kwargs!r}')
        return wrapper
    
    def llm_conclude_tool(self, state: State):
        """Return an llm-bindable tool with the correct definition, schema, etc."""
        # Build a schema for each field.
        args_schema = {}
        
        interview = self._get_state_interview(state)
        interview_field_names = interview._fields()
        for field_name in interview_field_names:
            field_metadata = interview._chatfield['fields'][field_name]
            is_conclude = field_metadata['specs']['conclude']
            if not is_conclude:
                # print(f'Skip non-conclude field in conclude args: {field_name}')
                continue
            
            field_definition = self.mk_field_definition(interview, field_name, field_metadata)

            # Encode field name to valid Python identifier
            encoded_name = encode_field_name(field_name)

            # Conclude fields are non-nullable, non-optional
            args_schema[encoded_name] = (field_definition, Field())

        tool_name = f'conclude_{interview._id()}'
        tool_desc = (
            f'Record key required information'
            f' about the {interview._name}'
            f' by summarizing, synthesizing, or recalling'
            f' the conversation so far with the {interview._bob_role_name}'
        )
        
        ConcludeToolArgs = create_model('ConcludeToolArgs', **args_schema)

        # This is not identical to the TypeScript implementation.
        # TypeScript allows binding to the object with {name, description, args_schema},
        # but that is not working in Python. For now, use the @tool decorator for a callable
        # which never actually runs.
        
        @tool(tool_name, description=tool_desc, args_schema=ConcludeToolArgs)
        def wrapper(**kwargs):
            raise Exception(f'This should not actually run: {tool_name} {kwargs!r}')
        return wrapper
    
    # Node
    def tools(self, state: State):
        """Process tool calls directly without using ToolNode."""
        interview = self._get_state_interview(state)
        logger.debug(f'Tools> {interview._name}')

        output_messages = []
        
        # First dump the interview state before anything happens, in order to detect changes later.
        pre_data = interview.model_dump()
        
        messages = state['messages']
        last_message = messages[-1]
        if not isinstance(last_message, AIMessage) or not last_message.tool_calls:
            raise ValueError(f'Expected AIMessage with tool_calls, got {type(last_message)}')
        
        tool_call_invocations = last_message.tool_calls
        
        for tool_call_invocation in tool_call_invocations:
            kwargs = tool_call_invocation['args']
            tool_call_id = tool_call_invocation['id'] or ''
            tool_call_name = tool_call_invocation['name']
            
            tool_message = self.run_tool(interview, tool_call_id, tool_call_name, kwargs)
            output_messages.append(tool_message)
        
        post_data = interview.model_dump()
        
        state_update = {}
        state_update['messages'] = output_messages
        
        # Check if anything changed.
        data_diff = DeepDiff(pre_data, post_data, ignore_order=True)
        if data_diff:
            state_update['interview'] = interview
        
        return state_update
    
    def run_tool(self, interview: Interview, tool_call_id: str, tool_call_name: str, kwargs: Dict[str, Any]) -> ToolMessage:
        """Run a tool and return a ToolMessage."""
        logger.debug(f'Run tool {tool_call_name}: {tool_call_id} {kwargs!r}')
        # TODO: This should really decide which tool to run. Currently it hard-codes process_update_tool.
        
        tool_error = None
        try:
            self.process_update_tool(interview, **kwargs)
        except Exception as er:
            tool_error = er
        
        content = (
            f'Error: {tool_error!r}\n\n' + ''.join(traceback.format_exception(tool_error))
            if tool_error
            else 'Success'
        )
        
        tool_message = ToolMessage(
            content=content,
            name=tool_call_name,
            tool_call_id=tool_call_id,
            additional_kwargs={'error': tool_error} if tool_error else {}
        )
        
        return tool_message

    # Node
    def digest_data(self, state: State):
        interview = self._get_state_interview(state)
        logger.debug(f'Digest Data> {interview._name}')

        # First digest undefined confidential fields. Then digest the conclude fields.
        for field_name, chatfield in interview._chatfield['fields'].items():
            if not chatfield['specs']['conclude']:
                if chatfield['specs']['confidential']:
                    if not chatfield['value']:
                        # Digest all confidentials since an undefined one was found.
                        return self.digest_confidential(state)
        return self.digest_conclude(state)
    
    def digest_confidentials(self, state: State):
        interview = self._get_state_interview(state)
        logger.debug(f'Digest Confidentials> {interview._name}')

        fields_prompt = []
        field_definitions = {}
        for field_name, chatfield in interview._chatfield['fields'].items():
            if chatfield['specs']['conclude']:
                # print(f'Skip conclude field in confidential digest: {field_name}')
                continue

            if chatfield['specs']['confidential'] and not chatfield['value']:
                # This confidential field must be marked "N/A".
                fields_prompt.append(f'- {field_name}: {chatfield["desc"]}')
                field_definition = self.mk_field_definition(interview, field_name, chatfield)

                # Encode field name to valid Python identifier
                encoded_name = encode_field_name(field_name)
                field_definitions[encoded_name] = (field_definition, Field())
            else:
                # Actually, just do not mention it.
                # field_definitions[field_name] = (Literal[None], Field(description='Must be null because the field is already recorded'))
                pass

        if not fields_prompt:
            # No fields to digest.
            return {'has_digested_confidentials': True}

        fields_prompt = '\n'.join(fields_prompt)

        # Build a special llm object bound to a tool which explicitly requires the proper arguments.
        tool_name = f'updateConfidential_{interview._id()}'
        tool_desc = (
            f'Record those confidential fields about the {interview._name}'
            f' from the {interview._bob_role_name}'
            f' which have no relevant information so far.'
        )

        ConfidentialToolArgs = create_model('ConfidentialToolArgs', **field_definitions)
        
        # This is not identical to the TypeScript implementation.
        # TypeScript allows binding to the object with {name, description, args_schema},
        # but that is not working in Python. For now, use the @tool decorator for a callable
        # which never actually runs.
        
        @tool(tool_name, description=tool_desc, args_schema=ConfidentialToolArgs)
        def wrapper(**kwargs):
            raise Exception(f'This should not actually run: {tool_name} {kwargs!r}')

        llm = self.llm.bind_tools([wrapper])

        # Prepare context for template
        context = {
            'interview_name': interview._name,
            'alice_role_name': interview._alice_role_name,
            'bob_role_name': interview._bob_role_name,
            'fields_prompt': fields_prompt
        }

        # Render template (note: existing digest-confidential template needs update)
        prompt_content = self.template_engine.render('digest-confidential', context)
        sys_msg = SystemMessage(content=prompt_content)

        all_messages = state['messages'] + [sys_msg]
        llm_response_message = llm.invoke(all_messages)
        # print(f'New LLM response message: {llm_response_message!r}')

        # LangGraph wants only net-new messages. Its reducer will merge them.
        new_messages = [sys_msg] + [llm_response_message]
        return {'messages':new_messages, 'has_digested_confidentials': True}
    
    def mk_field_definition(self, interview:Interview, field_name: str, chatfield: Dict[str, Any]):
        casts_definitions = self.mk_casts_definitions(chatfield)
        field_definition = create_model(
            field_name,
            __doc__= chatfield['desc'],
            value  = (str, Field(title=f'Natural Value', description=f'The most typical valid representation of a {interview._name} {field_name}. Use empty string "" if user wants to skip/leave blank, null if not yet discussed.')),
            **casts_definitions,
        )
        return field_definition
    
    def mk_casts_definitions(self, chatfield): # field_name:str, chatfield:Dict[str, Any]):
        casts_definitions = {}

        ok_primitive_types = {
            'int': int,
            'float': float,
            'str': str,
            'bool': bool,
            'list': List[Any],
            'set': set,
            'dict': Dict[str, Any],
            'choice': 'choice',
        }

        casts = chatfield['casts']
        for cast_name, cast_info in casts.items():
            cast_type = cast_info['type']
            cast_type = ok_primitive_types.get(cast_type)
            if not cast_type:
                raise ValueError(f'Cast {cast_name!r} bad type: {cast_info!r}; must be one of {ok_primitive_types.keys()}')

            cast_title = None # cast_info.get('title', f'{cast_name} value')
            cast_prompt = cast_info['prompt']

            if cast_type == 'choice':
                # TODO: Unclear if this name shortening helps:
                cast_short_name = re.sub(r'^choose_.*_', '', cast_name)
                cast_prompt = cast_prompt.format(name=cast_short_name)

                # First start with all the choices.
                choices = tuple(cast_info['choices'])
                min_results = 1
                max_results = 1

                if cast_info['null']:
                    min_results = 0

                cast_type = Literal[choices]  # type: ignore

                if cast_info['multi']:
                    # cast_type = Set[cast_type]
                    max_results = len(choices)
                    cast_type = conset(item_type=cast_type, min_length=min_results, max_length=max_results)

                if cast_info['null']:
                    cast_type = Optional[cast_type]

            cast_definition = (cast_type, Field(description=cast_prompt, title=cast_title))
            casts_definitions[cast_name] = cast_definition

        return casts_definitions

    def digest_concludes(self, state: State):
        interview = self._get_state_interview(state)
        logger.debug(f'Digest Concludes> {interview._name}')

        # Define the tool for the LLM to call.
        conclude_tool = self.llm_conclude_tool(state)
        llm = self.llm.bind_tools([conclude_tool])
        
        fields = self.mk_fields_prompt(interview, mode='conclude')
        if not fields:
            # No fields to digest.
            return {'has_digested_concludes': True}

        # Prepare context for template
        fields_prompt = '\n\n'.join(fields)
        context = {
            'interview_name': interview._name,
            'fields_prompt': fields_prompt
        }

        # Render template
        prompt_content = self.template_engine.render('digest-conclude', context)
        sys_msg = SystemMessage(content=prompt_content)

        all_messages = state['messages'] + [sys_msg]
        llm_response_message = llm.invoke(all_messages)
        # print(f'New LLM response message: {llm_response_message!r}')

        # LangGraph wants only net-new messages. Its reducer will merge them.
        new_messages = [sys_msg] + [llm_response_message]
        return {'messages':new_messages, 'has_digested_concludes': True}

    # Node
    def think(self, state: State):
        logger.debug(f'Think> {self._get_state_interview(state).__class__.__name__}')

        # Track any system messages that need to be added.
        new_system_message = None

        #
        # System Messages
        #

        prior_system_messages = [msg for msg in state['messages'] if isinstance(msg, SystemMessage)]
        if len(prior_system_messages) == 0:
            logger.info(f'Start conversation in thread: {self.config["configurable"]["thread_id"]}')
            system_prompt = self.mk_system_prompt(state)
            new_system_message = SystemMessage(content=system_prompt)

        #
        # LLM Tool Optimizations
        #

        # Determine which LLM to use.
        latest_message = state['messages'][-1] if state['messages'] else None
        
        if isinstance(latest_message, SystemMessage):
            # No tools right after system message
            llm = self.llm
        elif isinstance(latest_message, ToolMessage) and latest_message.content == 'Success':
            # No tools right after a successful tool call.
            llm = self.llm
        else:
            # Default to update tools
            update_tool = self.llm_update_tool(state)
            llm = self.llm.bind_tools([update_tool])

        #
        # Call the LLM
        #

        if new_system_message:
            if prior_system_messages:
                raise NotImplementedError(f'Cannot handle multiple system messages yet: {prior_system_messages!r}')

        # Although the reducer only wants net-new messages, the LLM wants the full conversation.
        new_system_messages = [new_system_message] if new_system_message else []
        all_messages = new_system_messages + state['messages']
        llm_response_message = llm.invoke(all_messages)
        # print(f'New LLM response message: {llm_response_message!r}')

        #
        # Return to LangGraph
        #
        
        # LangGraph wants only net-new messages. Its reducer will merge them.
        # TODO: I do not know if anything else needs to be done to place the system message before the others.
        new_messages = new_system_messages + [llm_response_message]
        new_messages.append(llm_response_message)
        return {'messages':new_messages}
    
    def process_update_tool(self, interview: Interview, **kwargs):
        """
        Move any LLM-provided field values into the interview state.
        """
        defined_args = [X for X in kwargs if kwargs[X] is not None]
        logger.debug(f'Tool input for {len(defined_args)} fields: {", ".join(defined_args)}')
        for encoded_name, llm_field_value in kwargs.items():
            if llm_field_value is None:
                continue

            # Decode the field name from the encoded identifier
            field_name = decode_field_name(encoded_name)

            # Handle both Pydantic models and plain dicts (for testing)
            if hasattr(llm_field_value, 'model_dump'):
                llm_values = llm_field_value.model_dump()
            else:
                llm_values = llm_field_value
            logger.debug(f'LLM found a valid field: {field_name!r} = {llm_values!r}')
            chatfield = interview._get_chat_field(field_name)
            if chatfield.get('value'):
                # print(f'{self.__class__.__name__}: Overwrite old field {field_name!r} value: {chatfield["value"]!r}')
                # TODO: This could do something sophisticated.
                pass

            all_values = {}
            for key, val in llm_values.items():
                key = re.sub(r'^choose_exactly_one_' , 'as_one_'  , key)
                key = re.sub(r'^choose_zero_or_one_' , 'as_maybe_', key)
                key = re.sub(r'^choose_one_or_more_' , 'as_multi_', key)
                key = re.sub(r'^choose_zero_or_more_', 'as_any_'  , key)
                all_values[key] = val
            chatfield['value'] = all_values

    def mk_system_prompt(self, state: State) -> str:
        interview = self._get_state_interview(state)

        # Count validation rules - will be updated by mk_fields_prompt/mk_fields_data
        counters = {'hint': 0, 'must': 0, 'reject': 0}
        fields_data = self.mk_fields_data(interview, counters=counters)

        # Prepare validation labels
        labels = None
        has_validation = counters['must'] > 0 or counters['reject'] > 0
        if has_validation:
            if counters['must'] > 0 and counters['reject'] == 0:
                # Must only
                labels = '"Must"'
            elif counters['must'] == 0 and counters['reject'] > 0:
                # Reject only
                labels = '"Reject"'
            elif counters['must'] > 0 and counters['reject'] > 0:
                # Both must and reject
                labels = '"Must" and "Reject"'

        # Prepare context for template
        context = {
            'form': interview,
            'labels': labels,
            'counters': counters,
            'fields': fields_data,
        }

        prompt = self.template_engine.render('system-prompt', context)
        return prompt

    def mk_fields_data(self, interview: Interview, mode='normal', field_names=None, counters=None) -> list:
        """Generate structured field data for templates."""
        if mode not in ('normal', 'conclude'):
            raise ValueError(f'Bad mode: {mode!r}; must be "normal" or "conclude"')

        fields = []  # Note, this should always be in source-code order.

        field_keys = field_names or interview._chatfield['fields'].keys()
        for field_name in field_keys:
            chatfield = interview._chatfield['fields'][field_name]

            if mode == 'normal' and chatfield['specs']['conclude']:
                continue

            if mode == 'conclude' and not chatfield['specs']['conclude']:
                continue

            # Count validation rules if counters provided
            if counters is not None:
                for spec_name in ('hint', 'must', 'reject'):
                    predicates = chatfield['specs'].get(spec_name, [])
                    if predicates and isinstance(predicates, list):
                        counters[spec_name] += len(predicates)

            casts = [ {'name':k, 'prompt':v["prompt"]} for k,v in chatfield['casts'].items() ]

            fields.append({
                'name': field_name,
                'desc': chatfield.get('desc', ''),
                'casts': casts,
                'specs': chatfield.get('specs', {})
            })

        return fields

    def mk_fields_prompt(self, interview: Interview, mode='normal', field_names=None, counters=None) -> list[str]:
        if mode not in ('normal', 'conclude'):
            raise ValueError(f'Bad mode: {mode!r}; must be "normal" or "conclude"')

        fields = [] # Note, this should always be in source-code order.

        field_keys = field_names or interview._chatfield['fields'].keys()
        for field_name in field_keys:
            chatfield = interview._chatfield['fields'][field_name]

            if mode == 'normal' and chatfield['specs']['conclude']:
                # print(f'Skip conclude field for normal prompt: {field_name!r}')
                continue
        
            if mode == 'conclude' and not chatfield['specs']['conclude']:
                # print(f'Skip normal field for conclude prompt: {field_name!r}')
                continue

            desc = chatfield.get('desc')
            field_label = f'{field_name}'
            if desc:
                field_label += f': {desc}'

            # TODO: I think confidential and conclude should be their own thing, not specs.
            specs = chatfield['specs']
            specs_prompts = []

            if specs['confidential']:
                specs_prompts.append(
                    f'    - **Confidential**: Do not inquire about this explicitly nor bring it up yourself. Continue your normal behavior.'
                    f' However, if the {interview._bob_role_name} ever volunteers or implies it, you must record this information.'
                )

            for spec_name, predicates in specs.items():
                if spec_name not in ('confidential', 'conclude'):
                    # Count validation rules if counters provided
                    if counters is not None and predicates:
                        if spec_name in ('hint', 'must', 'reject'):
                            counters[spec_name] += len(predicates)
                    
                    for predicate in predicates:
                        specs_prompts.append(f'    - {spec_name.capitalize()}: {predicate}')
            
            casts = chatfield.get('casts', {})
            casts_prompts = []
            for cast_name, cast_info in casts.items():
                cast_prompt = cast_info.get('prompt')
                if cast_prompt:
                    casts_prompts.append(f'Confidential cast: `{cast_name}` -> {cast_prompt}')
            
            field_prompt = f'- {field_label}'
            if specs_prompts:
                field_prompt += '\n' + '\n'.join(specs_prompts)
            if casts_prompts:
                field_prompt += '\n' + '\n'.join(f'    - {cast}' for cast in casts_prompts)
            
            fields.append(field_prompt)

        return fields
    
    def route_from_think(self, state: State) -> str:
        logger.debug(f'Route from think: {self._get_state_interview(state).__class__.__name__}')

        result = tools_condition(dict(state))
        if result == 'tools':
            logger.debug(f'Route: think -> tools')
            return 'tools'

        interview = self._get_state_interview(state)

        return 'listen'
    
    def route_from_tools(self, state: State) -> str:
        interview = self._get_state_interview(state)
        logger.debug(f'Route from tools: {interview._name}')

        # Auto-digest only the first time _enough becomes true
        if interview._enough:
            if not state['has_digested_confidentials']:
                logger.debug(f'Route: think -> digest_confidentials (first time _enough is true)')
                return 'digest_confidentials'
            if not state['has_digested_concludes']:
                logger.debug(f'Route: think -> digest_concludes (first time _enough is true)')
                return 'digest_concludes'

        return 'think'
    
    def route_from_digest(self, state: State) -> str:
        interview = self._get_state_interview(state)
        logger.debug(f'Route from digest_data: {interview._name}')

        # Check if we need to digest concludes after confidentials
        if interview._enough:
            if not state['has_digested_concludes']:
                logger.debug(f'Route: digest_data -> digest_concludes')
                return 'digest_concludes'

        result = tools_condition(dict(state))
        if result == 'tools':
            logger.debug(f'Route: digest_data -> tools')
            return 'tools'

        return 'think'
    
    # Node
    def teardown(self, state: State):
        # Ending will cause a return back to .go() caller.
        # That caller will expect the original interview object to reflect the conversation.
        interview = self._get_state_interview(state)
        logger.debug(f'Teardown> {interview._name}')
        self.interview._copy_from(interview)
        
    # Node
    def listen(self, state: State):
        interview = self._get_state_interview(state)
        logger.debug(f'Listen> {interview.__class__.__name__}')

        # The interrupt will cause a return back to .go() caller.
        # That caller will expect the original interview object to reflect the conversation.
        # So, for now just copy over the _chatfield dict.
        self.interview._copy_from(interview)

        msg = state['messages'][-1] if state['messages'] else None
        if not isinstance(msg, AIMessage):
            raise ValueError(f'Expected last message to be an AIMessage, got {type(msg)}: {msg!r}')

        # TODO: Make the LLM possibly set a prompt to the user.
        feedback = msg.content.strip()
        update = interrupt(feedback)

        logger.debug(f'Interrupt result: {update!r}')
        user_input = update["user_input"]
        user_msg = HumanMessage(content=user_input)
        return {'messages': [user_msg]}
    
    def get_graph_state(self) -> Dict[str, Any]:
        graph = self.graph
        config = self.config
        state = graph.get_state(config=config)
        return state.values
        
    def go(self, user_input: Optional[str] = None) -> str:
        """
        Process one conversation turn.

        The conversation will continue indefinitely until the application decides
        to stop. Check interview._done to see if all fields are collected, then
        call .end() when you want to terminate the conversation and run cleanup.

        Args:
            user_input: The user's input message (or None to start/continue)

        Returns:
            The content of the latest AI message as a string
        """
        logger.debug(f'Go: User input: {user_input!r}')
        state_values = self.get_graph_state()

        if state_values and state_values['messages']:
            logger.info(f'Continue conversation: {self.config["configurable"]["thread_id"]}')
            graph_input = Command(update={}, resume={'user_input': user_input})
        else:
            logger.info(f'New conversation: {self.config["configurable"]["thread_id"]}')
            thread_id = self.config["configurable"]["thread_id"]
            trace_url = f"https://smith.langchain.com/o/92e94533-dd45-4b1d-bc4f-4fd9476bb1e4/projects/p/1991a1b2-6dad-4d39-8a19-bbc3be33a8b6/t/{thread_id}"
            logger.info(f'LangSmith trace: {trace_url}')
            
            user_message = HumanMessage(content=user_input) if user_input else None
            user_messages = [user_message] if user_message else []
            graph_input = State(messages=user_messages)

        interrupts = []
        for event in self.graph.stream(graph_input, config=self.config):
            # The event is a dict mapping node name to node output.
            # print(f'ev> {event!r}')
            for node_name, state_delta in event.items():
                # print(f'Node {node_name!r} emitted: {state_delta!r}')
                if isinstance(state_delta, tuple):
                    if isinstance(state_delta[0], Interrupt):
                        interrupts.append(state_delta[0].value)

        if not interrupts:
            raise Exception(f'ERROR: No interrupts received - this should not happen as the graph should always route to listen')
        
        if len(interrupts) > 1:
            # TODO: I think this can happen? Because of parallel execution?
            raise Exception(f'Unexpected scenario multiple interrupts: {interrupts!r}')

        return interrupts[0]

    def end(self) -> None:
        """
        Explicitly end the conversation and run teardown cleanup.

        This jumps directly to the teardown node to perform any cleanup
        operations before ending the conversation. Call this method when
        you want to gracefully terminate the interview and run cleanup logic.

        The conversation will not automatically end when all fields are collected.
        Applications must decide when to call this method.
        """
        logger.debug(f'End: Jump to teardown')
        graph_input = Command(goto='teardown')

        for event in self.graph.stream(graph_input, config=self.config):
            # Just execute teardown, no output needed
            pass

    # TODO: digest() method to re-run digest.
    # I think it may need to reset the state has_digested_confidentials/has_digested_concludes flags

    @staticmethod
    def debug_prompt(prompt: str, use_color: bool = True) -> str:
        """
        Make a prompt string more readable for debugging by visualizing whitespace
        and detecting template interpolation bugs.

        - Template variables like {var}, {{var}}, {{{var}}} are highlighted as ERRORS
        - Newlines are shown with colored ↵ symbol
        - Trailing spaces are highlighted with colored background
        - Multiple consecutive spaces are shown with colored ␣ symbol
        - Tabs vs spaces in indentation are visualized
        - Invisible Unicode characters are detected

        Args:
            prompt: The prompt string to make visible
            use_color: Whether to use ANSI color codes (default: True)

        Returns:
            A version of the prompt with visible whitespace and colored highlights
        """
        import re

        # ANSI color codes for dark terminal backgrounds
        if use_color:
            # Bright colors for visibility on dark backgrounds
            RED_BG = '\033[48;5;196m'      # Bright red background for errors
            YELLOW_BG = '\033[48;5;226m'   # Yellow background for warnings
            CYAN = '\033[38;5;51m'          # Bright cyan for newlines
            MAGENTA = '\033[38;5;201m'      # Bright magenta for multiple spaces
            BLUE = '\033[38;5;39m'          # Bright blue for tabs
            ORANGE = '\033[38;5;208m'       # Orange for special chars
            GRAY = '\033[38;5;242m'         # Gray for space indents
            RESET = '\033[0m'
            BOLD = '\033[1m'
        else:
            RED_BG = YELLOW_BG = CYAN = MAGENTA = BLUE = ORANGE = GRAY = RESET = BOLD = ''

        lines = prompt.split('\n')
        result = []

        for i, line in enumerate(lines):
            processed = line

            # Detect template interpolation bugs - these should NOT exist in final prompts
            # Look for {var}, {{var}}, {{{var}}} etc.
            template_pattern = r'(\{+[^{}]+\}+)'
            if re.search(template_pattern, processed):
                processed = re.sub(
                    template_pattern,
                    lambda m: f'{RED_BG}{BOLD}⚠{m.group()}⚠{RESET}',
                    processed
                )

            # Detect invisible Unicode characters
            invisible_chars = {
                '\u200b': f'{ORANGE}[ZWSP]{RESET}',      # Zero-width space
                '\u00a0': f'{ORANGE}[NBSP]{RESET}',      # Non-breaking space
                '\u200c': f'{ORANGE}[ZWNJ]{RESET}',      # Zero-width non-joiner
                '\u200d': f'{ORANGE}[ZWJ]{RESET}',       # Zero-width joiner
                '\ufeff': f'{ORANGE}[BOM]{RESET}',       # Byte order mark
                '\u2060': f'{ORANGE}[WJ]{RESET}',        # Word joiner
            }

            for char, replacement in invisible_chars.items():
                if char in processed:
                    processed = processed.replace(char, replacement)

            # Handle indentation (before other processing)
            indent_match = re.match(r'^([ \t]+)', processed)
            if indent_match:
                indent = indent_match.group(1)
                rest = processed[len(indent):]

                # Check for mixed indentation (problematic!)
                if ' ' in indent and '\t' in indent:
                    # Mixed spaces and tabs - highlight as error
                    indent_visual = ''
                    for char in indent:
                        if char == ' ':
                            indent_visual += f'{RED_BG}·{RESET}'
                        else:  # tab
                            indent_visual += f'{RED_BG}→{RESET}'
                    processed = indent_visual + rest
                else:
                    # Pure spaces or pure tabs
                    if indent[0] == ' ':
                        # Spaces - use subtle gray markers
                        indent_visual = f'{GRAY}{"·" * len(indent)}{RESET}'
                    else:
                        # Tabs - use blue arrows
                        indent_visual = f'{BLUE}{"→" * len(indent)}{RESET}'
                    processed = indent_visual + rest

            # Handle trailing spaces - but check the raw line, not the processed one
            if line and line.endswith(' '):
                # Find where the trailing spaces start
                raw_stripped = line.rstrip(' ')
                num_trailing = len(line) - len(raw_stripped)

                # If we've already processed indentation, we need to be careful
                if RESET in processed:
                    # Find the actual content after all the formatting
                    parts = processed.rsplit(RESET, 1)
                    if len(parts) == 2 and parts[1].endswith(' ' * num_trailing):
                        parts[1] = parts[1][:-num_trailing] + f'{YELLOW_BG}{"·" * num_trailing}{RESET}'
                        processed = RESET.join(parts)
                elif processed.endswith(' '):
                    stripped = processed.rstrip(' ')
                    actual_trailing = len(processed) - len(stripped)
                    processed = stripped + f'{YELLOW_BG}{"·" * actual_trailing}{RESET}'

            # Replace multiple consecutive spaces (not in indentation)
            # Skip if we already processed indentation
            if not indent_match:
                processed = re.sub(
                    r'  +',
                    lambda m: f'{MAGENTA}{"␣" * len(m.group())}{RESET}',
                    processed
                )
            else:
                # For lines with indentation, only process spaces after the indent
                parts = processed.split(f'{RESET}', 1)
                if len(parts) == 2:
                    indent_part, rest_part = parts
                    rest_part = re.sub(
                        r'  +',
                        lambda m: f'{MAGENTA}{"␣" * len(m.group())}{RESET}',
                        rest_part
                    )
                    processed = f'{indent_part}{RESET}{rest_part}'

            result.append(processed)

        # Join with colored newline indicator
        return f'{CYAN}↵{RESET}\n'.join(result)