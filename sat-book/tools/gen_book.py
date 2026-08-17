#!/usr/bin/env python3
"""JSON -> LaTeX for the combined hard-question workbook.

Layout rule that drives everything here: these are hard questions, so at
most THREE problems are set on a page and the leftover height is handed
to the student as working space.
"""
import json, pathlib, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
BOOK = HERE / "content/book.json"
OUT = HERE / "book/generated"

PER_PAGE = 3
PER_ROW = 6      # answer-key pairs per row

DOMAINS = [
    ("ALG", "Algebra"),
    ("AM", "Advanced Math"),
    ("PSDA", "Problem-Solving and Data Analysis"),
    ("GT", "Geometry and Trigonometry"),
]

FIGMACRO = {
    "circle-oabc": r"\figcircleoabc", "tbl-cyl-ab": r"\figtblcylab",
    "tbl-bacteria": r"\figtblbacteria", "tbl-freq-ab": r"\figtblfreqab",
    "fig-parallel-pqr": r"\figparallelpqr", "fig-bowtie": r"\figbowtie",
    "fig-triangle-pqrs": r"\figtrianglepqrs", "fig-line-g": r"\figlineg",
    "tbl-cyl-jk": r"\figtblcyljk", "fig-nested-rect": r"\fignestedrect",
    "fig-right-tri-60": r"\figrighttrisixty", "tbl-basketball": r"\figtblbasketball",
    "tbl-samples": r"\figtblsamples", "tbl-gx": r"\figtblgx",
    "fig-parallel-ab": r"\figparallelab", "tbl-fx-quad": r"\figtblfxquad",
    "fig-circle-abcd": r"\figcircleabcd", "tbl-rect-sim": r"\figtblrectsim",
    "fig-parallel-abcde": r"\figparallelabcde", "tbl-freq-choice": r"\figtblfreqchoice",
    "fig-lines-abk": r"\figlinesabk", "fig-circle-arc": r"\figcirclearc",
    "fig-expdecay": r"\figexpdecay", "fig-circle-abcd2": r"\figcircleabcdii",
    "fig-parallel-abcde2": r"\figparallelabcdeii", "fig-bowtie2": r"\figbowtieii",
    "fig-bowtie3": r"\figbowtieiii", "fig-line-a2": r"\figlineaii",
    "fig-righttri-xyz": r"\figrighttrixyz",
}

NOT_TO_SCALE = {"fig-circle-abcd2", "fig-parallel-abcde2", "fig-bowtie2",
                "fig-bowtie3", "fig-righttri-xyz", "fig-right-tri-60", "fig-parallel-ab", "fig-circle-abcd",
                "fig-parallel-abcde", "fig-lines-abk", "fig-nested-rect"}


def render_problem(p, number):
    out = [r"\noindent\begin{minipage}{\linewidth}",
           r"\satmarker{%d}\par\smallskip" % number,
           p["stem"]]
    if fig := p.get("figure"):
        out.append(r"\satfig{%s}" % FIGMACRO[fig])
        if fig in NOT_TO_SCALE:
            out.append(r"\satnotetoscale")
    if p["choices"]:
        out.append(r"\begin{satchoices}")
        for letter, choice in zip("ABCD", p["choices"]):
            out.append(r"  \item[%s)] %s" % (letter, choice))
        out.append(r"\end{satchoices}")
    out.append(r"\end{minipage}")
    return "\n".join(out)


def emit_problems(problems, path):
    """Three problems a page; the slack between them is working space."""
    lines = []
    for domain, title in DOMAINS:
        group = [p for p in problems if p["domain"] == domain]
        if not group:
            continue
        lines.append(r"\satpart{%d}{%s}" % (DOMAINS.index((domain, title)) + 1, title))
        lines.append(r"\addcontentsline{toc}{section}{%s}" % title)
        for i, p in enumerate(group):
            if i and i % PER_PAGE == 0:
                lines.append(r"\clearpage")
            lines.append(render_problem(p, p["book_n"]))
            lines.append(r"\vfill")
        lines.append(r"\clearpage")
    path.write_text("\n".join(lines) + "\n")


def emit_key(problems, path):
    """Six number/answer pairs a row, banded so the eye can find a row
    again after crossing the page. The watermark goes quiet here: a
    20% emblem under a packed table is noise, not identity."""
    lines = [r"\clearpage", r"\satquietpages", r"\satlesson{Answer Key}",
             r"\noindent{\footnotesize Answers marked \textemdash\ are the "
             r"handful that could not be pinned down from the source page, "
             r"and are left open rather than guessed.}\par"]
    for domain, title in DOMAINS:
        group = [p for p in problems if p["domain"] == domain]
        if not group:
            continue
        lines.append(r"\satkeyhead{%s}" % title)
        lines.append(r"\begingroup\setlength{\tabcolsep}{0pt}"
                     r"\renewcommand{\arraystretch}{1.45}")
        lines.append(r"\rowcolors{1}{}{satband}")
        lines.append(r"\noindent\begin{tabular}{@{}" + "l" * PER_ROW + r"@{}}")
        row = []
        for p in group:
            row.append(r"\satkeycell{%d}{%s}"
                       % (p["book_n"], p.get("answer") or r"\textemdash"))
            if len(row) == PER_ROW:
                lines.append(" & ".join(row) + r" \\")
                row = []
        if row:
            lines.append(" & ".join(row + [r"\satkeyblank"] * (PER_ROW - len(row))) + r" \\")
        lines.append(r"\end{tabular}\endgroup\par")
    path.write_text("\n".join(lines) + "\n")


def main():
    problems = json.loads(BOOK.read_text())["problems"]

    # renumber 1..N in the book's own domain order
    ordered = []
    for domain, _ in DOMAINS:
        ordered += [p for p in problems if p["domain"] == domain]
    for i, p in enumerate(ordered, 1):
        p["book_n"] = i

    OUT.mkdir(parents=True, exist_ok=True)
    emit_problems(ordered, OUT / "problems.tex")
    emit_key(ordered, OUT / "answerkey.tex")

    counts = {d: sum(1 for p in ordered if p["domain"] == d) for d, _ in DOMAINS}
    with_key = sum(1 for p in ordered if p.get("answer"))
    stats = (r"\textbf{%d} hard problems, deduplicated from three sources\\[2pt]"
             r"Algebra %d \quad Advanced Math %d \quad "
             r"Data Analysis %d \quad Geometry \& Trigonometry %d\\[2pt]"
             r"Three problems per page, with working space") % (
        len(ordered), counts["ALG"], counts["AM"], counts["PSDA"], counts["GT"])
    (OUT / "stats.tex").write_text(stats + "\n")

    print(f"problems: {len(ordered)}  {counts}")
    print(f"pages of problems: ~{sum(-(-counts[d] // PER_PAGE) for d, _ in DOMAINS)}")
    print(f"answers published: {with_key}/{len(ordered)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
