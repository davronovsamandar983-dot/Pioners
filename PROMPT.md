# Build prompt — "SAT DAVLAT" mathematics workbook

This is a complete, self-contained brief for producing a Digital-SAT mathematics
workbook in the **SAT DAVLAT** house style. It specifies the design down to
individual point measurements, the asset pipeline, the content architecture and
the correctness gates.

**It deliberately does NOT specify the topics.** The topic list is an input you
must be given (or must ask for). Everything else here is fixed.

---

## 0. What you are building

Two PDFs generated from one source of truth:

| Output | Contents |
| --- | --- |
| `dist/<Name>.pdf` | full edition — lesson, problems, worked solutions, answer key |
| `dist/<Name>-Problems.pdf` | problem edition — the same questions, answer key, **nothing else** |

Both are produced by the same build so they can never drift apart.

**The shape of the content**

* `T` topics (supplied to you — see §1).
* Every topic carries **exactly 44 problems**, split into two modules of 22.
* **Module 1 is numbered 1–22. Module 2 restarts its numbering at 1** and runs
  1–22 again. This is not a typo — it mirrors how the adaptive test presents a
  second module, and it applies to the problem pages, the worked solutions and
  the answer key alike.
* Total problems = `T × 44`. State this number on the cover.

---

## 1. What you must be told before starting

Ask for these if they are not supplied:

1. **The topic list** — the ordered topics, each with a title and the domain it
   belongs to. Do not invent it, and do not silently substitute your own.
2. **The instructor / brand name** for the header and cover.
3. Whether an author photograph exists for the cover panel (if not, the emblem
   is used instead).

Everything below is fixed and needs no further input.

---

## 2. Assets — the two PNG logos

The identity rests on one circular emblem: concentric orbital rings with nodes,
an abstract knot at the centre, `SAT` set along the top arc and the instructor
name along the bottom arc.

Two files live in `book/assets/`:

| File | Pixels | Mode | Stroke RGBA | Role |
| --- | --- | --- | --- | --- |
| `logo.png` | 1250 × 1260 | RGBA | `(0, 24, 86, 255)` | solid emblem — header bar, cover panel |
| `logo-watermark.png` | 1250 × 1260 | RGBA | `(0, 30, 87, 51)` | same art at **alpha 51/255 ≈ 20 %** — page watermark, cover, part pages |

Both must be **RGBA with a real alpha channel**. Never place the emblem on an
opaque white square: it sits over navy on the cover and over body text on every
page, and a white box would be visible in both places.

The faint variant is *not* produced by setting opacity at draw time — it is a
second file baked at 20 % alpha. Over white it resolves to roughly `#CDD3DE`,
which is the grey you should see in a rendered page.

### 2.1 Extracting the emblem from an existing PDF

If you are handed a reference PDF rather than image files, the emblem is
probably embedded as a raster with a separate soft mask. Recover it:

```bash
pdfimages -list reference.pdf          # find the image and its smask object
pdfimages -png -f 4 -l 4 reference.pdf out    # extract page 4's images
```

`pdfimages` writes the colour image and its soft mask as *separate* files. Merge
them, then trim the transparent border:

```python
from PIL import Image
base = Image.open("out-000.png").convert("RGB")   # the colour image
mask = Image.open("out-001.png").convert("L")     # its smask, same dimensions
base.putalpha(mask)
base.crop(mask.getbbox()).save("logo.png")
```

Do the same for the faint instance to get `logo-watermark.png`. Sample a stroke
pixel afterwards and check the alpha matches the table above.

### 2.2 Where each asset is used

| Placement | Asset | Size |
| --- | --- | --- |
| header bar, right cell | `logo.png` | height `15pt` |
| cover author panel | `logo.png` | height `44pt` |
| cover, across the gold band | `logo-watermark.png` | width `333pt` |
| part divider page | `logo-watermark.png` | width `0.56\paperwidth` |
| every body page, centred | `logo-watermark.png` | width `0.56\paperwidth` |

---

## 3. Palette

Sample these exactly; do not approximate.

| Token | Hex | Used for |
| --- | --- | --- |
| `satnavy` | `#0A2463` | cover field, header rules, headings, emblem disc |
| `satnavyd` | `#082260` | cover shading |
| `satblue` | `#1A4E9D` | question-number markers, the `DAVLAT` wordmark, part rule |
| `satgold` | `#C8A434` | series line, cover band, `MUNDARIJA` label |
| `satpale` | `#D6E4FA` | author panel, tinted teaching boxes |
| `satmist` | `#CDD3DE` | the watermark as it renders on white |
| `satgrey` | `#5A6672` | secondary text |
| `satline` | `#B9C4D6` | hairline borders |

---

## 4. Page setup

* `\documentclass[11pt,openany]{book}` — **`openany`**: never force a chapter
  onto an odd page, and never emit a blank verso. Use `\clearpage`, never
  `\cleardoublepage`.
* Font: **Latin Modern** (`lmodern`), the default LaTeX roman. Do not substitute
  a sans or a commercial serif — the reference is set in Latin Modern and any
  other face reads as a different book.
* Geometry, A4:

```latex
\usepackage[a4paper,top=100pt,bottom=54pt,left=34pt,right=34pt,
            headheight=46pt,headsep=14pt,footskip=26pt]{geometry}
```

  The text block is therefore **527 pt wide** with 34 pt side margins. `top` has
  to clear `headheight + headsep`, because the running head carries two stacked
  elements; a smaller `top` clips the instructor line off the page.

* Page number: plain, centred in the foot, `\small`, no rule, no decoration.

---

## 5. The header block

This is the signature of the design. It appears on **every body page** and has
two stacked parts.

### 5.1 The instructor line

Flush **right**, `7.6pt`, bold, `satnavy`, in the form:

```
MATH INSTRUCTOR: <NAME IN CAPITALS>
```

### 5.2 The brand bar

Directly beneath it, a **full-textwidth rectangle, 24 pt tall**, outlined in
`satnavy` at `0.8pt`. Inside, left to right:

1. **7 pt** in from the left edge: a filled `satnavy` **circle of diameter
   15 pt** containing the word `SAT` in white, bold, `6.6pt`.
2. **6 pt** to the right of that circle: the wordmark — the brand name in
   `satblue`, bold, `15pt` (e.g. `DAVLAT`).
3. A **vertical `0.8pt` navy rule 26 pt in from the right edge**, closing off a
   narrow cell.
4. Inside that cell, 6 pt from the right edge: `logo.png` at height `15pt`.

Implementation sketch:

```latex
\fancyhead[C]{%
  \hbox to \textwidth{\hfil
    \fontsize{7.6}{9}\selectfont\bfseries\color{satnavy}%
    MATH INSTRUCTOR: \satauthorname}%
  \vspace{2pt}\par
  \satbrandbar}
```

where `\satbrandbar` draws the rectangle as a single `tikzpicture` with
`minimum width=\textwidth, minimum height=24pt`.

Part-divider pages and the cover use `\thispagestyle{empty}` — no header there.

### 5.3 The watermark

Every body page carries the emblem centred behind the text:

```latex
\AddToShipoutPictureBG{%
  \begin{tikzpicture}[remember picture,overlay]
    \node at (current page.center)
      {\includegraphics[width=0.56\paperwidth]{assets/logo-watermark.png}};
  \end{tikzpicture}}
```

Use a tikz overlay anchored to `current page.center`. `eso-pic`'s `\AtPageCenter`
combined with `\raisebox` does not reliably centre the box vertically.

---

## 6. The cover

Coordinates are in points, measured from the named page corner. A4 is
595.28 × 841.89 pt.

* **Navy field** from the top of the page down to **429 pt above the foot**.
* **Gold band**: full width, from **417 pt to 429 pt above the foot** — it closes
  the navy field.
* **Emblem**: `logo-watermark.png`, width **333 pt**, centred horizontally, its
  centre **354 pt above the foot** — so the gold band crosses its upper third.
* Text, all measured from the **north-west** corner, `x = 78pt` (the large title
  sits at `75pt` to compensate for its side bearing):

| Element | y from top | Style |
| --- | --- | --- |
| `MATH EXCELLENCE SERIES` | 155 pt | `\bfseries\large`, `satgold` |
| Book title (e.g. `SAT MATH`) | 192 pt | `\fontsize{38}{42}`, white |
| Gold rule, `x` 78→208 pt | 216 pt | `1.6pt`, `satgold` |
| Subtitle (e.g. `& Complete Mastery`) | 243 pt | `\fontsize{18}{21}` bold italic, white |
| Domain line | 289 pt | `\normalsize`, white |
| Statistics block | 314 pt (top) | `\small`, white, in a 380 pt minipage |

* **Author panel**: a `satpale` rectangle from `x` **60 pt to 536 pt**, `y`
  **17 pt to 88 pt** above the foot. Inside: the name at `(78pt, 60pt)` in
  `\Large\bfseries` `satnavy`; the role at `(78pt, 38pt)` in `\small` `satgrey`;
  and at the right, `x = 518pt`, `y = 52pt`, either the author photograph
  clipped to a circle or `logo.png` at height `44pt`.
* **Foot strip**: solid `satnavy`, full width, **16 pt** tall, flush to the
  bottom edge — the author panel sits directly on it.

Keep the cover in its own file and parameterise only the subtitle and the
statistics block, so both editions share one cover source.

---

## 7. Contents page

A full-width `satnavy` block, inner padding `14pt` × `10pt`, containing two
lines: `MUNDARIJA` in `satgold`, bold, `\footnotesize`; then `Contents` in white
at `\fontsize{20}{23}`.

Below it, the table of contents in **two columns** (`columnsep 22pt`,
`\raggedcolumns`), listing **parts and lessons only**.

Lesson sub-headings must not reach the contents. Emit them as `\section*` and
add the lesson itself with an explicit
`\addcontentsline{toc}{section}{Lesson N: Title}`. If you use numbered
`\section`, the contents fills with junk entries like `0.21 Polynomials`.

---

## 8. Part divider pages

One page per domain, `\thispagestyle{empty}`, no header, no folio, and the whole
composition centred on the page:

* `logo-watermark.png` at width `0.56\paperwidth`, centred.
* `PART <n>` at **+99 pt above page centre**, `\fontsize{10}{12}`, black.
* The domain title at **+61 pt**, `\fontsize{19}{22}\bfseries`, black.
* A `satblue` rule, `1pt`, spanning **±82 pt** at **+36 pt**.

The text sits in the upper third of the emblem, not at its centre.

---

## 9. Lesson opening

Centred, no chapter number, no coloured slab:

```latex
\begin{center}
  {\fontsize{16}{19}\selectfont\bfseries Lesson N: Title}\\[3pt]
  \textcolor{satnavy}{\rule{0.30\textwidth}{0.7pt}}
\end{center}
```

Then the teaching material (full edition only), then the modules.

---

## 10. Problem pages — the core layout

### 10.1 Module heading

`Module 1` / `Module 2` in `\fontsize{13}{15}\bfseries`, flush left, black.

* Reset the question counter to 0 at every module heading.
* **Module 2 begins on a fresh page** (`\clearpage` before it). Module 1 simply
  follows the lesson.

### 10.2 Two columns

Problems are set in `multicols` with `columnsep 20pt` and `\raggedcolumns`.

### 10.3 The question marker

A small filled `satblue` rectangle carrying the number in white bold `8pt`,
`minimum width 11pt`, `inner xsep 3pt`, `inner ysep 2pt`. It sits **on its own
line above the question text**, not inline with it.

The reference prints **no difficulty label and no question-type label** on the
page. Track difficulty in the data, but do not show it.

### 10.4 Answer choices

One per line — never a 2 × 2 grid:

```latex
\begin{list}{}{%
  \setlength{\leftmargin}{22pt}\setlength{\labelwidth}{16pt}%
  \setlength{\labelsep}{5pt}\setlength{\itemsep}{4pt}%
  \setlength{\parsep}{0pt}\setlength{\topsep}{0pt}}
  \item[A)] ...
  \item[B)] ...
  \item[C)] ...
  \item[D)] ...
\end{list}
```

Student-produced-response items simply have no choices and no marker of any
kind after the stem.

### 10.5 Two rules that the layout will break without

**A problem must never split across a column break.** Wrap each complete item —
marker, figure, stem, choices — in a `minipage{\linewidth}`. `\needspace` and
`\samepage` have no effect inside `multicols`, and a stem stranded at the foot
of one column with its choices at the head of the next is unreadable.

**A figure must fit its column.** Figures are authored at full-page width but
render in a 250 pt column. Wrap them so they scale down:

```latex
\begin{adjustbox}{max width=\linewidth,center}
\begin{varwidth}{\textwidth}
  ... the figure ...
\end{varwidth}
\end{adjustbox}
```

`varwidth` is required: figure content usually contains a `center` or a
`tabular`, and `adjustbox` alone cannot box a list environment — it fails with
*"Something's wrong--perhaps a missing \item"*.

Carry `Figure not drawn to scale.` under any diagram whose drawing does not
match its given measurements.

---

## 11. Worked solutions (full edition only)

Single column. Per topic: the topic title, then `Module 1` and `Module 2`
subheadings, and under each, items numbered **1–22** — matching the printed
question numbers, not a running 1–44.

Each solution opens with the question marker, then `Answer: <value>` in bold
`satnavy`, then a numbered list of mechanical steps, then a short paragraph
explaining *why* that path is the right one.

---

## 12. Answer key

One block per topic, split under `Module 1` and `Module 2` labels in `satblue`
`\footnotesize\bfseries`. Without those labels the two 1–22 runs read as one
confusing sequence.

Eight number/answer pairs per row in a left-aligned `longtable`
(`\LTleft=0pt`, `\LTright=\fill` — a bare `longtable` centres itself).

---

## 13. Content architecture

Keep the content in data, not in LaTeX. One JSON file per topic; generate all
`.tex`; never hand-edit generated files.

```
content/topics.json          the ordered topic list (supplied to you)
content/schema.json          JSON Schema for a topic bank
content/bank/topic-NN.json   lesson + 44 problems  <- the source of truth
book/satmath.sty             the design system
book/main.tex                full edition
book/problems.tex            problem edition
book/frontmatter/cover.tex   the shared cover
book/assets/                 the two PNGs
tools/gen_book.py            JSON -> LaTeX (emits BOTH editions)
tools/validate.py            schema + structure + machine-checked answers
tools/build.sh               validate -> generate -> typeset -> dist/
```

The problem edition is the same renderer with the lesson suppressed — a
`lesson=False` flag, not a second template. Two templates drift; one does not.

### 13.1 A problem record

```jsonc
{
  "id": "T07-M1-05",       // T<topic>-M<module>-<position within the module>
  "module": 1,             // 1 for n 1..22, 2 for n 23..44
  "n": 5,                  // 1..44, unique within the topic
  "difficulty": "E",       // E | M | H  -- tracked, never printed
  "type": "MC",            // MC (four choices) | SPR (grid-in)
  "skill": "Factoring",
  "stem": "What is the sum of the solutions to $x^2-7x+12=0$?",
  "choices": ["$3$", "$4$", "$7$", "$12$"],
  "answer": "C",           // A-D for MC; the literal value for SPR
  "accepted": ["7.0"],     // optional alternative correct SPR forms
  "figure": "...",         // optional TikZ / pgfplots / tabular
  "wide": true,            // optional: sentence-length choices
  "form": true,            // optional: see §14
  "solution": "...",
  "steps": ["...", "..."],
  "verify": "x = symbols('x')\nresult = sum(solve(x**2-7*x+12, x))"
}
```

`n` stays 1–44 in the data; the **printed** number is `n` for Module 1 and
`n − 22` for Module 2. Do the subtraction in the renderer, not in the data.

All mathematical text is raw LaTeX inside JSON strings, so backslashes are
doubled: `"\\frac{1}{2}"`.

---

## 14. Correctness gates

The build must refuse to produce a PDF if any check fails. Three layers:

**Schema** — exactly 44 problems; the `id` pattern; MC answers restricted to
A–D; SPR items carry no choices.

**Structure** —

* a 22 / 22 module split, numbering exactly 1–44
* `id` agrees with topic number, module and position
* no two problems share a stem, **within a topic or across the whole book**
* four distinct choices per MC item
* no distractor mathematically equal to the key

and warnings for: a module that does not ramp easy → hard or does not open easy
and close hard; any answer letter exceeding 40 % of a topic's MC key; a grid-in
share far from one quarter.

**Mathematics** — every problem carries a `verify` snippet: a short Python
expression evaluated with sympy in a restricted namespace that must assign
`result`. The validator compares `result` against the correct choice's text (MC)
or against `answer` (SPR), and separately checks that no distractor equals the
key.

Three things this layer must get right, each of which is a real trap:

* **The parser must read the LaTeX the reader actually sees** — `\frac` (nested),
  `\sqrt`, `\pi`, `\cdot`, `\%`, `\$`, degree marks, `^`, and implicit
  multiplication such as `5x` or `3\sqrt{2}`. If it cannot, authors will paste a
  machine-readable duplicate into `accepted`, and the distractor-equals-key
  check then silently stops running on those items.
* **Strip thousands separators only.** A blanket comma strip turns the ordered
  pair `(4,7)` into the integer `47`.
* **A string `result` must always be compared as text**, never pushed through
  sympy — otherwise a prose answer parses into a symbol and the comparison
  becomes meaningless.

Add an audit mode that lists every problem whose `verify` merely asserts the
answer as a string literal. Those are structurally checked but mathematically
unchecked — typically interpretation items whose answer is a sentence — and each
one needs a human or model read before the book ships.

**`"form": true`** suppresses the distractor-equals-key check for a question
that is about the *form* of an expression ("which expression is equivalent",
"factored completely"), where an equal-but-differently-written distractor is the
point. It is not an escape hatch for an accidental duplicate.

---

## 15. House style for the problems

* **Difficulty per module**: roughly 7 easy, 8 medium, 7 hard, in that order.
  Each module opens easy and closes hard. Module 2 sits one band harder than
  Module 1 throughout.
* **Question mix**: about 3 in 4 multiple choice, 1 in 4 student-produced
  response — around 11 grid-ins per topic.
* **Distractors are diagnoses, not noise.** Every wrong choice must be the value
  a student actually reaches by one specific, nameable mistake — a sign slip, an
  un-distributed factor, the un-flipped inequality, the diameter used as the
  radius, solving for the wrong quantity. Say which mistake in the solution
  text. Never pad a choice list with an arbitrary number.
* **Order numeric choices ascending**, as the real test does. Balance the answer
  key by choosing which plausible-error values bracket the key, not by shuffling
  choices out of order.
* **Contexts are ordinary**: receipts, distances, temperatures, populations,
  memberships. No exotic scenarios.
* **Numbers stay clean** — integer or simple-fraction answers unless the topic is
  specifically about decimals. Grid-in answers must be a single value, never an
  interval and never a symbolic form like `25\pi`.
* **Vary the surface.** Forty-four near-identical questions with different
  numbers is not a topic. Move across bare computation, equations in context,
  reverse questions, parameter questions and interpretation.
* **Solutions teach.** `steps` is the mechanical path; `solution` is the sentence
  that explains why that path is right. A solution that only restates the
  arithmetic is not finished.

---

## 16. Copyright

Do **not** reproduce real College Board test items — they are copyrighted. Write
original problems against the published specification: the tested domains and
skills, the question formats, the multiple-choice / grid-in ratio, the
difficulty distribution and the characteristic question shapes. The result
should feel like the real test without copying from it.

---

## 17. Build

```bash
pip install sympy jsonschema pillow
apt-get install -y texlive-latex-recommended texlive-latex-extra \
                   texlive-science texlive-pictures texlive-fonts-recommended \
                   lmodern latexmk poppler-utils

tools/build.sh              # validate -> generate -> typeset both editions
tools/build.sh --no-check   # skip validation, fast preview
tools/build.sh --strict     # every problem must carry a verify snippet
```

Required LaTeX packages: `geometry`, `lmodern`, `amsmath`, `amssymb`, `xcolor`,
`graphicx`, `adjustbox`, `varwidth`, `tikz`, `pgfplots`, `tcolorbox`, `enumitem`,
`fancyhdr`, `titlesec`, `multicol`, `array`, `booktabs`, `longtable`,
`needspace`, `etoolbox`, `eso-pic`, `hyperref`.

**Typeset into a scratch directory** (`-outdir=.build`). Two pdflatex runs in one
directory overwrite each other's `.aux`, and the second dies on a half-written
file — which matters as soon as anything builds in parallel.

Run pdflatex **three times**: the tikz overlays anchored to `current page` need a
second pass to position, and the contents needs a third to settle.

---

## 18. Verify before you ship

1. `tools/validate.py` reports **0 errors and 0 warnings**, and *every* problem
   verified.
2. Both PDFs typeset with no `!` in the log.
3. **Render pages to PNG and look at them** (`pdftoppm -png -r 80`). Check the
   cover, the contents, a part divider, a lesson opening, a Module 1 page, a
   Module 2 opening, a solutions page and the answer key. Layout faults —
   clipped headers, split problems, figures overrunning a column, a watermark
   off centre — do not appear in the log. They only appear in the picture.
