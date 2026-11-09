#!/usr/bin/env python3
"""Add GitHub demand signals to assets/gap-evidence.json.

For every card check, search GitHub (via the authenticated gh CLI) for public
repositories matching the card's first query term — a phrase in name or
description, 15+ stars. High counts mean hackers are circling the gap; zero
means even the hackers haven't started. Requires: gh auth login.

Usage:  python3 pipeline/gh_signal.py [--limit N]
"""
import argparse
import json
import os
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
EV = os.path.join(os.path.dirname(HERE), "assets", "gap-evidence.json")


def gh_search(phrase):
    q = f'"{phrase}" in:name,description stars:>15 fork:false'
    result = subprocess.run(
        ["gh", "api", "-X", "GET", "search/repositories",
         "-f", f"q={q}", "-f", "sort=stars", "-f", "per_page=3"],
        capture_output=True, text=True, timeout=90)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip()[:200])
    data = json.loads(result.stdout)
    top = ""
    items = data.get("items") or []
    if items:
        r = items[0]
        stars = r.get("stargazers_count", 0)
        pushed = (r.get("pushed_at") or "")[:10]
        top = f"{r['full_name']} ({stars:,}★, last push {pushed})"
    return {"total": data.get("total_count", 0), "top": top}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=0, help="only check the first N cards")
    args = ap.parse_args()

    with open(EV, encoding="utf-8") as fh:
        ev = json.load(fh)
    checks = ev.get("checks", {})
    todo = list(checks.items())
    if args.limit:
        todo = todo[:args.limit]

    done = 0
    for cid, chk in todo:
        if "gh" in chk:
            continue
        phrase = (chk.get("queries") or [""])[0]
        if not phrase:
            continue
        try:
            chk["gh"] = gh_search(phrase)
        except Exception as e:  # noqa: BLE001 - rate limits etc: stop, keep progress
            print(f"  stopped at {cid}: {e}", file=__import__("sys").stderr)
            break
        done += 1
        g = chk["gh"]
        print(f"{cid:<18} {g['total']:>5} repos  {g['top'][:70]}")
        time.sleep(2.2)  # GitHub search API allows ~30 requests/minute

    with open(EV, "w", encoding="utf-8") as fh:
        json.dump(ev, fh, ensure_ascii=False, indent=1)
    print(f"\nupdated {EV} (signals this run: {done})")


if __name__ == "__main__":
    main()
