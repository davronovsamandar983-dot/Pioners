# SAT Math Mastery

A complete Digital SAT mathematics textbook: **20 topics × 44 problems = 880
problems**, each topic split into Module 1 (questions 1–22) and Module 2
(questions 23–44), with a full lesson and a worked solution for every question.

## Build

```bash
pip install sympy jsonschema
apt-get install -y texlive-latex-recommended texlive-latex-extra \
                   texlive-science texlive-pictures texlive-fonts-recommended \
                   lmodern latexmk

tools/build.sh            # validate → generate LaTeX → typeset → dist/
tools/build.sh --no-check # skip validation (fast preview)
tools/build.sh --strict   # every problem must carry a `verify` snippet
```

The PDF lands at `dist/SAT-Math-Mastery.pdf`.

## Layout

| Path | What it is |
| --- | --- |
| `content/topics.json` | the ordered list of the 20 topics and their official skills |
| `content/schema.json` | JSON Schema every topic bank is validated against |
| `content/bank/topic-NN.json` | **the source of truth** — lesson + 44 problems for one topic |
| `book/satmath.sty` | the design system (palette, boxes, problem/solution layout) |
| `book/main.tex` | document skeleton and title page |
| `book/frontmatter/` | hand-written front matter |
| `tools/gen_book.py` | JSON → LaTeX |
| `tools/validate.py` | schema + structure + **machine-verified answers** |
| `tools/build.sh` | the whole pipeline |

`book/topics/`, `book/solutions/` and `book/generated/` are build products and
are git-ignored. **Never edit the generated `.tex` — edit the JSON.**

## Correctness

`tools/validate.py` runs three layers of checking:

1. **Schema** — exactly 44 problems, id pattern, MCQ answers restricted to
   A–D, student-produced-response items carry no choices.
2. **Structure** — a 22/22 module split, contiguous numbering 1–44, ids that
   agree with their topic/module/position, no duplicate stems, a difficulty
   ramp inside each module, and a balanced answer key.
3. **Mathematics** — every problem carries a `verify` snippet evaluated with
   sympy; its `result` must match the stated answer. Distractors are also
   checked so that none of them is secretly equal to the key.

A topic that fails any layer will not build under `tools/build.sh`.

See [AUTHORING.md](AUTHORING.md) for how to write a topic bank.
