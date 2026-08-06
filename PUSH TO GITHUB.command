#!/bin/zsh
# Double-click this to commit the audit corrections and push them to GitHub.
# Safe to run more than once. It never force-pushes and never rewrites history.
cd "$(dirname "$0")"

echo "=== Clearing stale git locks (harmless if none) ==="
find .git -name "*.lock" -delete 2>/dev/null
find .git -name "tmp_obj_*" -delete 2>/dev/null

echo
echo "=== SAFETY CHECK: make sure no secrets are staged ==="
if git ls-files --error-unmatch .env > /dev/null 2>&1; then
  echo "!! STOP: .env is tracked by git. Run:  git rm --cached .env"
  echo "!! Then re-run this script."
  exit 1
fi
echo "OK: .env is not tracked."

echo
echo "=== What will be committed ==="
git add -A
git status --short

echo
echo "Press RETURN to commit and push, or Ctrl-C to cancel."
read _

git commit -m "Add make_report_figures.py (all 5 figures at 300 dpi from raw data); \
document figure provenance; fix duplication rates (Llama 19.3%, Mistral 4.2%); \
correct judge/human attribution on \$20.93 item; restore Steele & Aronson citation; \
correct stale April dates to July 2026; add arXiv build assets (figures, fonts, preamble); \
regenerate PDF/HTML and arXiv source from corrected source."

echo
echo "=== Pushing to origin/main ==="
git push origin main

echo
echo "=== DONE. Now verify in a browser (logged OUT, or a private window): ==="
echo "    https://github.com/rudrarajumc-star/prompt-sensitivity-study"
echo "If it 404s while logged out, the repo is PRIVATE — open it in"
echo "Settings -> General -> Danger Zone -> Change visibility -> Public."
echo "The paper cites this URL, so it MUST be public before you post to arXiv."
