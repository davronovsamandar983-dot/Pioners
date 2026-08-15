#!/usr/bin/env python3
"""Validate every topic bank in content/bank/.

Three layers of checking:

  1. schema      -- content/schema.json (shape, id pattern, 44 problems, ...)
  2. structure   -- module split 22/22, contiguous numbering, id/module/n
                    agreement, MCQ answer present among choices, difficulty
                    ramp, duplicate-stem detection
  3. mathematics -- every problem may carry a `verify` field: a small Python
                    snippet evaluated with sympy in a sandboxed namespace that
                    must set `result`.  `result` is compared against the stated
                    answer (for SPR) or against the stated correct choice text
                    (for MC).  A problem without `verify` is reported so no
                    item silently escapes review.

Exit code is non-zero if any error is found.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter

import jsonschema
import sympy

ROOT = pathlib.Path(__file__).resolve().parent.parent
BANK = ROOT / "content" / "bank"
SCHEMA = ROOT / "content" / "schema.json"

PROBLEMS_PER_TOPIC = 44
PROBLEMS_PER_MODULE = 22


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, where: str, msg: str) -> None:
        self.errors.append(f"{where}: {msg}")

    def warn(self, where: str, msg: str) -> None:
        self.warnings.append(f"{where}: {msg}")


# --------------------------------------------------------------- helpers ---

_SANDBOX_DENY = re.compile(r"\b(import|open|exec|eval|__|compile|globals|locals)\b")


def run_verify(code: str):
    """Evaluate a `verify` snippet and return its `result`."""
    if _SANDBOX_DENY.search(code):
        raise ValueError("verify snippet uses a forbidden construct")
    ns: dict = {"sp": sympy, "S": sympy.S, "Rational": sympy.Rational,
                "sqrt": sympy.sqrt, "pi": sympy.pi, "symbols": sympy.symbols,
                "solve": sympy.solve, "simplify": sympy.simplify,
                "Eq": sympy.Eq, "nsimplify": sympy.nsimplify,
                "expand": sympy.expand, "factor": sympy.factor,
                "Abs": sympy.Abs, "log": sympy.log, "exp": sympy.exp,
                "sin": sympy.sin, "cos": sympy.cos, "tan": sympy.tan,
                "Matrix": sympy.Matrix, "binomial": sympy.binomial}
    exec(code, {"__builtins__": {"range": range, "len": len, "sum": sum,
                                 "abs": abs, "min": min, "max": max,
                                 "sorted": sorted, "list": list,
                                 "float": float, "int": int, "round": round}}, ns)
    if "result" not in ns:
        raise ValueError("verify snippet did not set `result`")
    return ns["result"]


def to_expr(text: str):
    """Parse an answer string (LaTeX-lite or plain) into a sympy expression."""
    t = text.strip()
    t = t.replace("$", "").replace("\\!", "").replace("\\,", "").replace(" ", "")
    t = t.replace("\\left", "").replace("\\right", "")
    t = re.sub(r"\\d?frac\{([^{}]+)\}\{([^{}]+)\}", r"((\1)/(\2))", t)
    t = re.sub(r"\\sqrt\{([^{}]+)\}", r"sqrt(\1)", t)
    t = re.sub(r"\\sqrt(\d)", r"sqrt(\1)", t)
    t = t.replace("\\pi", "pi").replace("^", "**").replace("\\cdot", "*")
    t = t.replace("\\times", "*").replace("\\div", "/")
    t = re.sub(r"[{}]", "", t)
    t = t.rstrip("%")
    return sympy.sympify(t, rational=True)


def answers_match(a, b) -> bool:
    try:
        return sympy.simplify(sympy.nsimplify(a) - sympy.nsimplify(b)) == 0
    except Exception:
        return str(a).strip() == str(b).strip()


# ------------------------------------------------------------ structure ----

def check_structure(bank: dict, rep: Report) -> None:
    tno = bank["number"]
    where = f"topic {tno:02d}"
    problems = bank["problems"]

    if len(problems) != PROBLEMS_PER_TOPIC:
        rep.error(where, f"expected {PROBLEMS_PER_TOPIC} problems, found {len(problems)}")

    by_module = Counter(p["module"] for p in problems)
    for mod in (1, 2):
        if by_module[mod] != PROBLEMS_PER_MODULE:
            rep.error(where, f"module {mod} has {by_module[mod]} problems, "
                             f"expected {PROBLEMS_PER_MODULE}")

    # numbering must run 1..44 exactly once, module 1 taking 1..22
    ns = [p["n"] for p in problems]
    if sorted(ns) != list(range(1, PROBLEMS_PER_TOPIC + 1)):
        rep.error(where, "problem numbers are not exactly 1..44")
    for p in problems:
        expected_mod = 1 if p["n"] <= PROBLEMS_PER_MODULE else 2
        if p["module"] != expected_mod:
            rep.error(where, f"{p['id']}: n={p['n']} belongs to module "
                             f"{expected_mod}, but module={p['module']}")

    # id must agree with topic number, module and position within the module
    for p in problems:
        pos = p["n"] if p["module"] == 1 else p["n"] - PROBLEMS_PER_MODULE
        want = f"T{tno:02d}-M{p['module']}-{pos:02d}"
        if p["id"] != want:
            rep.error(where, f"id {p['id']} should be {want}")

    if len({p["id"] for p in problems}) != len(problems):
        rep.error(where, "duplicate problem ids")

    # MCQ sanity
    for p in problems:
        if p["type"] == "MC":
            if len({c.strip() for c in p["choices"]}) != 4:
                rep.error(where, f"{p['id']}: duplicate answer choices")
        else:
            if not p["answer"].strip():
                rep.error(where, f"{p['id']}: empty SPR answer")

    # duplicate stems across the topic
    stems = Counter(re.sub(r"\s+", " ", p["stem"]).strip().lower() for p in problems)
    for stem, count in stems.items():
        if count > 1:
            rep.error(where, f"stem repeated {count}x: {stem[:70]}...")

    # difficulty ramp: each module should progress easy -> hard
    order = {"E": 0, "M": 1, "H": 2}
    for mod in (1, 2):
        seq = [order[p["difficulty"]] for p in sorted(
            (q for q in problems if q["module"] == mod), key=lambda q: q["n"])]
        first_half, second_half = seq[:11], seq[11:]
        if first_half and second_half and \
                sum(first_half) / 11 > sum(second_half) / 11:
            rep.warn(where, f"module {mod}: difficulty does not increase "
                            f"across the module")
        if seq[0] != 0:
            rep.warn(where, f"module {mod}: does not open with an EASY item")
        if seq[-1] != 2:
            rep.warn(where, f"module {mod}: does not close with a HARD item")

    # answer-key balance for MCQs
    mc = [p for p in problems if p["type"] == "MC"]
    if mc:
        dist = Counter(p["answer"] for p in mc)
        for letter in "ABCD":
            share = dist[letter] / len(mc)
            if share > 0.40:
                rep.warn(where, f"answer '{letter}' is {share:.0%} of MCQs "
                                f"(key is unbalanced)")
    spr = [p for p in problems if p["type"] == "SPR"]
    if not 4 <= len(spr) <= 14:
        rep.warn(where, f"{len(spr)} student-produced-response items "
                        f"(the real test runs about 25%)")


# ---------------------------------------------------------- mathematics ----

def check_math(bank: dict, rep: Report, require_verify: bool) -> tuple[int, int]:
    tno = bank["number"]
    where = f"topic {tno:02d}"
    verified = 0
    for p in bank["problems"]:
        code = p.get("verify")
        if not code:
            (rep.error if require_verify else rep.warn)(
                where, f"{p['id']}: no `verify` snippet -- answer unchecked")
            continue
        try:
            result = run_verify(code)
        except Exception as exc:                       # noqa: BLE001
            rep.error(where, f"{p['id']}: verify failed to run -- {exc}")
            continue

        if p["type"] == "MC":
            idx = "ABCD".index(p["answer"])
            target = p["choices"][idx]
        else:
            target = p["answer"]

        candidates = [target] + list(p.get("accepted", []))
        ok = False
        for cand in candidates:
            try:
                if answers_match(result, to_expr(cand)):
                    ok = True
                    break
            except Exception:                          # noqa: BLE001
                if str(result).strip() == cand.strip():
                    ok = True
                    break
        if ok:
            verified += 1
        else:
            rep.error(where, f"{p['id']}: verify gives {result!r} but the "
                             f"stated answer is {target!r}")

        # a distractor must never equal the key
        if p["type"] == "MC":
            for i, choice in enumerate(p["choices"]):
                if i == "ABCD".index(p["answer"]):
                    continue
                try:
                    if answers_match(to_expr(choice), to_expr(target)):
                        rep.error(where, f"{p['id']}: distractor "
                                         f"{'ABCD'[i]} equals the key")
                except Exception:                      # noqa: BLE001
                    pass

    return verified, len(bank["problems"])


# ----------------------------------------------------------------- main ----

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--require-verify", action="store_true",
                    help="treat a missing `verify` snippet as an error")
    ap.add_argument("--topic", type=int, default=None,
                    help="validate a single topic number")
    args = ap.parse_args()

    schema = json.loads(SCHEMA.read_text())
    rep = Report()

    files = sorted(BANK.glob("topic-*.json"))
    if args.topic is not None:
        files = [f for f in files if f.stem == f"topic-{args.topic:02d}"]
    if not files:
        print("no topic banks found in content/bank/", file=sys.stderr)
        return 1

    total_problems = total_verified = 0
    seen_numbers: set[int] = set()

    for path in files:
        try:
            bank = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            rep.error(path.name, f"invalid JSON -- {exc}")
            continue

        try:
            jsonschema.validate(bank, schema)
        except jsonschema.ValidationError as exc:
            loc = "/".join(str(x) for x in exc.absolute_path) or "<root>"
            rep.error(path.name, f"schema violation at {loc} -- {exc.message}")
            continue

        if bank["number"] in seen_numbers:
            rep.error(path.name, f"topic number {bank['number']} used twice")
        seen_numbers.add(bank["number"])
        if path.stem != f"topic-{bank['number']:02d}":
            rep.error(path.name, f"filename does not match topic number "
                                 f"{bank['number']}")

        check_structure(bank, rep)
        v, t = check_math(bank, rep, args.require_verify)
        total_verified += v
        total_problems += t

    # book-level totals
    if args.topic is None:
        missing = sorted(set(range(1, 21)) - seen_numbers)
        if missing:
            rep.error("book", f"missing topics: "
                              f"{', '.join(f'{m:02d}' for m in missing)}")
        if total_problems != 880 and not missing:
            rep.error("book", f"{total_problems} problems in total, expected 880")

    for w in rep.warnings:
        print(f"  warn   {w}")
    for e in rep.errors:
        print(f"  ERROR  {e}")

    print()
    print(f"  topics      {len(seen_numbers)}/20")
    print(f"  problems    {total_problems}" +
          ("/880" if args.topic is None else ""))
    print(f"  verified    {total_verified}/{total_problems}"
          if total_problems else "  verified    0")
    print(f"  warnings    {len(rep.warnings)}")
    print(f"  errors      {len(rep.errors)}")

    return 1 if rep.errors else 0


if __name__ == "__main__":
    sys.exit(main())
