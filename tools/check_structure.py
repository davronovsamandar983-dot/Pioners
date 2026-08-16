#!/usr/bin/env python3
"""Structural gate for every topic of SAT Math Mastery.

Every topic must be: 44 questions, split 22 (Module 1) + 22 (Module 2),
question numbering restarting at 1 in Module 2, a matching answer-key file
with 44 entries, and a machine-readable manifest with 44 entries whose
types agree with the LaTeX source.

Usage:  python3 tools/check_structure.py [NN ...]     (default: all topics)
Exit code 0 = every checked topic is structurally sound.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TOPICS = ROOT / "book" / "topics"
ANSWERS = ROOT / "book" / "answers"
DATA = ROOT / "data"

PER_MODULE = 22
PER_TOPIC = PER_MODULE * 2

FORBIDDEN = [
    "Enter your response",
    "Enter response",
    "SAT Takers",
    "Quick Reference",
    "Key Concept",
    r"\begin{keyconcept}",
]


def strip_comments(text: str) -> str:
    """Drop LaTeX line comments so they cannot fool the counters."""
    out = []
    for line in text.split("\n"):
        idx = 0
        while True:
            idx = line.find("%", idx)
            if idx == -1:
                break
            if idx > 0 and line[idx - 1] == "\\":
                idx += 1
                continue
            line = line[:idx]
            break
        out.append(line)
    return "\n".join(out)


def brace_balance(text: str) -> int:
    depth = 0
    i = 0
    while i < len(text):
        c = text[i]
        if c == "\\" and i + 1 < len(text):
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
        i += 1
    return depth


def find_questions(text: str) -> list[tuple[int, str]]:
    """Return (position, kind) for every \\question / \\qfr in source order."""
    hits = []
    for m in re.finditer(r"\\(question|qfr)\s*\{", text):
        hits.append((m.start(), "fr" if m.group(1) == "qfr" else "q"))
    return hits


def macro_arg(text: str, open_brace: int) -> tuple[str, int]:
    """Given index of '{', return (contents, index just past matching '}')."""
    depth = 0
    i = open_brace
    while i < len(text):
        c = text[i]
        if c == "\\":
            i += 2
            continue
        if c == "{":
            depth += 1
        elif c == "}":
            depth -= 1
            if depth == 0:
                return text[open_brace + 1 : i], i + 1
        i += 1
    raise ValueError("unbalanced brace starting at %d" % open_brace)


def check_topic(tex_path: Path, errors: list[str], warnings: list[str]) -> None:
    slug = tex_path.stem
    tag = f"[{slug}]"
    raw = tex_path.read_text(encoding="utf-8")
    text = strip_comments(raw)

    bal = brace_balance(text)
    if bal != 0:
        errors.append(f"{tag} unbalanced braces in topic file (depth {bal:+d})")
        return

    for bad in FORBIDDEN:
        if bad in text:
            errors.append(f"{tag} forbidden content present: {bad!r}")

    # --- required scaffolding -------------------------------------------
    for macro in (r"\settopicname{", r"\chapter{", r"\topicopen{"):
        if macro not in text:
            errors.append(f"{tag} missing required macro {macro}...}}")

    if text.count(r"\begin{essentials}") != 1:
        errors.append(f"{tag} needs exactly one essentials block")

    heads = [m.start() for m in re.finditer(r"\\modulehead\s*\{", text)]
    if len(heads) != 2:
        errors.append(f"{tag} expected 2 \\modulehead, found {len(heads)}")
        return

    opens = text.count(r"\begin{multicols*}")
    closes = text.count(r"\end{multicols*}")
    if opens != closes:
        errors.append(f"{tag} multicols* not balanced ({opens} open, {closes} close)")
    if opens != 2:
        warnings.append(f"{tag} expected 2 multicols* blocks, found {opens}")

    # --- question count and module split --------------------------------
    qs = find_questions(text)
    if len(qs) != PER_TOPIC:
        errors.append(f"{tag} expected {PER_TOPIC} questions, found {len(qs)}")

    m1 = [k for pos, k in qs if heads[0] < pos < heads[1]]
    m2 = [k for pos, k in qs if pos > heads[1]]
    stray = [pos for pos, _ in qs if pos < heads[0]]
    if stray:
        errors.append(f"{tag} {len(stray)} question(s) sit before Module 1 header")
    if len(m1) != PER_MODULE:
        errors.append(f"{tag} Module 1 has {len(m1)} questions, expected {PER_MODULE}")
    if len(m2) != PER_MODULE:
        errors.append(f"{tag} Module 2 has {len(m2)} questions, expected {PER_MODULE}")

    # --- answer key ------------------------------------------------------
    ans_path = ANSWERS / f"{slug}.tex"
    if not ans_path.exists():
        errors.append(f"{tag} missing answer file {ans_path.relative_to(ROOT)}")
        return
    ans_text = strip_comments(ans_path.read_text(encoding="utf-8"))
    if brace_balance(ans_text) != 0:
        errors.append(f"{tag} unbalanced braces in answer file")
        return
    ans_entries = re.findall(r"\\ans\s*\{(\d+)\}\s*\{(\d+)\}", ans_text)
    if len(ans_entries) != PER_TOPIC:
        errors.append(
            f"{tag} answer key has {len(ans_entries)} entries, expected {PER_TOPIC}"
        )
    expected = [(str(mod), str(n)) for mod in (1, 2) for n in range(1, PER_MODULE + 1)]
    if ans_entries and ans_entries != expected:
        got = {e for e in ans_entries}
        missing = [e for e in expected if e not in got]
        if missing:
            errors.append(
                f"{tag} answer key missing M{missing[0][0]}Q{missing[0][1]}"
                f" (+{len(missing)-1} more)"
            )
        else:
            errors.append(f"{tag} answer key entries are out of order")

    # --- manifest --------------------------------------------------------
    data_path = DATA / f"{slug}.json"
    if not data_path.exists():
        errors.append(f"{tag} missing manifest {data_path.relative_to(ROOT)}")
        return
    try:
        manifest = json.loads(data_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{tag} manifest is not valid JSON: {exc}")
        return

    items = manifest.get("questions", [])
    if len(items) != PER_TOPIC:
        errors.append(f"{tag} manifest has {len(items)} questions, expected {PER_TOPIC}")

    # manifest type must agree with what the LaTeX actually renders
    kinds_tex = []
    for pos, _ in qs:
        brace = text.index("{", pos)
        body, _ = macro_arg(text, brace)
        kinds_tex.append("mc" if r"\choices" in body else "fr")

    for i, item in enumerate(items[: len(kinds_tex)]):
        want = kinds_tex[i]
        got = item.get("type")
        if got != want:
            mod = 1 if i < PER_MODULE else 2
            num = i + 1 if i < PER_MODULE else i + 1 - PER_MODULE
            errors.append(
                f"{tag} M{mod}Q{num}: manifest says type={got!r}"
                f" but LaTeX renders a {want!r} question"
            )
        if want == "mc":
            if len(item.get("choices", [])) != 4:
                errors.append(f"{tag} manifest item {i+1}: mc needs 4 choices")
            if item.get("choice") not in ("A", "B", "C", "D"):
                errors.append(f"{tag} manifest item {i+1}: choice must be A-D")
        if not str(item.get("answer", "")).strip():
            errors.append(f"{tag} manifest item {i+1}: empty answer")

    # --- difficulty ladder ------------------------------------------------
    diffs = [it.get("difficulty") for it in items]
    if any(d not in ("easy", "medium", "hard") for d in diffs):
        errors.append(f"{tag} every manifest item needs difficulty easy|medium|hard")
    else:
        rank = {"easy": 0, "medium": 1, "hard": 2}
        for mod, chunk in (("1", diffs[:PER_MODULE]), ("2", diffs[PER_MODULE:])):
            if not chunk:
                continue
            inversions = sum(
                1
                for a, b in zip(chunk, chunk[1:])
                if rank[b] < rank[a] - 0  # any step backwards
            )
            if inversions > 3:
                warnings.append(
                    f"{tag} Module {mod} difficulty ladder wobbles"
                    f" ({inversions} backward steps); should climb easy->hard"
                )
        if diffs[:PER_MODULE].count("hard") > diffs[PER_MODULE:].count("hard"):
            warnings.append(
                f"{tag} Module 1 has more hard questions than Module 2;"
                " Module 2 is meant to be the harder adaptive module"
            )


def main(argv: list[str]) -> int:
    if argv:
        wanted = {a.zfill(2) for a in argv}
        files = sorted(p for p in TOPICS.glob("*.tex") if p.stem[:2] in wanted)
    else:
        files = sorted(TOPICS.glob("*.tex"))

    if not files:
        print("no topic files found", file=sys.stderr)
        return 1

    errors: list[str] = []
    warnings: list[str] = []
    for f in files:
        check_topic(f, errors, warnings)

    for w in warnings:
        print("WARN  " + w)
    for e in errors:
        print("ERROR " + e)

    total_q = len(files) * PER_TOPIC
    print(
        f"\nchecked {len(files)} topic(s) = {total_q} question slots;"
        f" {len(errors)} error(s), {len(warnings)} warning(s)"
    )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
