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
cd book
latexmk -pdf -interaction=nonstopmode -halt-on-error -quiet main.tex >/dev/null 2>&1 || {
  echo "pdflatex failed -- last 40 lines of the log:" >&2
  tail -40 main.log >&2
  exit 1
}
cd ..

mkdir -p dist
cp book/main.pdf "dist/SAT-Math-Mastery.pdf"
echo "==> dist/SAT-Math-Mastery.pdf"
