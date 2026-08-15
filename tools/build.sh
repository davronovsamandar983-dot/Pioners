#!/usr/bin/env bash
# Build the book: validate the banks, regenerate the LaTeX, run pdflatex.
#
#   tools/build.sh              validate + generate + build the PDF
#   tools/build.sh --no-check   skip validation (fast preview)
#   tools/build.sh --strict     every problem must carry a `verify` snippet
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

CHECK=1
STRICT=""
for arg in "$@"; do
  case "$arg" in
    --no-check) CHECK=0 ;;
    --strict)   STRICT="--require-verify" ;;
    *) echo "unknown option: $arg" >&2; exit 2 ;;
  esac
done

if [ "$CHECK" -eq 1 ]; then
  echo "==> validating problem banks"
  python3 tools/validate.py $STRICT
fi

echo "==> generating LaTeX"
python3 tools/gen_book.py

echo "==> typesetting"
# Build into a scratch directory rather than alongside the sources: two
# concurrent pdflatex runs in one directory overwrite each other's .aux and
# the second one dies on a half-written file.
BUILD="book/.build"
rm -rf "$BUILD"
mkdir -p "$BUILD"
mkdir -p dist

# main.tex     -- the full edition: lessons, problems, worked solutions, key
# problems.tex -- the problem edition: the same 880 questions and the key,
#                 with no teaching and no solutions
typeset() {
  local src="$1" out="$2"
  ( cd book && latexmk -pdf -interaction=nonstopmode -halt-on-error -quiet \
        -outdir=.build "$src.tex" >/dev/null 2>&1 ) || {
    echo "pdflatex failed on $src.tex -- last 40 lines of the log:" >&2
    tail -40 "$BUILD/$src.log" >&2
    exit 1
  }
  cp "$BUILD/$src.pdf" "dist/$out"
  echo "==> dist/$out ($(pdfinfo "dist/$out" 2>/dev/null | awk '/^Pages/{print $2" pages"}'))"
}

typeset main     "SAT-Math-Mastery.pdf"
typeset problems "SAT-Math-Mastery-Problems.pdf"
