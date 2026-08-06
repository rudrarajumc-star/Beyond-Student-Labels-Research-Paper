#!/bin/zsh
cd "$(dirname "$0")"
echo "Cleaning stale git locks..."
find .git -name "*.lock" -delete
find .git -name "tmp_obj_*" -delete
echo "Replacing old history with the clean single commit..."
git branch -D main 2>/dev/null
git branch -m main
git remote remove origin 2>/dev/null
echo
echo "=== FINAL STATE ==="
git log --oneline
echo "Commits: $(git rev-list --count main) (should be 1)"
git remote -v
echo "(no remote listed = correct)"
echo
echo "NEXT: 1) On github.com delete BOTH old repositories."
echo "      2) Open GitHub Desktop -> Publish repository -> beyond-student-labels (uncheck private)."
