---
description: Generate daily commit diary and post to GitHub wiki
---

Read all git commits over the last 24 hours and create a Markdown diary entry summarizing the work. Post it to the GitHub wiki with a title reflecting today's date. (Content and formatting details below.) To post to the wiki, push git changes within `wiki/` from this project root. (It is a git clone of the GitHub wiki.)

Steps:
1. Get today's date in the proper format by running `date +%Y-%m-%d`
2. State aloud the time frame in scope. By default it is 24 hours but the user may optionally explicitly clarify a better time frame.
3. Use `git log` and `git diff`, filtering for the time frame in scope (e.g. "24 hours ago") to see all commit messages and changes. Analyze the commits to create a narrative summary of the high-level changes made.
4. `git pull` any changes from the wiki repo origin
5. Format as a Markdown document in the wiki repo. Follow all of the rules below as default behavior, but allow the user to optionally override things as needed.
   - Filename in the wiki repo: `Daily_YYYY_MM_DD.md`
   - Title: `Development Diary: <longhand date e.g. October 31, 2025>`
   - "Summary" section: One sentence summarizing the major changes, **bolding** key words. Next paragraph: one sentence summarizing the major themes or apparent goals of the changes, **bolding** key words.
   - "Major Changes" section: A bullet list of one or more roughly independent changes made (e.g. CLI options vs. documentation vs. unit tests). Summarize in one sentence the gist of the changes.