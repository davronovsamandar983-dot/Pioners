#!/usr/bin/env python3
"""Plain-text edition of the workbook.

The bank stores stems as LaTeX, so the maths has to be flattened into
something readable in a terminal or a notes app: fractions become a/b,
radicals become sqrt(...), and the display-maths delimiters become their
own indented line.
"""
import json, re, pathlib, textwrap, sys

HERE = pathlib.Path(__file__).resolve().parent.parent
BOOK = HERE / "content/book.json"
OUT = HERE / "dist/SAT-Math-294-Hard-Questions.txt"
WIDTH = 78

DOMAINS = [("ALG", "ALGEBRA"), ("AM", "ADVANCED MATH"),
           ("PSDA", "PROBLEM-SOLVING AND DATA ANALYSIS"),
           ("GT", "GEOMETRY AND TRIGONOMETRY")]

SYMBOL = {
    r"\pi": "pi", r"\cdot": "*", r"\times": "x", r"\ge": ">=", r"\le": "<=",
    r"\neq": "!=", r"\angle": "angle ", r"\circ": "deg", r"\%": "%",
    r"\$": "\x00DOLLAR\x00", r"\textbullet": "-", r"\textemdash": "--",
    r"\ldots": "...", r"\quad": "  ", r"\,": " ", r"\!": "",
    r"\left": "", r"\right": "", r"\displaystyle": "",
}


def braces(s, i):
    """Return (content, index after) for the group starting at s[i] == '{'."""
    depth, j = 0, i
    while j < len(s):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
        j += 1
    return s[i + 1:], len(s)


def take_two(s, i):
    a, i = braces(s, i)
    while i < len(s) and s[i] == " ":
        i += 1
    b, i = braces(s, i)
    return a, b, i


def flatten(s):
    """LaTeX -> readable ASCII, innermost groups first."""
    for _ in range(12):
        out, i, changed = [], 0, False
        while i < len(s):
            m = re.match(r"\\(dfrac|frac|tfrac|sqrt|overline|underline|text|mathrm)", s[i:])
            if m and i + m.end() < len(s):
                cmd, j = m.group(1), i + m.end()
                if cmd in ("dfrac", "frac", "tfrac") and j < len(s) and s[j] == "{":
                    a, b, j = take_two(s, j)
                    # parenthesise only a compound part; (z)/(124) is
                    # noisier than z/124 and means the same thing
                    wrap = lambda t: t if re.fullmatch(r"[\w.,]+", t) else f"({t})"
                    out.append(f"{wrap(a)}/{wrap(b)}")
                    i, changed = j, True
                    continue
                if cmd == "sqrt" and j < len(s):
                    if s[j] == "[":
                        k = s.index("]", j)
                        n, j2 = s[j + 1:k], k + 1
                        a, j2 = braces(s, j2)
                        out.append(f"({a})^(1/{n})")
                    else:
                        a, j2 = braces(s, j)
                        out.append(f"sqrt({a})")
                    i, changed = j2, True
                    continue
                if cmd in ("overline", "underline", "text", "mathrm") and s[j] == "{":
                    a, j = braces(s, j)
                    out.append(a)
                    i, changed = j, True
                    continue
            out.append(s[i])
            i += 1
        s = "".join(out)
        if not changed:
            break

    s = re.sub(r"\\[a-zA-Z]+|\\[$%,!]",
               lambda m: SYMBOL.get(m.group(0), ""), s)
    s = s.replace("$$", "\n    ").replace("$", "")
    s = s.replace("{", "").replace("}", "")
    s = re.sub(r"[ \t]+", " ", s)
    return s.replace("\x00DOLLAR\x00", "$").strip()


def para(s):
    """Split on the LaTeX paragraph breaks and on display maths, so an
    equation set off in the source is set off here too."""
    s = s.replace(r"\par\smallskip", "\n").replace(r"\par", "\n")
    out = []
    for block in s.split("\n"):
        for i, piece in enumerate(block.split("$$")):
            t = flatten(piece)
            if t:
                out.append(("    " + t) if i % 2 else t)
    return out


def main():
    problems = json.loads(BOOK.read_text())["problems"]
    ordered = []
    for d, _ in DOMAINS:
        ordered += [p for p in problems if p["domain"] == d]
    for i, p in enumerate(ordered, 1):
        p["book_n"] = i

    L = []
    bar = "=" * WIDTH
    L += [bar, "SAT MATH - 294 HARD QUESTIONS".center(WIDTH),
          "Math Instructor: Davlat Kamoliddinov".center(WIDTH), bar, ""]
    counts = {d: sum(1 for p in ordered if p["domain"] == d) for d, _ in DOMAINS}
    for d, t in DOMAINS:
        L.append(f"  {t.title():<38} {counts[d]:>3}")
    L += ["", "Merged from three collections, deduplicated.",
          "Answers are listed at the end.", ""]

    for d, title in DOMAINS:
        group = [p for p in ordered if p["domain"] == d]
        L += ["", bar, title.center(WIDTH), bar, ""]
        for p in group:
            L.append(f"{p['book_n']}.")
            for chunk in para(p["stem"]):
                if chunk.startswith("    "):
                    L.append("      " + chunk.strip())
                else:
                    L.append(textwrap.fill(chunk, WIDTH, initial_indent="   ",
                                           subsequent_indent="   "))
            if p.get("figure"):
                L.append("   [figure - see the PDF edition]")
            for letter, c in zip("ABCD", p["choices"]):
                L.append(textwrap.fill(f"{letter}) {flatten(c)}", WIDTH,
                                       initial_indent="   ",
                                       subsequent_indent="      "))
            L += ["", "", ""]          # room to work

    L += ["", bar, "ANSWER KEY".center(WIDTH), bar, ""]
    for d, title in DOMAINS:
        group = [p for p in ordered if p["domain"] == d]
        L += ["", title, "-" * len(title)]
        row = []
        for p in group:
            row.append(f"{p['book_n']:>4}. {flatten(p.get('answer') or '--'):<9}")
            if len(row) == 5:
                L.append("".join(row).rstrip())
                row = []
        if row:
            L.append("".join(row).rstrip())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n")
    print(f"{OUT.name}: {len(ordered)} problems, {len(L)} lines, "
          f"{OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
