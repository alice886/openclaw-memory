#!/bin/bash
cd ~/.openclaw/workspace || exit 1

git add -A
git diff --quiet --cached && exit 0  # nothing to commit

COMMIT_MSG="auto backup $(date '+%Y-%m-%d_%H:%M:%S')"
git commit -m "$COMMIT_MSG"
git push
