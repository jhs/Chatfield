"""LangGraph-based evaluator for Chatfield conversations."""

import re
import uuid
import traceback

from pydantic import BaseModel, Field, conset, create_model
from deepdiff import DeepDiff, extract

from typing import Annotated, Any, Dict, Optional, TypedDict, List, Literal, Set
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt, Interrupt
from langgraph.prebuilt import tools_condition
from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph.message import add_messages

from .interview import Interview

class State(TypedDict):
    messages: Annotated[List[Any] , add_messages    ]
    interview: Annotated[Interview, merge_interviews]

def merge_interviews(a:Interview, b:Interview) -> Interview:
    """
    LangGraph reducer for Interview objects. It merges any defined values.
    """
    result = None

    a_type = type(a)
    b_type = type(b)
    a_subclass = isinstance(a, b_type) and a_type is not b_type
    b_subclass = isinstance(b, a_type) and a_type is not b_type

    if a_subclass:
        # print(f'Reduce to subclass: {a!r}')
        return a
    if b_subclass:
        # print(f'Reduce to subclass: {b!r}')
        return b
    if a_type is not b_type:
        # TODO: I think this logic will change if/when changing the model in-flight works.
        raise NotImplementedError(f'Cannot reduce {a_type!r} and {b_type!r}')

    # a and b are the same type. Diff them to see what changed.
    left, right = a, b
    diff = DeepDiff(left._chatfield, right._chatfield, ignore_order=True)
    if not diff:
        # print(f'Identical instances: {a_type} and {b_type}')
        return a

    # Accumulate everything into the result in order to return it.
    # print(f'Reduce:')
    # print(f'  a: {type(a)} {a!r}')
    # print(f'  b: {type(b)} {b!r}')

    # TODO: Assume B has all the latest information. If LangGraph does not guarantee
    # any ordering, then this a bug which would trigger if they arrive differently from my testing.
    result = b

    type_changes = diff.pop('type_changes') if 'type_changes' in diff else {}
    for key_path, delta in type_changes.items():
        if delta['old_value'] is None and delta['new_value'] is not None:
            # print(f'  Field changing to non-None {key_path}: {extract(result._chatfield, key_path)}')
            pass
        else:
            raise NotImplementedError(f'Cannot reduce {a_type!r} with type changes at {key_path}: old={delta["old_value"]!r} new={delta["new_value"]!r}')

    values_changed = diff.pop('values_changed') if 'values_changed' in diff else {}
    for key_path, delta in values_changed.items():
        if delta['old_value'] is None and delta['new_value'] is not None:
            # print(f'  Field changing to non-None {key_path}: {extract(result._chatfield, key_path)}')
            pass
        elif (not delta['old_value']) and delta['new_value']:
            # print(f'  Field changing falsy to truthy {key_path}: {extract(result._chatfield, key_path)}')
            pass
        elif key_path == "root['roles']['alice']['type']" and delta['old_value'] == 'Agent':
            # print(f'  Field changing from default value {key_path}: {extract(result._chatfield, key_path)}')
            pass
        elif key_path == "root['roles']['bob']['type']" and delta['old_value'] == 'User':
            # print(f'  Field changing from default value {key_path}: {extract(result._chatfield, key_path)}')
            pass
        else:
            raise NotImplementedError(f'Cannot reduce {a_type!r} with value changes at {key_path}: old={delta["old_value"]!r} new={delta["new_value"]!r}')

    dict_added = diff.pop('dictionary_item_added') if 'dictionary_item_added' in diff else set()
    if dict_added:
        pass # All adds are fine.

    iterable_added = diff.pop('iterable_item_added') if 'iterable_item_added' in diff else set()
    if iterable_added:
        pass # All adds are fine.
    
    if diff:
        raise NotImplementedError(f'Cannot reduce {a_type!r} with non-type changes: {diff}')

    return result


class Interviewer:
    """
    Interviewer that manages conversation flow.
    """
    
    def __init__(self, interview: Interview, thread_id: Optional[str]=None, llm=None, llm_id=None, temperature=None):
        self.checkpointer = InMemorySaver()

        self.config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}
        self.interview = interview
        theAlice = self.interview._alice_role_name()
        theBob   = self.interview._bob_role_name()

        self.llm = llm
        if not self.llm:
            # llm_id = 'openai:o3-mini'
            # temperature = None
            # llm_id = 'openai:gpt-5'
            # llm_id = 'openai:gpt-4.1'
            llm_id = llm_id or 'openai:gpt-4o'
            temperature = temperature or 0.0
            if llm_id in ('openai:o3-mini', 'openai:o3'):
                temperature = None
            self.llm = init_chat_model(llm_id, temperature=temperature)

        builder = StateGraph(State)

        builder.add_node('initialize', self.initialize)
        builder.add_node('think'     , self.think)
        builder.add_node('listen'    , self.listen)
        builder.add_node('tools'     , self.tools)
        builder.add_node('digest'    , self.digest)
        builder.add_node('teardown'  , self.teardown)

        builder.add_edge             (START       , 'initialize')
        builder.add_edge             ('initialize', 'think')
        builder.add_conditional_edges('think'     , self.route_from_think)
        builder.add_edge             ('listen'    , 'think')
        builder.add_conditional_edges('tools'     , self.route_from_tools, ['think', 'digest'])
        builder.add_conditional_edges('digest'    , self.route_from_digest, ['tools', 'think'])
        builder.add_edge             ('teardown'  , END    )

        self.graph = builder.compile(checkpointer=self.checkpointer)
        
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
        print(f'Initialize> {self._get_state_interview(state).__class__.__name__}')
        
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
            args_schema[field_name] = Optional[field_definition]  # Optional for update
        
        tool_name = f'update_{interview._id()}'
        tool_desc = f'Record valid information shared by the {interview._bob_role_name()} about the {interview._name()}'
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
            
            # Conclude fields are non-nullable, non-optional.
            args_schema[field_name] = field_definition
        
        tool_name = f'conclude_{interview._id()}'
        tool_desc = (
            f'Record key required information'
            f' about the {interview._name()}'
            f' by summarizing, synthesizing, or recalling'
            f' the conversation so far with the {interview._bob_role_name()}'
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
        print(f'Tools> {interview._name()}')
        
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
        print(f'Run tool {tool_call_name}: {tool_call_id} {kwargs!r}')
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
    def digest(self, state: State):
        interview = self._get_state_interview(state)
        print(f'Digest> {interview._name()}')

        # First digest undefined confidential fields. Then digest the conclude fields.
        for field_name, chatfield in interview._chatfield['fields'].items():
            if not chatfield['specs']['conclude']:
                if chatfield['specs']['confidential']:
                    if not chatfield['value']:
                        return self.digest_confidential(state)
        return self.digest_conclude(state)
    
    def digest_confidential(self, state: State):
        interview = self._get_state_interview(state)
        print(f'Digest Confidential> {interview._name()}')

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
                field_definitions[field_name] = field_definition
            else:
                # Actually, just do not mention it.
                # field_definitions[field_name] = (Literal[None], Field(description='Must be null because the field is already recorded'))
                pass

        fields_prompt = '\n'.join(fields_prompt)

        # Build a special llm object bound to a tool which explicitly requires the proper arguments.
        tool_name = f'updateConfidential_{interview._id()}'
        tool_desc = (
            f'Record those confidential fields about the {interview._name()}'
            f' from the {interview._bob_role_name()}'
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
        sys_msg = SystemMessage(content=(
            f'You have successfully recorded good {interview._name()} fields.'
            f' Now, before messaging {interview._bob_role_name()} again,'
            f' you must perform one more followup update to record'
            f' that there is no relevant information for'
            f' the not-yet-defined confidential fields, listed below to remind you.'
            f' Use the update tool call to record that there is no forthcoming information'
            f' for these fields.'
            f' After a successful tool call, you may resume conversation with the {interview._bob_role_name()} again.'
            f'\n\n'
            f'## Confidential Fields needed for {interview._name()}\n'
            f'\n'
            f'{fields_prompt}'
        ))

        all_messages = state['messages'] + [sys_msg]
        llm_response_message = llm.invoke(all_messages)
        # print(f'New LLM response message: {llm_response_message!r}')

        # LangGraph wants only net-new messages. Its reducer will merge them.
        new_messages = [sys_msg] + [llm_response_message]
        return {'messages':new_messages}
    
    def mk_field_definition(self, interview:Interview, field_name: str, chatfield: Dict[str, Any]):
        casts_definitions = self.mk_casts_definitions(chatfield)
        field_definition = create_model(
            field_name,
            __doc__= chatfield['desc'],
            value  = (str, Field(title=f'Natural Value', description=f'The most typical valid representation of a {interview._name()} {field_name}')),
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

    def digest_conclude(self, state: State):
        interview = self._get_state_interview(state)
        print(f'Digest Conclude> {interview._name()}')

        # Define the tool for the LLM to call.
        conclude_tool = self.llm_conclude_tool(state)
        llm = self.llm.bind_tools([conclude_tool])
        
        fields_prompt = self.mk_fields_prompt(interview, mode='conclude')
        sys_msg = SystemMessage(content=(
            f'You have successfully recorded enough information'
            f' to draw conclusions and record key information from this conversation.'
            f' You must now record all conclusion fields, defined below.'
            f'\n\n'
            f'## Conclusion Fields needed for {interview._name()}\n'
            f'\n'
            f'{fields_prompt}'
        ))

        all_messages = state['messages'] + [sys_msg]
        llm_response_message = llm.invoke(all_messages)
        # print(f'New LLM response message: {llm_response_message!r}')

        # LangGraph wants only net-new messages. Its reducer will merge them.
        new_messages = [sys_msg] + [llm_response_message]
        return {'messages':new_messages}

    # Node
    def think(self, state: State):
        print(f'Think> {self._get_state_interview(state).__class__.__name__}')

        # Track any system messages that need to be added.
        new_system_message = None

        #
        # System Messages
        #

        prior_system_messages = [msg for msg in state['messages'] if isinstance(msg, SystemMessage)]
        if len(prior_system_messages) == 0:
            print(f'Start conversation in thread: {self.config["configurable"]["thread_id"]}')
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
        print(f'Tool input for {len(defined_args)} fields: {", ".join(defined_args)}')
        for field_name, llm_field_value in kwargs.items():
            if llm_field_value is None:
                continue

            # Handle both Pydantic models and plain dicts (for testing)
            if hasattr(llm_field_value, 'model_dump'):
                llm_values = llm_field_value.model_dump()
            else:
                llm_values = llm_field_value
            print(f'LLM found a valid field: {field_name!r} = {llm_values!r}')
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
        collection_name = interview._name()
        theAlice = interview._alice_role_name()
        theBob = interview._bob_role_name()
        
        # Count validation rules - will be updated by mk_fields_prompt
        counters = {'hint': 0, 'must': 0, 'reject': 0}
        
        fields_prompt = self.mk_fields_prompt(interview, counters=counters)

        alice_traits = ''
        bob_traits = ''

        traits = interview._alice_role().get('traits', [])
        if traits:
            alice_traits = f'# Traits and Characteristics about the {theAlice}\n\n'
            # Maintain source-code order, since decorators apply bottom-up.
            alice_traits += '\n'.join(f'- {trait}' for trait in reversed(traits))

        traits = interview._bob_role().get('traits', [])
        if traits:
            bob_traits = f'# Traits and Characteristics about the {theBob}\n\n'
            # Maintain source-code order, since decorators apply bottom-up.
            bob_traits += '\n'.join(f'- {trait}' for trait in reversed(traits))

        with_traits = f''
        if alice_traits or bob_traits:
            with_traits = f" Participants' characteristics and traits will be described below."
            
        alice_and_bob = ''
        if alice_traits or bob_traits:
            alice_and_bob = f'\n\n'
            alice_and_bob += alice_traits
            if alice_traits and bob_traits:
                alice_and_bob += '\n\n'
            alice_and_bob += bob_traits

        # Build description section if provided
        description_section = ''
        if interview._chatfield['desc']:
            description_section = f'\n\n## Description\n\n{interview._chatfield["desc"]}'

        explain_fields = ''
        
        if counters['must'] > 0 or counters['reject'] > 0:
            # Explain how validation works
            labels_and = ''
            labels_or = ''
            how_it_works = ''
            
            if counters['must'] > 0 and counters['reject'] == 0:
                # Must only
                labels_and = '"Must"'
                labels_or = '"Must"'
                how_it_works = 'All "Must" rules must pass for the field to be valid.'
            elif counters['must'] == 0 and counters['reject'] > 0:
                # Reject only
                labels_and = '"Reject"'
                labels_or = '"Reject"'
                how_it_works = 'Any "Reject" rule which does not pass causes the field to be invalid.'
            elif counters['must'] > 0 and counters['reject'] > 0:
                # Both must and reject
                labels_and = '"Must" and "Reject"'
                labels_or = '"Must" or "Reject"'
                how_it_works = (
                    'All "Must" rules associated with a field must pass for the field to be valid.'
                    '\n\n'
                    'Any "Reject" rule associated with a field which does not pass causes the field to be invalid.'
                )
            
            explain_fields += (
                f'\n\n# Validation Rules: {labels_and}\n\n'
                f'Always ensure that all {labels_and} rules are satisfied before recording information.'
                f'\n\n'
                f'{how_it_works}'
                f'\n\n'
                f'If the {theBob} provides information not satisfying {labels_or} rules,'
                f' explain the situation'
                f' in a manner suitable for the {theAlice} role.'
            )
        
        if counters['hint'] > 0:
            explain_fields += (
                '\n\n# How Hints Work\n\n'
                'Fields may have one or more "Hints", which are clarifications to you,'
                ' or "tooltip"-style explanations,'
                ' or example content.'
                f' Remember these hints, and provide this information to the {theBob} as needed.'
            )
            
            if counters['must'] > 0 or counters['reject'] > 0:
                # Hints override validation
                explain_fields += (
                    '\n\n'
                    f'To explain main ideas or examples to the {theBob}, use Hints.'
                    ' Mention specific validation rules as they become relevant in conversation.'
                )

        # TODO: Do not mention casts if there are no casts.
        # TODO: Maybe remind the LLM about the validation rules later in conversation, or at/around tool calls.
        res = (
            f'You are the conversational {theAlice} focused on gathering key information'
            f' in conversation with the {theBob}, detailed below.{with_traits}'
            f' As soon as you encounter relevant information in conversation, immediately use tools to record information'
            f' fields and their related "casts", which are cusom conversions you provide for each field.'
            f' Although the {theBob} may take the conversation anywhere, your response must fit the conversation and your'
            f' respective roles while refocusing the discussion so that you can gather'
            f' clear key {collection_name} information from the {theBob}.'
            f'{alice_and_bob}'
            f'{explain_fields}'
            f'\n\n----\n\n'
            f'# Collection: {collection_name}'
            f'{description_section}'
            f'\n\n## Fields to Collect\n\n'
            f'{fields_prompt}'
        )
        return res

    def mk_fields_prompt(self, interview: Interview, mode='normal', field_names=None, counters=None) -> str:
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
                    f' However, if the {interview._bob_role_name()} ever volunteers or implies it, you must record this information.'
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
                    casts_prompts.append(f'{cast_name.capitalize()}: {cast_prompt}')
            
            # Disable casts for the system prompt becauase they are required parameters for the tool call.
            casts_prompts = []

            field_prompt = f'- {field_label}'
            if specs_prompts:
                field_prompt += '\n' + '\n'.join(specs_prompts)
            
            # Casts are disabled in system prompt as per comment
            # if casts_prompts:
            #     field_prompt += '\n' + '\n'.join(f'    - {cast}' for cast in casts_prompts)
            
            fields.append(field_prompt)

        fields = '\n\n'.join(fields)
        return fields
    
    def route_from_think(self, state: State) -> str:
        print(f'Route from think: {self._get_state_interview(state).__class__.__name__}')

        result = tools_condition(dict(state))
        if result == 'tools':
            print(f'Route: think -> tools')
            return 'tools'

        interview = self._get_state_interview(state)
        if interview._done:
            # print(f'Route: to teardown')
            return 'teardown'
        
        # Either digest once, the first time _enough becomes true.
        # Or, digest after every subsequent user message. For now, do the former
        # because then _done would evaluate true, so the above return would trigger.
        if interview._enough:
            # TODO: I wonder if this is needed anymore? Does digest happen differently in the graph now?
            print(f'Route: think -> digest')
            return 'digest'

        return 'listen'
    
    def route_from_tools(self, state: State) -> str:
        interview = self._get_state_interview(state)
        print(f'Route from tools: {interview._name()}')

        if interview._enough and not interview._done:
            print(f'Route: tools -> digest')
            return 'digest'

        return 'think'
    
    def route_from_digest(self, state: State) -> str:
        interview = self._get_state_interview(state)
        print(f'Route from digest: {interview._name()}')

        result = tools_condition(dict(state))
        if result == 'tools':
            print(f'Route: digest -> tools')
            return 'tools'

        return 'think'
    
    # Node
    def teardown(self, state: State):
        # Ending will cause a return back to .go() caller.
        # That caller will expect the original interview object to reflect the conversation.
        interview = self._get_state_interview(state)
        print(f'Teardown> {interview._name()}')
        self.interview._copy_from(interview)
        
    # Node
    def listen(self, state: State):
        interview = self._get_state_interview(state)
        print(f'Listen> {interview.__class__.__name__}')

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

        print(f'Interrupt result: {update!r}')
        user_input = update["user_input"]
        user_msg = HumanMessage(content=user_input)
        return {'messages': [user_msg]}
        
    def go(self, user_input: Optional[str] = None) -> Optional[str]:
        """
        Process one conversation turn.
        
        Args:
            user_input: The user's input message (or None to start/continue)
            
        Returns:
            The content of the latest AI message as a string, or None if conversation is complete
        """
        print(f'Go: User input: {user_input!r}')
        state = self.graph.get_state(config=self.config)

        if state.values and state.values['messages']:
            print(f'Continue conversation: {self.config["configurable"]["thread_id"]}')
            graph_input = Command(update={}, resume={'user_input': user_input})
        else:
            print(f'New conversation: {self.config["configurable"]["thread_id"]}')
            thread_id = self.config["configurable"]["thread_id"]
            trace_url = f"https://smith.langchain.com/o/92e94533-dd45-4b1d-bc4f-4fd9476bb1e4/projects/p/1991a1b2-6dad-4d39-8a19-bbc3be33a8b6/t/{thread_id}"
            print(f'LangSmith trace: {trace_url}')
            
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
            print(f'WARN: Return None, probably should generate a message anyway')
            return None
        
        if len(interrupts) > 1:
            # TODO: I think this can happen? Because of parallel execution?
            raise Exception(f'Unexpected scenario multiple interrupts: {interrupts!r}')

        return interrupts[0]