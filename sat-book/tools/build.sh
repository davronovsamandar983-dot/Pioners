#!/usr/bin/env bash
# dedupe -> generate -> typeset -> dist/
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== assets"
python3 tools/make_assets.py "DAVLAT KAMOLIDDINOV"

echo "== dedupe"
python3 tools/dedupe.py

echo "== generate"
python3 tools/gen_book.py

echo "== typeset"
mkdir -p book/.build dist
cd book
# Typeset into a scratch directory: two runs in one directory overwrite
# each other's .aux. Three passes -- the tikz overlays anchored to
# current page need a second to position, the contents a third to settle.
for i in 1 2 3; do
  pdflatex -interaction=nonstopmode -output-directory=.build main.tex >/dev/null
done

if grep -q '^!' .build/main.log; then
  echo "LaTeX errors:"; grep -A4 '^!' .build/main.log; exit 1
fi
over=$(grep -c 'Overfull' .build/main.log || true)
echo "overfull boxes: $over"

cp .build/main.pdf ../dist/SAT-Math-294-Hard-Questions.pdf
cd ..
echo "== done -> dist/SAT-Math-294-Hard-Questions.pdf"
python3 - <<'EOF'
import pymupdf
d = pymupdf.open("dist/SAT-Math-294-Hard-Questions.pdf")
print(f"   {d.page_count} pages")
EOF
