# Authoring a topic bank

One file per topic: `content/bank/topic-NN.json`. It holds the lesson and all
44 problems. Nothing else in the book is written by hand.

## Skeleton

```jsonc
{
  "number": 7,
  "topic": "Quadratic Equations",
  "domain": "Advanced Math",
  "skills": ["Factoring and the quadratic formula", "The discriminant"],

  "lesson": {
    "intro": "One paragraph that says what the topic is and why the test cares.",
    "blocks": [
      { "kind": "section", "title": "Solving by factoring", "body": "..." },
      { "kind": "concept",  "title": "Key idea",            "body": "..." },
      { "kind": "formula",  "title": "Formulas you must know", "body": "..." },
      { "kind": "trap",     "title": "Common trap",         "body": "..." },
      { "kind": "strategy", "title": "Calculator / strategy","body": "..." },
      { "kind": "worked",   "title": "Worked example",      "body": "..." }
    ]
  },

  "problems": [ /* exactly 44 */ ]
}
```

`body` and every problem field are **raw LaTeX**. Write `$3x+5=14$`, not
`3x+5=14`.

## A problem

```jsonc
{
  "id": "T07-M1-05",         // T<topic>-M<module>-<position in module>
  "module": 1,               // 1 for n 1..22, 2 for n 23..44
  "n": 5,                    // 1..44, unique within the topic
  "difficulty": "E",         // E | M | H
  "type": "MC",              // MC (four choices) | SPR (grid-in)
  "skill": "Factoring",
  "stem": "What is the sum of the solutions to $x^2-7x+12=0$?",
  "choices": ["$3$", "$4$", "$7$", "$12$"],
  "answer": "C",             // A-D for MC; the literal value for SPR
  "accepted": ["7.0"],       // optional extra accepted SPR forms
  "solution": "By Vieta's formulas the sum of the roots is $-b/a = 7$.",
  "steps": ["Identify $a=1$, $b=-7$.", "The sum of the roots is $-b/a$."],
  "verify": "x = symbols('x')\nresult = sum(solve(x**2-7*x+12, x))"
}
```

Add `"figure": "\\begin{center}...\\end{center}"` for a TikZ or pgfplots
diagram, and `"wide": true` when a choice is too long for the two-column
layout.

## The `verify` field

Every problem must carry one. It is a short Python snippet run with sympy in a
restricted namespace; it must assign `result`. The validator compares `result`
against the correct choice's text (for `MC`) or against `answer` (for `SPR`),
and it also checks that no distractor equals the key.

Available names: `sp`, `S`, `Rational`, `sqrt`, `pi`, `symbols`, `solve`,
`simplify`, `Eq`, `nsimplify`, `expand`, `factor`, `Abs`, `log`, `exp`, `sin`,
`cos`, `tan`, `Matrix`, `binomial`, plus `range len sum abs min max sorted list
float int round`. `import`, `open`, `exec`, `eval` and dunders are rejected.

For a question whose answer is not a number (an interpretation question, say),
make `result` a Python **string** holding the correct choice:

```python
result = "The slope of the line of best fit"
```

A string `result` is always compared as text — never through sympy — ignoring
case, surrounding whitespace, `$` delimiters and a trailing full stop. You do
not need to punctuate a sentence a particular way to make this work.

The comparison of a non-string `result` understands the LaTeX the book
actually renders: `\frac` (nested), `\sqrt`, `\pi`, `\cdot`, `\%`, `^`, and
implicit multiplication such as `5x` or `3\sqrt{2}`. Write the choice the way
the reader should see it; do not add a machine-readable copy in `accepted`
just to get it to parse. Use `accepted` only for genuinely alternative correct
forms of an SPR answer (`0.5` and `1/2`).

### Questions about form, not value

A "which expression is equivalent" or "factored completely" or "which form
displays the vertex as a constant" question deliberately offers a distractor
that is *mathematically equal* to the key but written the wrong way. Mark such
a problem `"form": true` so the distractor-equals-key check is suppressed for
it. Do not use this flag to excuse an accidental duplicate answer.

## Rules the validator enforces

* exactly 44 problems, numbered 1–44, split 22 in Module 1 and 22 in Module 2
* `id` must agree with the topic number, module and position
* no two problems in a topic may share a stem
* MCQ choices must be four distinct strings
* no distractor may be mathematically equal to the key

and it warns when:

* a module does not ramp from easy to hard, or does not open easy / close hard
* one answer letter takes more than 40% of the topic's MCQ key
* the topic has far fewer or more than about a quarter grid-in questions

## House style

* **Difficulty mix per module**: roughly 7 easy, 8 medium, 7 hard, in that
  order. Module 2 sits a band harder than Module 1 throughout.
* **Question types**: about 3 in 4 multiple choice, 1 in 4 student-produced
  response — the ratio the real test uses.
* **Context**: keep word problems short and concrete. The SAT does not use
  exotic scenarios; it uses receipts, distances, temperatures, populations.
* **Solutions teach.** Use `steps` for the mechanical path and `solution` for
  the sentence that explains *why* that path is the right one. A solution that
  only restates the arithmetic is not finished.
* **Numbers stay clean.** Answers should be integers or simple fractions
  unless the topic is specifically about decimals.
