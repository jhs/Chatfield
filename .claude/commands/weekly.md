---
description: Generate weekly commit diary and post to GitHub wiki
---

Read all daily diary entries for a given week and create a Markdown weekly summary to post to the GitHub wiki. A week is defined as Sunday through Saturday. Content and formatting details below. To post to the wiki, push git changes within `wiki/` from this project root. (It is a git clone of the GitHub wiki.)

Steps:

1. Confirm the local system date and week number by running `date +%Y-%m-%d && date +%V`
2. Determine the week range (Sunday to Saturday) for the requested week. If no week specified, use the most recently completed week (last Sunday through last Saturday).
3. In the wiki repo then `git pull` any changes from its origin
4. Read all daily diary entries for the week under analysis. The filenames follow the pattern: `Daily | YYYY_MM_DD.md`
5. If no daily entries exist for this week, STOP this procedure and tell the user **There is nothing to do**.
6. Analyze the daily entries to create a narrative summary of the high-level themes and changes for the entire week.
7. Create a new Markdown file for the weekly content. The filename contains pipe characters: `Weekly | YYYY_WW.md` where WW is the ISO week number (01-53).
8. Concatenate all relevant daily .md files into a new file `Daily | YYYY_MM_DD to YYYY_MM_DD.md` newest content first, oldest content last.
9. `git rm` all relevant daily `.md` files.
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
