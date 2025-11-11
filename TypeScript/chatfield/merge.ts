/**
 * Interview state merging utilities for LangGraph reducer
 */
import { Interview } from './interview';
import { wrapInterviewWithProxy } from './interview-proxy';

/**
 * Helper function to detect changes in _chatfield structure
 * Simplified version of Python's DeepDiff check
 */
export function checkChatfieldChanges(aChatfield: any, bChatfield: any): boolean {
  // Check for field value changes
  if (aChatfield?.fields && bChatfield?.fields) {
    for (const fieldName in bChatfield.fields) {
      const aField = aChatfield.fields[fieldName];
      const bField = bChatfield.fields[fieldName];

      // Check if value has changed from null/undefined to something
      if (aField?.value !== bField?.value) {
        if (bField?.value != null) {
          return true; // Found a change
        }
      }
    }
  }

  // Check for role changes (alice/bob)
  if (aChatfield?.roles && bChatfield?.roles) {
    // Check alice role
    if (
      aChatfield.roles.alice?.type !== bChatfield.roles.alice?.type &&
      bChatfield.roles.alice?.type &&
      aChatfield.roles.alice?.type === 'Agent'
    ) {
      return true; // alice role changed from default
    }

    // Check bob role
    if (
      aChatfield.roles.bob?.type !== bChatfield.roles.bob?.type &&
      bChatfield.roles.bob?.type &&
      aChatfield.roles.bob?.type === 'User'
    ) {
      return true; // bob role changed from default
    }

    // Check for trait changes
    const aliceTraitsChanged =
      JSON.stringify(aChatfield.roles.alice?.traits) !==
      JSON.stringify(bChatfield.roles.alice?.traits);
    const bobTraitsChanged =
      JSON.stringify(aChatfield.roles.bob?.traits) !== JSON.stringify(bChatfield.roles.bob?.traits);
    if (aliceTraitsChanged || bobTraitsChanged) {
      return true;
    }
  }

  return false; // No significant changes detected
}

/**
 * Merge two Interview instances
 * Matches Python's merge_interviews logic exactly
 */
export function mergeInterviews(a: Interview | null, b: Interview | null): Interview {
  if (!a && !b) {
    // Unsure if this ever happens. Unsure if this ever matters.
    console.log(`WARN: Reducing two null Interview instances`);
    return wrapInterviewWithProxy(new Interview());
  }

  if (a) {
    a = wrapInterviewWithProxy(a);
  }
  if (b) {
    b = wrapInterviewWithProxy(b);
  }

  if (!a) {
    return b!;
  }
  if (!b) {
    return a!;
  }

  // Match Python lines 43-48: Check for changes
  // Simple diff for _chatfield - if no changes, return a
  if (a && b) {
    const hasChanges = checkChatfieldChanges(a._chatfield, b._chatfield);
    if (!hasChanges) {
      // console.log('Identical instances')
      return a;
    }

    // Match Python line 57: Assume B has all the latest information
    // TODO: Python assumes B has latest info. If LangGraph doesn't guarantee ordering, this could be a bug
    return b;
  }

  return b || a;
}

/**
 * Reducer for hasDigested: once true, stays true
 */
export function mergeHasDigested(a: boolean, b: boolean): boolean {
  return a || b;
}
