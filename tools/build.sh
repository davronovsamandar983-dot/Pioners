#!/usr/bin/env bash
# Build the full book from whatever topics currently exist.
#   bash tools/build.sh            -> build/sat_math_mastery.pdf
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"
mkdir -p build

# Regenerate the include lists so a partially finished book still compiles.
: > build/_topics.tex
: > build/_answers.tex
shopt -s nullglob
for f in book/topics/*.tex; do
  echo "\\input{../book/topics/$(basename "$f")}" >> build/_topics.tex
done
for f in book/answers/*.tex; do
  echo "\\input{../book/answers/$(basename "$f")}" >> build/_answers.tex
done
shopt -u nullglob

n_topics=$(grep -c . build/_topics.tex || true)
echo "building with ${n_topics} topic file(s)"

cd book
# three passes: TOC + TikZ positions need to settle
for pass in 1 2 3; do
  pdflatex -interaction=nonstopmode -halt-on-error \
           -output-directory=../build main.tex > /dev/null 2>&1 || {
    echo "pdflatex FAILED on pass ${pass}; first errors:" >&2
    grep -nE "^! " -A3 ../build/main.log | head -40 >&2
    exit 1
  }
done
cd ..

mv -f build/main.pdf build/sat_math_mastery.pdf
pages=$(pdfinfo build/sat_math_mastery.pdf 2>/dev/null | awk '/^Pages:/{print $2}')
echo "OK  build/sat_math_mastery.pdf  (${pages:-?} pages)"

# surface layout damage rather than hiding it
overfull=$(grep -c "Overfull \\\\hbox" build/main.log || true)
echo "overfull hboxes: ${overfull}"
