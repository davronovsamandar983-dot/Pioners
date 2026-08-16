#!/usr/bin/env python3
"""Symbolic answer verification for SAT Math Mastery.

Each topic ships a manifest at data/<slug>.json. Every question carries the
answer the book prints, and — wherever the mathematics can be expressed
symbolically — a `check` block that sympy re-derives independently. A topic
passes only when every derivable answer is reproduced from scratch and every
multiple-choice letter points at the option holding that answer.

    python3 tools/verify_answers.py [NN ...]

Manifest question shape
-----------------------
{
  "module": 1, "n": 3, "type": "mc" | "fr",
  "difficulty": "easy" | "medium" | "hard",
  "answer": "7",                       # what the answer key prints
  "answer_kind": "number" | "expression" | "text",
  "choices": ["6", "7", "8", "9"],     # mc only, in A-D order
  "choice": "B",                       # mc only
  "check": { ... }                     # see CHECKS below
}

CHECKS
------
{"kind": "solve",    "expr": "3*x - 21", "var": "x"}          expr = 0
{"kind": "solve",    "expr": "3*x - 21", "var": "x", "all": true}
{"kind": "system",   "exprs": [...], "vars": [...], "want": "x"}
{"kind": "evaluate", "expr": "3*5 - 7"}
{"kind": "equiv",    "expr": "(x+1)**2", "other": "x**2+2*x+1"}
{"kind": "manual",   "note": "why sympy cannot express this"}
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import sympy as sp
from sympy.parsing.sympy_parser import (
    convert_xor,
    implicit_multiplication_application,
    parse_expr,
    standard_transformations,
)

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"

TRANSFORMS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)

TEXTUAL = {"text", "interpretation"}


def P(s: str):
    return parse_expr(str(s), transformations=TRANSFORMS, evaluate=True)


def same(a, b, tol=1e-9) -> bool:
    """Symbolic-then-numeric equality that tolerates 1/3 vs 0.333..."""
    try:
        if sp.simplify(sp.nsimplify(a - b)) == 0:
            return True
    except Exception:
        pass
    try:
        d = complex(sp.N(a - b))
        return abs(d) < tol
    except Exception:
        return False


def as_set(value: str) -> list:
    return [P(part) for part in str(value).split(",") if str(part).strip()]


def run_check(chk: dict, answer: str) -> tuple[bool, str]:
    kind = chk.get("kind")

    if kind == "manual":
        return True, "manual: " + chk.get("note", "no note given")

    if kind == "solve":
        var = sp.Symbol(chk["var"])
        roots = sp.solve(sp.Eq(P(chk["expr"]), 0), var, dict=False)
        roots = [sp.nsimplify(r) for r in roots]
        if chk.get("all"):
            want = as_set(answer)
            ok = len(want) == len(roots) and all(
                any(same(w, r) for r in roots) for w in want
            )
            return ok, f"solve -> {roots}"
        want = P(answer)
        return any(same(want, r) for r in roots), f"solve -> {roots}"

    if kind == "system":
        vars_ = [sp.Symbol(v) for v in chk["vars"]]
        eqs = [sp.Eq(P(e), 0) for e in chk["exprs"]]
        sol = sp.solve(eqs, vars_, dict=True)
        if not sol:
            return False, "system has no solution"
        want_sym = sp.Symbol(chk["want"]) if chk.get("want") else None
        if want_sym is not None:
            vals = [s[want_sym] for s in sol if want_sym in s]
            if not vals:
                return False, f"system did not determine {want_sym}"
            return any(same(P(answer), v) for v in vals), f"system -> {vals}"
        expr = P(chk["want_expr"])
        vals = [expr.subs(s) for s in sol]
        return any(same(P(answer), v) for v in vals), f"system -> {vals}"

    if kind == "evaluate":
        val = sp.nsimplify(P(chk["expr"]))
        return same(P(answer), val), f"evaluate -> {val}"

    if kind == "equiv":
        a, b = P(chk["expr"]), P(chk["other"])
        ok = sp.simplify(sp.expand(a - b)) == 0
        return ok, f"equiv({a}, {b})"

    return False, f"unknown check kind {kind!r}"


def verify_topic(path: Path) -> tuple[int, int, list[str]]:
    manifest = json.loads(path.read_text(encoding="utf-8"))
    slug = manifest.get("slug", path.stem)
    problems: list[str] = []
    checked = 0
    manual = 0

    for item in manifest.get("questions", []):
        label = f"[{slug}] M{item.get('module')}Q{item.get('n')}"
        answer = str(item.get("answer", "")).strip()
        kind = item.get("answer_kind", "number")

        # 1. multiple-choice letter must point at the printed answer
        if item.get("type") == "mc":
            letter = item.get("choice", "")
            choices = item.get("choices", [])
            if letter in "ABCD" and len(choices) == 4:
                keyed = str(choices["ABCD".index(letter)]).strip()
                if kind in TEXTUAL:
                    if keyed != answer:
                        problems.append(
                            f"{label}: choice {letter} is {keyed!r}"
                            f" but answer key prints {answer!r}"
                        )
                else:
                    try:
                        if not same(P(keyed), P(answer)):
                            problems.append(
                                f"{label}: choice {letter} = {keyed}"
                                f" does not equal the keyed answer {answer}"
                            )
                    except Exception as exc:
                        problems.append(f"{label}: cannot parse choices ({exc})")
                # a correct option must not be duplicated
                parsed = []
                dup = False
                for c in choices:
                    try:
                        parsed.append(P(c))
                    except Exception:
                        parsed.append(None)
                for i in range(4):
                    for j in range(i + 1, 4):
                        if parsed[i] is not None and parsed[j] is not None:
                            try:
                                if same(parsed[i], parsed[j]):
                                    dup = True
                            except Exception:
                                pass
                if dup:
                    problems.append(f"{label}: two answer choices are equal")

        # 2. the mathematics itself
        chk = item.get("check")
        if not chk:
            if kind not in TEXTUAL:
                problems.append(f"{label}: no check block and answer is not textual")
            continue
        try:
            ok, detail = run_check(chk, answer)
        except Exception as exc:
            problems.append(f"{label}: check raised {type(exc).__name__}: {exc}")
            continue
        if chk.get("kind") == "manual":
            manual += 1
            continue
        checked += 1
        if not ok:
            problems.append(f"{label}: answer {answer!r} contradicts {detail}")

    return checked, manual, problems


def main(argv: list[str]) -> int:
    if argv:
        wanted = {a.zfill(2) for a in argv}
        files = sorted(p for p in DATA.glob("*.json") if p.stem[:2] in wanted)
    else:
        files = sorted(DATA.glob("*.json"))

    if not files:
        print("no manifests found", file=sys.stderr)
        return 1

    total_checked = total_manual = 0
    all_problems: list[str] = []
    for f in files:
        c, m, probs = verify_topic(f)
        total_checked += c
        total_manual += m
        all_problems.extend(probs)

    for p in all_problems:
        print("FAIL  " + p)

    print(
        f"\n{len(files)} topic(s): {total_checked} answer(s) re-derived by sympy,"
        f" {total_manual} manual, {len(all_problems)} problem(s)"
    )
    if total_manual and total_checked:
        share = total_manual / (total_manual + total_checked)
        if share > 0.30:
            print(
                f"WARN  {share:.0%} of questions are 'manual' — that is high;"
                " prefer questions sympy can re-derive"
            )
    return 1 if all_problems else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
