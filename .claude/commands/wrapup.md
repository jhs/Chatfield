---
description: Generate daily commit diary and post to GitHub wiki
---

Read all git commits over the last 24 hours and create a Markdown diary entry summarizing the work. Post it to the GitHub wiki with a tititle of today's date in the format "YYYY-MM-DD". Use GitHub wiki via git, cloned to `wiki/` from this project root.

Steps:
1. Get today's date in the proper format by running `date +%Y-%m-%d`
2. Get commits from last 24 hours using `git log --since="24 hours ago" --pretty=format:"%h - %an, %ar : %s" --stat`
3. Analyze the commits and their changes to create a narrative summary
3. Format as a Markdown document in the wiki:
   - Filename in the wiki repo: `Daily_YYYY_MM_DD.md`
   - Title: Development Diary: <longhand date e.g. October 31, 2025>
   - "Summary" section: A paragraph summarizing the major work to the code. Then, a paragraph summarizing the overall theme or goals of the work.
   - "Major Changes" section: Deep dive on each major change, not specific code but abstract changes
   - Nothing else
