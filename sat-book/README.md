# SAT Math — 220 Hard Questions

One workbook merged from two hard-question collections, deduplicated,
regrouped by the four tested SAT domains, and set **three problems to a
page** so there is room to work.

| | |
| --- | --- |
| Output | `dist/SAT-Math-220-Hard-Questions.pdf` — 83 pages |
| Problems | 220 |
| Algebra | 31 |
| Advanced Math | 90 |
| Problem-Solving and Data Analysis | 35 |
| Geometry and Trigonometry | 64 |

## Sources

| Tag | Collection | Problems | Answer key |
| --- | --- | --- | --- |
| A | *Collection of 70 HARD SAT Math questions* — Merey Altaiuly | 70 | yes |
| B | *Advanced Digital SAT Math, 150 Hard Questions* — M. & M. Stroup | 150 | **no** |

The 150-question source publishes no answers of its own; they are solved
in `tools/answers_b.py` and machine-checked by `tools/verify_b.py`
(72 of them reduce to an equation sympy can confirm). Four could not be
pinned down from the source page and print as `—` rather than a guess.

Both PDFs had to be transcribed by reading the rendered pages: A is a
scan with no text layer at all, and B's text layer has a broken font
encoding that turns every variable into punctuation.

## Deduplication

`tools/dedupe.py` compares problems three ways and reports what it finds:

* **exact duplicates** — normalised stems that match. **0 found**; the
  two collections do not overlap.
* **same-template groups** — identical wording, different numbers.
  4 groups. Kept: different numbers make a different problem to solve.
* **high-similarity pairs** (≥ 0.90) flagged for a human read. 7 pairs,
  all of them the same-template case above.

## Layout

Hard questions need working room, so the page is single column and
carries at most three problems, with the slack between them handed to
the student. Each problem is wrapped in a `minipage` so a stem is never
stranded from its answer choices across a page break, and every figure
is wrapped in `adjustbox`+`varwidth` so it scales into the measure.

## Build

```bash
pip install pymupdf pillow
apt-get install -y texlive-latex-recommended texlive-latex-extra \
                   texlive-science texlive-pictures texlive-fonts-recommended \
                   lmodern latexmk

tools/build.sh        # assets -> dedupe -> generate -> typeset -> dist/
```

## Layout

```
content/bank_a.json    the 70-question source, transcribed
content/bank_b.json    the 150-question source, transcribed
content/book.json      generated: the merged, deduplicated bank
book/satmath.sty       the design system
book/figures.tex       22 TikZ figures and tables
book/main.tex          the edition
book/frontmatter/      the cover
book/assets/           the emblem, solid and at 20% alpha
tools/                 assets, dedupe, generator, build
```

Content lives in the JSON banks; the `.tex` under `book/generated/` is
produced by `tools/gen_book.py` and should never be hand-edited.
