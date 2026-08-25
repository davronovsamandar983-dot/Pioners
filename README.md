# Pionerlar

A Digital SAT mathematics textbook, written in LaTeX and generated from a
validated JSON problem bank.

## Where the work actually is

`main` holds only this README. Every draft of the book lives on its own
branch, none of them merged:

| Branch | What it holds |
| --- | --- |
| [`claude/sat-math-textbook-880`](../../tree/claude/sat-math-textbook-880-7ot0t4) | The fullest version — 20 topics × 44 problems, the JSON bank, the build pipeline and two built PDFs in `dist/` |
| [`claude/sat-math-mastery-book`](../../tree/claude/sat-math-mastery-book-ppnwy8) | An earlier cut with per-topic answer files under `book/answers/` |
| [`claude/sat-combined-questions`](../../tree/claude/sat-combined-questions-bffgc2) | A combined-questions variant, nested under `sat-book/` |

Start with `claude/sat-math-textbook-880` — it is the one with the build
tooling and the machine-checked answers.

## The idea

880 problems: 20 topics, 44 problems each, split into Module 1 (questions
1–22) and Module 2 (questions 23–44) to mirror the adaptive structure of the
Digital SAT. Every question carries a full worked solution.

The problems are **not** written in LaTeX by hand. Each topic is a JSON file
under `content/bank/`, validated against a schema, and turned into LaTeX by
`tools/gen_book.py`. The generated `.tex` is a build product — edit the JSON.

## Why it is generated

Validation is the point. `tools/validate.py` checks three layers before
anything typesets:

1. **Schema** — exactly 44 problems, ids in the right pattern, multiple-choice
   answers restricted to A–D.
2. **Structure** — a 22/22 module split, contiguous numbering, a difficulty
   ramp within each module, a balanced answer key, no duplicate stems.
3. **Mathematics** — every problem carries a `verify` snippet evaluated with
   sympy, and its result must match the stated answer. Distractors are checked
   too, so none of them is accidentally also correct.

A topic that fails any layer will not build. For an 880-problem book that is
the difference between a usable text and a liability.

## Building

On the textbook branch:

```bash
tools/build.sh
```

The PDF lands in `dist/`. See that branch's `README.md` and `AUTHORING.md`
for prerequisites and for how to write a new topic bank.
