---
description: Generate weekly commit diary and post to GitHub wiki
---

Read all daily diary entries for a given week and create a Markdown weekly summary to post to the GitHub wiki. A week is defined as Sunday through Saturday. Content and formatting details below. To post to the wiki, push git changes within `wiki/` from this project root. (It is a git clone of the GitHub wiki.)

Steps:

1. Confirm the local system date by running: `date +%Y-%m-%d`
2. Determine the week range (Sunday to Saturday) for the requested week. If no week specified, use the most recently completed week (last Sunday through last Saturday).
3. ALWAYS run a `pwd` in case Bash configs have changed it.
4. Change to the wiki repo and ALWAYS confirm with a `pwd`; then `git pull` any changes from its origin
5. Read all daily diary entries for the week under analysis. The filenames follow the pattern: `Daily | YYYY_MM_DD.md`
6. If no daily entries exist for this week, STOP this procedure and tell the user **There is nothing to do**.
7. Analyze the daily entries to create a narrative summary of the high-level themes and changes for the entire week.
8. ALWAYS run a `pwd` to confirm still in wiki directory.
9. Create a new Markdown file for the weekly content. The filename contains pipe characters: `Weekly | YYYY_WW.md` where WW is the ISO week number (01-53).
10. `git add .` (to avoid issues with pipe characters), then commit with a message and push.
11. END OF PROCEDURE

The template below is default behavior, but allow the user to optionally override things as needed. Here is the weekly diary entry template with notes to you <in angle brackets>:

# Development Week: <week range e.g. "September 21-27, 2025">

## Summary

<A sole sentence summarizing the major accomplishments and changes for the week, **bolding** key achievements.>

<A sole sentence summarizing the overarching themes and strategic direction of the week's work, *italicizing* key words.>

[See these changes in GitHub](/jhs/Chatfield/compare/<first commit 7 chars>...<final commit 7 chars>)

## Major Themes

* <Example "Refactored template system across both implementations">
* <Example "Enhanced security evaluation framework">
* <Etc>
<^^ the above is a bullet list of 3-5 major themes or areas of work that spanned multiple days. Summarize at a higher level than daily entries, focusing on weekly accomplishments.>

## Commits

* First commit on <day of week>: **<commit id 7 characters>**
* Final commit on <day of week>: **<commit id 7 characters>**
