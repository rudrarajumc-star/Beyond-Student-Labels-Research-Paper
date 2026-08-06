#!/bin/zsh
# Double-click AFTER rewriting a section.
# Confirms you changed prose without accidentally changing any number,
# then rebuilds the PDF, HTML, and arXiv package.
cd "$(dirname "$0")"

BASE="_audit_backup_2026-07-17/NUMBER_FINGERPRINT_baseline.txt"

echo "=== 1. Did any number change? ==="
grep -oE "[0-9]+\.[0-9]+" report/REPORT.md | sort > /tmp/nums_now.txt
if diff -q "$BASE" /tmp/nums_now.txt > /dev/null 2>&1; then
  echo "   OK — every numeric token is identical to the verified baseline."
else
  echo "   !! NUMBERS CHANGED. Review carefully before continuing:"
  echo "   (< = in verified baseline but now missing;  > = new/altered)"
  diff "$BASE" /tmp/nums_now.txt | head -30
  echo
  echo "   If a change was intentional, fine. If not, undo it —"
  echo "   the baseline values were verified against the raw data."
fi

echo
echo "=== 2. Are the key corrections still present? ==="
for s in "American Educational Research Journal" "AI-assistance disclosure" "clustered on the 539" "overstatement"; do
  c=$(grep -c "$s" report/REPORT.md)
  [ "$c" -ge 1 ] && echo "   OK   $s" || echo "   !! MISSING: $s"
done

echo
echo "=== 3. Rebuilding deliverables ==="
cd report
pandoc REPORT.md -o REPORT.html --standalone --mathml && echo "   HTML rebuilt"
pandoc REPORT.md -o REPORT.pdf --pdf-engine=xelatex -H _header.tex -V geometry:margin=1in && echo "   PDF rebuilt"
cd ..
pandoc report/REPORT.md -s -o arxiv/main.tex -H "$(pwd)/arxiv/preamble.tex" \
  -V geometry:margin=1in -V fontsize=11pt -V linkcolor=blue
sed -i '' 's|\.\./results/figures/|figures/|g' arxiv/main.tex 2>/dev/null || sed -i 's|\.\./results/figures/|figures/|g' arxiv/main.tex
sed -i '' '1i\
%!TEX program = xelatex
' arxiv/main.tex 2>/dev/null || sed -i '1i %!TEX program = xelatex' arxiv/main.tex
cd arxiv
xelatex -interaction=nonstopmode main.tex > /dev/null 2>&1
xelatex -interaction=nonstopmode main.tex > /dev/null 2>&1
[ -f main.pdf ] && echo "   arXiv PDF rebuilt ($(python3 -c "import sys;print()" 2>/dev/null)pages: $(pdfinfo main.pdf 2>/dev/null | awk '/Pages/{print $2}'))"
rm -f ../arxiv_submission.zip
zip -r ../arxiv_submission.zip main.tex figures fonts -x "*.DS_Store" > /dev/null
echo "   arxiv_submission.zip rebuilt"

echo
echo "=== DONE. Open report/REPORT.pdf and read your rewritten section aloud. ==="
