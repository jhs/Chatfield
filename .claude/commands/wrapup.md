---
description: Generate daily commit diary and post to GitHub wiki
---

Read all git commits from the last 24 hours and create a Markdown "diary" entry summarizing the work. Post it to the GitHub wiki with a timestamped title in the format "YYYY-MM-DD".

Steps:
1. Get commits from last 24 hours using `git log --since="24 hours ago" --pretty=format:"%h - %an, %ar : %s" --stat`
2. Analyze the commits and their changes to create a narrative summary
3. Format as a Markdown document with:
   - Title: Timestamped (YYYY-MM-DD-HHMM format)
   - Summary section describing overall theme/goal of work
   - Detailed sections covering each major change
   - Files modified list
4. Use `gh api` to post to the repository wiki:
   - Clone/update wiki if needed: `gh repo clone owner/repo.wiki`
   - Create new file with timestamped name
   - Commit and push to wiki repository
