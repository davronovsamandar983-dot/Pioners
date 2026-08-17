#!/usr/bin/env python3
"""Merge the two source banks into one book, removing duplicates.

Exact duplicates are dropped outright. Near-duplicates (same question
template, different numbers) are reported but kept, because they are
distinct problems a student must actually solve.
"""
import json, re, sys, itertools, difflib, pathlib

HERE = pathlib.Path(__file__).resolve().parent.parent
BANKS = [("A", HERE / "content/bank_a.json"),
         ("B", HERE / "content/bank_b.json"),
         ("C", HERE / "content/bank_c.json")]


def normalise(stem: str) -> str:
    """Collapse a stem to its comparable skeleton."""
    s = stem.lower()
    s = re.sub(r"\\par|\\smallskip|\\underline|\\dfrac|\\frac|\\left|\\right", " ", s)
    s = re.sub(r"[^a-z0-9]+", " ", s)
    return re.sub(r"\s+", " ", s).strip()


def skeleton(stem: str) -> str:
    """Normalised stem with every number replaced by a placeholder."""
    return re.sub(r"\d+", "#", normalise(stem))


def main() -> int:
    items = []
    for tag, path in BANKS:
        bank = json.loads(path.read_text())
        for p in bank["problems"]:
            p["src"] = tag
            p["src_n"] = p["n"]
            p["src_name"] = bank["source"]
            items.append(p)

    print(f"loaded {len(items)} problems from {len(BANKS)} sources")

    # --- exact duplicates -------------------------------------------------
    seen, kept, exact = {}, [], []
    for p in items:
        key = normalise(p["stem"])
        if key in seen:
            exact.append((seen[key], p))
            continue
        seen[key] = p
        kept.append(p)

    print(f"\nexact duplicates removed: {len(exact)}")
    for a, b in exact:
        print(f"  {b['src']}{b['src_n']} == {a['src']}{a['src_n']}: {b['stem'][:70]}...")

    # --- near duplicates (same template, different numbers) ---------------
    by_skel = {}
    for p in kept:
        by_skel.setdefault(skeleton(p["stem"]), []).append(p)
    near = [v for v in by_skel.values() if len(v) > 1]

    print(f"\nsame-template groups (kept, numbers differ): {len(near)}")
    for grp in near:
        ids = ", ".join(f"{p['src']}{p['src_n']}" for p in grp)
        print(f"  [{ids}] {grp[0]['stem'][:64]}...")

    # --- high-similarity pairs that the skeleton test misses --------------
    print("\nhigh-similarity pairs (>=0.90, manual review):")
    norms = [(p, normalise(p["stem"])) for p in kept]
    flagged = 0
    for (p, a), (q, b) in itertools.combinations(norms, 2):
        if abs(len(a) - len(b)) > 40:
            continue
        if difflib.SequenceMatcher(None, a, b).ratio() >= 0.90:
            print(f"  {p['src']}{p['src_n']} ~ {q['src']}{q['src_n']}: {p['stem'][:56]}...")
            flagged += 1
    if not flagged:
        print("  none")

    for i, p in enumerate(kept, 1):
        p["n"] = i
    out = HERE / "content/book.json"
    out.write_text(json.dumps({"problems": kept}, indent=1, ensure_ascii=False))
    print(f"\nunique problems written to {out.name}: {len(kept)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
