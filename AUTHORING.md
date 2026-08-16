# Authoring contract — SAT Math Mastery

Every topic in this book is written to the same contract so that 20 topics
written independently read as one textbook. Read all of it before writing a
single question.

Repo root: `/home/user/Pioners`

## What one topic consists of

| File | Contents |
| --- | --- |
| `book/topics/NN-slug.tex` | the topic: opener, Essentials box, Module 1 (22 questions), Module 2 (22 questions) |
| `book/answers/NN-slug.tex` | the topic's answer key: 44 worked `\ans` entries |
| `data/NN-slug.json` | machine-readable manifest of all 44 answers, used by the sympy verifier |

`NN` is the zero-padded topic number. The three files share one slug.
No topic file contains a preamble, `\documentclass`, or `\begin{document}`.

## Skeleton of `book/topics/NN-slug.tex`

```latex
\settopicname{Linear Equations in One Variable}
\chapter{Linear Equations in One Variable}
\topicopen{Algebra}{One-sentence statement of what the testing point asks
for, in College Board's own framing.}

\begin{essentials}
The complete toolkit for this topic: the forms, the moves, the special
cases. 90--150 words. No question in the topic may need anything that is
not here. Display math is fine.
\end{essentials}

\modulehead{Module 1}{Questions 1--22}
\begin{multicols*}{2}

\qfr{Student-produced response question.}

\question{Multiple-choice question stem?
\choices{\item $6$ \item $7$ \item $8$ \item $9$}}

% ... 22 questions total ...

\end{multicols*}

\modulehead{Module 2}{Questions 1--22}
\begin{multicols*}{2}

% ... 22 more questions, numbering restarts at 1 automatically ...

\end{multicols*}
```

`\modulehead` resets the question counter, so Module 2 starts at 1 by itself.
Never number questions by hand.

## Macros you may use — and only these

| Macro | Use |
| --- | --- |
| `\question{...}` | a multiple-choice question (put `\choices` inside the braces) |
| `\qfr{...}` | a student-produced response question; the Work Space box is added for you |
| `\choices{\item A \item B \item C \item D}` | the four options, in order |
| `\begin{essentials}...\end{essentials}` | the topic's toolkit box, exactly once |
| `\modulehead{Module 1}{Questions 1--22}` | module divider |
| `\topicopen{Domain}{blurb}` | under the chapter title |
| `\settopicname{...}` | sets the running footer |
| `\akhead{...}`, `\ans{mod}{n}{answer}{reasoning}` | answer-key file only |
| `\dfrac`, `\begin{cases}`, `\[...\]`, `$...$` | mathematics |
| `tikzpicture` | figures — see the figures section below |

A question is an atomic box: it can never be split across columns. Keep each
question short enough to fit in one column (roughly 12 lines of text at most,
including choices and the Work Space box).

## Hard rules

- Exactly **22** questions in Module 1 and **22** in Module 2. Not 21, not 23.
- Never write `(Enter your response.)`, `(Enter your answer.)`, `SAT Takers`,
  `Quick Reference`, `Key Concept`, or a Vocabulary list. The checker rejects
  these strings.
- Never re-draw the page banner in the body — it repeats from the preamble.
- A long expression must never sit inside a running sentence where LaTeX can
  break it mid-expression. Put it on its own display line:
  ```latex
  \question{Which expression is equivalent to
  \[ (3x^3 - x^2 + 4)(5x^2 + 8x)\,? \]
  \choices{...}}
  ```
  Apply this to every "which expression is equivalent to" question.
- A tall or nested `\dfrac` must not open a question inline next to the badge
  — it collides with the badge. Break it into `\[ ... \]`.
- Use `\dfrac`, not `\frac`, in display context.
- Use `\begin{cases}` for systems, never hand-aligned lines.
- Escape `$` in currency as `\$`, and `%` as `\%`.

## Question design

**Format mix per topic (44 questions):** roughly 30 multiple-choice
(`\question`) and 14 student-produced response (`\qfr`). The real section is
about 75% multiple choice; match that. Student-produced response answers must
be a single number — never negative-plus-fraction combinations the format
cannot accept, and never an answer that requires rounding an exact value.

**Difficulty ladder.** This is the part that makes it a textbook rather than
a question dump:

- Module 1 Q1–Q8: **easy.** One step, numbers chosen to stay clean.
- Module 1 Q9–Q17: **medium.** Two steps, or one step with a context to parse.
- Module 1 Q18–Q22: **hard** relative to Module 1 — the first questions that
  ask for a constant, a condition, or an interpretation.
- Module 2 Q1–Q6: **medium.** Restart gently, but above where Module 1 began.
- Module 2 Q7–Q15: **medium**, tightening; abstract constants appear routinely.
- Module 2 Q16–Q22: **hard.** Multi-step, parameters rather than numbers,
  "for what value of $k$", "which must be true", edge cases.

Every question's `difficulty` in the manifest must reflect this, and the
ladder must climb — the structure checker flags a topic whose difficulty
wanders backwards.

**Progression is cumulative.** Question 12 may rely on the idea introduced at
question 5. That is the point: a student working straight through is being
taught, not sampled. Do not repeat the same problem with different numbers —
44 questions means 44 distinct ideas, contexts, or twists.

**Question types to rotate through:**
1. Solve for a value.
2. Multiple choice with four plausible options — every distractor must be the
   result of a *specific* believable error (sign slip, inverted fraction,
   forgetting to distribute), never a random number.
3. Word problem in a real context (cost, distance, population, dosage, area).
4. Table or graph interpretation — "what does the value 12 represent".
5. Condition questions — no solution, infinitely many solutions, one solution.
6. "Which of the following" — identify the equivalent expression or equation.

**SAT language patterns to use verbatim:**
- "In the given equation, $k$ is a constant."
- "Which of the following could be the value of ...?"
- "What is the best interpretation of ... in this context?"
- "The function $f$ is defined by $f(x) = \ldots$"
- "Which equation correctly expresses $x$ in terms of $y$?"
- "Which statement must be true?"

Contexts must be neutral and self-contained: no named real people, no real
companies, no assumed cultural knowledge. Units always stated.

## Figures

Some topics need them (geometry, scatterplots, right triangles). Draw with
`tikzpicture` inside the question's braces. Keep a figure under 4 cm tall and
under `\columnwidth` wide, and label it so the question is answerable from the
labels alone — never rely on the drawing being to scale. State
"Note: figure not drawn to scale." when it is not.

```latex
\question{In the figure, $\ol{AB}\parallel\ol{CD}$.
\begin{center}
\begin{tikzpicture}[scale=0.8, line width=0.7pt]
  \draw (0,0) -- (3,0) node[right]{$B$};
  ...
\end{tikzpicture}
\end{center}
What is the value of $x$?}
```

## The answer key — `book/answers/NN-slug.tex`

```latex
\akhead{Topic 1 — Linear Equations in One Variable}
\ans{1}{1}{$x=7$}{Add 7 to both sides: $3x=21$, so $x=7$.}
\ans{1}{2}{B}{Multiply by 3: $2x+1=15$, so $x=7$.}
...
\ans{2}{22}{$k=-4$}{The equation has no solution when the coefficients of
$x$ match but the constants do not, so $k=-4$.}
```

44 entries, in order: `\ans{1}{1}` through `\ans{1}{22}`, then `\ans{2}{1}`
through `\ans{2}{22}`. For multiple choice the third argument is the **letter**;
for a student-produced response it is the **value**. The fourth argument is
the reasoning that produces it — one or two sentences, the actual method, not
a restatement. A student who got it wrong must be able to see where.

## The manifest — `data/NN-slug.json`

```json
{
  "topic": 1,
  "slug": "01-linear-equations-one-variable",
  "title": "Linear Equations in One Variable",
  "domain": "Algebra",
  "questions": [
    {
      "module": 1, "n": 1, "type": "fr", "difficulty": "easy",
      "answer": "7", "answer_kind": "number",
      "check": {"kind": "solve", "expr": "3*x - 7 - 14", "var": "x"}
    },
    {
      "module": 1, "n": 2, "type": "mc", "difficulty": "easy",
      "answer": "7", "answer_kind": "number",
      "choices": ["6", "7", "8", "9"], "choice": "B",
      "check": {"kind": "solve", "expr": "(2*x+1)/3 - 5", "var": "x"}
    }
  ]
}
```

44 entries in the same order as the LaTeX. `type` must match what the LaTeX
renders (`mc` if the question contains `\choices`, else `fr`) — the checker
compares them and fails on a mismatch.

Available `check` kinds:

| kind | fields | meaning |
| --- | --- | --- |
| `solve` | `expr`, `var`, optional `all: true` | `expr = 0`; the answer must be a root (with `all`, the answer lists every root, comma-separated) |
| `system` | `exprs`, `vars`, `want` | solve the system, compare the value of `want` |
| `evaluate` | `expr` | the answer equals this expression's value |
| `equiv` | `expr`, `other` | the two expressions are identically equal |
| `manual` | `note` | sympy cannot express it; say why |

Write the `check` from the **question**, not from your answer — that is the
whole point. `expr` is parsed by sympy: use `**` for powers, `*` for every
multiplication, `sqrt(...)`, `pi`, `Rational(1,3)`.

Keep `manual` rare. Above 30% of a topic being `manual` is flagged. Geometry
and interpretation questions can usually still be checked with `evaluate`.
For a genuinely textual answer (an interpretation), set
`"answer_kind": "text"` and no check is required — but for multiple choice the
verifier still confirms the letter matches the option text exactly.

## Before you report done — run all three gates

```bash
cd /home/user/Pioners
bash tools/topic_preview.sh NN-slug        # must compile, 0 errors
python3 tools/check_structure.py NN        # must print 0 errors
python3 tools/verify_answers.py NN         # must print 0 problems
```

Then **look at the rendered PNGs** (`build/preview-NN-slug-*.png`) with the
Read tool. Check with your own eyes:

- the blue banner sits on top of **every** page,
- no question is cut in half across a column or page,
- no math runs off the right edge of a column,
- the Work Space boxes are intact,
- Module 2 restarts at question 1.

A topic is done when all three gates pass **and** the pages look right. Do not
report success on a topic that fails a gate — report what is failing instead.
