"""Interview state merging utilities for LangGraph reducer."""

from deepdiff import DeepDiff, extract
from .interview import Interview


def merge_interviews(a: Interview, b: Interview) -> Interview:
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
        pass  # All adds are fine.

    iterable_added = diff.pop('iterable_item_added') if 'iterable_item_added' in diff else set()
    if iterable_added:
        pass  # All adds are fine.

    if diff:
        raise NotImplementedError(f'Cannot reduce {a_type!r} with non-type changes: {diff}')

    return result


def merge_has_digested(a: bool, b: bool) -> bool:
    """Reducer for has_digested: once True, stays True."""
    return a or b