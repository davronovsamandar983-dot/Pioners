# SAT Math — 294 Hard Questions

One workbook merged from three hard-question collections, deduplicated,
regrouped by the four tested SAT domains, and set **three problems to a
page** so there is room to work.

| | |
| --- | --- |
| Output | `dist/SAT-Math-294-Hard-Questions.pdf` — 108 pages |
| Plain text | `dist/SAT-Math-294-Hard-Questions.txt` — 79 KB |
| Problems | 294 |
| Algebra | 43 |
| Advanced Math | 117 |
| Problem-Solving and Data Analysis | 48 |
| Geometry and Trigonometry | 86 |
| Answers published | 292 / 294 |

## Sources

| Tag | Collection | Pulled in | Answer key |
| --- | --- | --- | --- |
| A | *Collection of 70 HARD SAT Math questions* — Merey Altaiuly | 70 | published |
| B | *Advanced Digital SAT Math, 150 Hard Questions* — M. & M. Stroup | 150 | none — solved here |
| C | *PrepPros Advanced Digital SAT Math Course #2* (157 pp.) | 74 | published |

All three had to be transcribed by reading the rendered pages. A and C
are scans with no usable text layer — C's carries nothing but `@DSATuz`
watermarks — and B's text layer has a broken font encoding that turns
every variable into punctuation.

### What source C actually contained

Source C is a 157-page slide deck: one question per page for 150 pages,
then a published answer key on pages 151–157. Roughly half of it is the
same collection as source B — its odd-numbered questions match B's
odd-numbered questions almost throughout. Only the questions that were
genuinely new were pulled in, so C contributes 74 rather than 150.

C's key is also an independent check on the answers solved for B: **47
of B's answers appear in it, and all 47 agree**. It resolved two that
were left open, and showed that B95 had been transcribed with its two
quantities the wrong way round.

Two of C's key entries do not survive checking and are not used as
printed: entry 66 gives a letter for a grid-in item (the equation has no
real solution for `b = 26`), and entry 105 gives 13 where the printed
equation yields 12. `tools/gen_book.py` is fed the checked values.

## Answers

B publishes no key of its own. Those answers are solved in
`tools/answers_b.py`; `tools/verify_b.py` machine-checks the 72 that
reduce to an equation sympy can confirm, and all 72 agree. Two remain
open and print as `—` rather than a guess: one system whose solution is
not a clean value, and one figure whose angle labels are unreadable in
the scan.

## Deduplication

`tools/dedupe.py` compares problems three ways and reports what it finds:

* **exact duplicates** — normalised stems that match. Dropped.
* **same-template groups** — identical wording, different numbers.
  4 groups, all kept: different numbers make a different problem.
* **high-similarity pairs** (≥ 0.90) flagged for a human read.

## Layout

Hard questions need working room, so the page is single column and
carries at most three problems, with the slack between them handed to
the student. Each problem is wrapped in a `minipage` so a stem is never
stranded from its answer choices across a page break, and every figure
is wrapped in `adjustbox`+`varwidth` so it scales into the measure.

## Plain-text edition

`tools/gen_txt.py` flattens the LaTeX in the bank into readable ASCII —
fractions become `a/b`, radicals `sqrt(...)`, display maths gets its own
indented line — and writes the same 294 problems and the full key as a
78-column text file. Figures are the one thing it cannot carry; those
items are marked and refer back to the PDF.

## Build

```bash
pip install pymupdf pillow sympy
apt-get install -y texlive-latex-recommended texlive-latex-extra \
                   texlive-science texlive-pictures texlive-fonts-recommended \
                   lmodern latexmk

tools/build.sh        # assets -> dedupe -> generate -> typeset -> dist/
```

## Tree

```
content/bank_a.json    the 70-question source, transcribed
content/bank_b.json    the 150-question source, transcribed
content/bank_c.json    the PrepPros Course #2 additions
content/book.json      generated: the merged, deduplicated bank
book/satmath.sty       the design system
book/figures.tex       29 TikZ figures and tables
book/main.tex          the edition
book/frontmatter/      the cover
book/assets/           the emblem, solid and at 20% alpha
tools/gen_txt.py       the plain-text edition
tools/                 assets, answers, verify, dedupe, generator, build
```

Content lives in the JSON banks; the `.tex` under `book/generated/` is
produced by `tools/gen_book.py` and should never be hand-edited.
