---
description: Generate daily commit diary and post to GitHub wiki
---

Read all git commits over the last 24 hours (or duration explicitly stated by the user) and create a Markdown diary entry summarizing the work, to post to the GitHub wiki. Content and formatting details below. To post to the wiki, push git changes within `wiki/` from this project root. (It is a git clone of the GitHub wiki.)

Steps:

1. Confirm the local system date by running: `date +%Y-%m-%d`
2. Use `git log` and `git diff`, filtering for the time frame in scope (e.g. "24 hours ago") to see all commit messages and changes. Analyze the commits to create a narrative summary of the high-level changes made.
3. If `Tomorrow_Plan.md` exists, capture its contents as tomorrow's plan. Otherwise, tomorrow will have "no plan".
4. If no changes have happened during this time frame, STOP this procedure and tell the user **There is nothing to do**.
5. In the wiki repo, `git pull` any changes from its origin.
6. Create a new Markdown file for the content. The filename contains pipe characters: `Daily | YYYY_MM_DD.md`.
7. `git add .` (to avoid issues with pipe characters)
8. Commit with a message and push.

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

## Plan for Tomorrow <But omit this entire section if there is no plan for tomorrow>

<Short summary of plan for tomorrow as apparent from uncommited changes>

## Commits

* First commit: **<commit id 7 characters>**
* Final commit: **<commit id 7 characters>**
