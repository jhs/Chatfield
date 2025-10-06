---
description: Generate daily commit diary and post to GitHub wiki
---

Read all git commits over the last 24 hours (or duration explicitly stated by the user) and create a Markdown diary entry summarizing the work, to post to the GitHub wiki. Content and formatting details below. To post to the wiki, push git changes within `wiki/` from this project root. (It is a git clone of the GitHub wiki.)

Steps:

1. State your time frame in scope for analysis. By default it is 24 hours but the user may optionally explicitly clarify a better time frame.
2. ALWAYS run a `pwd` in case Bash init scripts has changed it.
3. Use `git log` and `git diff`, filtering for the time frame in scope (e.g. "24 hours ago") to see all commit messages and changes. Analyze the commits to create a narrative summary of the high-level changes made.
4. Use `git diff` to see if I have uncommitted changes. If so, capture that as tomorrow's plan. Otherwise, tomorrow will have "No plan"
5. If no changes have happened during this time frame, STOP this procedure and tell the user there is nothing to do.
6. ALWAYS run a second `pwd` in case Bash configs have changed it.
7. Change to the wiki repo and ALWAYS confirm with a `pwd`; then `git pull` any changes from its origin
8. Create a new Markdown file for the content. The filename contains pipe characters: `Diary | Daily | YYYY_MM_DD.md`
9. `git add .` (to avoid issues with pipe characters), then commit with a message and push.
10. END OF PROCEDURE

The template below is default behavior, but allow the user to optionally override things as needed. Here is the diary entry template with notes to you <in angle brackets>:

# Development: <longhand date e.g. October 31, 2025>

## Summary

<A sole sentence summarizing the major changes, **bolding** key changes.>

<A sole sentence summarizing the major themes and apparent goals of the changes, *italicizing* key words.>

[See these changes in GitHub](/jhs/Chatfield/compare/<first commit 7 chars>...<final commit 7 chars>)

## Major Changes

* <Example "Update documentation about ...">
* <Example "Remove unused unit tests">
* <Etc>
<^^ the above is a bullet list of one or more roughly independent changes made (e.g. CLI options vs. documentation vs. unit tests). Summarize in a few words, second person, each change.>

## <Either "No Plan" if there is no plan for tomorrow or else "Plan for Tomorrow">

<Only if there is a plan for tomorrow from uncommitted changes, provide a short summary>

## Commits

* First commit: **<commit id 7 characters>**
* Final commit: **<commit id 7 characters>**
