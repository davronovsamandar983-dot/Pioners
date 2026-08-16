#!/usr/bin/env bash
# Compile ONE topic on its own and render its pages to PNG.
#   bash tools/topic_preview.sh 01-linear-equations-one-variable
# Produces build/preview-<slug>.pdf and build/preview-<slug>-N.png
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
SLUG="${1:?usage: topic_preview.sh <slug>}"
SLUG="${SLUG%.tex}"

TEX="book/topics/${SLUG}.tex"
ANS="book/answers/${SLUG}.tex"
[[ -f "$TEX" ]] || { echo "no such topic file: $TEX" >&2; exit 1; }

mkdir -p build
OUT="build/preview-${SLUG}.tex"
{
  echo '\documentclass[11pt,a4paper,oneside]{book}'
  echo '\input{../book/preamble.tex}'
  echo '\begin{document}'
  echo "\\input{../${TEX}}"
  [[ -f "$ANS" ]] && echo "\\clearpage\\input{../${ANS}}"
  echo '\end{document}'
} > "$OUT"

cd build
for pass in 1 2; do
  pdflatex -interaction=nonstopmode -halt-on-error "preview-${SLUG}.tex" >/dev/null 2>&1 || {
    echo "pdflatex FAILED for ${SLUG}:" >&2
    grep -nE "^! " -A4 "preview-${SLUG}.log" | head -40 >&2
    exit 1
  }
done

pages=$(pdfinfo "preview-${SLUG}.pdf" | awk '/^Pages:/{print $2}')
over=$(grep -c "Overfull \\\\hbox" "preview-${SLUG}.log" || true)
echo "OK  build/preview-${SLUG}.pdf  (${pages} pages, ${over} overfull hbox)"

rm -f "preview-${SLUG}"-[0-9]*.png
pdftoppm -png -r 80 "preview-${SLUG}.pdf" "preview-${SLUG}"
ls "preview-${SLUG}"-*.png | sed 's|^|    build/|'
