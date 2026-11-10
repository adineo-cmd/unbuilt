#!/usr/bin/env python3
"""Merge data/raw/*.json into the site's shelf index and a local SQLite catalog.

Outputs (relative to the project root):
  assets/catalog.json   compact index shipped with the site (default: 20,000 rows)
  data/catalog.db       full SQLite catalog with descriptions, for deep local search

Usage:
  python3 pipeline/build_site_index.py            # default cap 20,000
  python3 pipeline/build_site_index.py --max 40000
"""
import argparse
import json
import os
import sqlite3
from datetime import date, datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
RAW = os.path.join(ROOT, "data", "raw")
ASSETS = os.path.join(ROOT, "assets")

SUMMARY_LIMIT = 220


def load_raw():
    rows = []
    for name in sorted(os.listdir(RAW)):
        if name.endswith(".json"):
            source = name[:-5]
            with open(os.path.join(RAW, name), encoding="utf-8") as fh:
                data = json.load(fh)
            apps = data.get("apps") or []
            rows.append((source, apps))
            print(f"  {source}: {len(apps)}")
        elif name.endswith(".ndjson.gz"):
            import gzip
            source = name[:-len(".ndjson.gz")]
            apps = []
            with gzip.open(os.path.join(RAW, name), "rt", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if line:
                        try:
                            apps.append(json.loads(line))
                        except Exception:
                            continue
            rows.append((source, apps))
            print(f"  {source}: {len(apps)} (ndjson.gz)")
    return rows


def normalize(source, a):
    name = (a.get("name") or "").strip()
    if not name:
        return None
    summary = (a.get("summary") or a.get("description") or "").strip()[:SUMMARY_LIMIT]
    return {
        "name": name,
        "summary": summary,
        "source": source,
        "category": (a.get("category") or "").strip()[:60],
        "developer": (a.get("developer") or "").strip()[:100],
        "url": (a.get("url") or "").strip(),
        "description": (a.get("description") or "").strip()[:4000],
        "id": (a.get("id") or "").strip(),
    }


def interleave(groups):
    """Round-robin across sources so every catalog is represented in the cap."""
    out, idx = [], 0
    pools = [list(g) for g in groups if g]
    while pools:
        for pool in list(pools):
            if not pool:
                pools.remove(pool)
                continue
            out.append(pool.pop(0))
        idx += 1
        if idx > 200000:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max", type=int, default=20000,
                    help="max rows shipped in assets/catalog.json")
    args = ap.parse_args()

    os.makedirs(ASSETS, exist_ok=True)
    print("loading raw catalogs:")
    import hashlib
    groups = []
    seen = set()
    for source, apps in load_raw():
        norm, per_source_seen = [], set()
        for a in apps:
            row = normalize(source, a)
            if not row:
                continue
            key = hashlib.md5(
                (row["name"].lower() + "\x00" + row["developer"].lower()).encode()
            ).digest()
            if key in seen or key in per_source_seen:
                continue
            per_source_seen.add(key)
            seen.add(key)
            norm.append(row)
        groups.append(norm)

    merged = interleave(groups)
    shipped = merged[:args.max]

    catalog = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "count": len(shipped),
        "total": len(merged),
        "sources": {s: sum(1 for r in shipped if r["source"] == s)
                    for s in sorted({r["source"] for r in shipped})},
        "apps": [[r["name"], r["summary"], r["source"], r["category"], r["url"], r["developer"]]
                 for r in shipped],
    }
    out = os.path.join(ASSETS, "catalog.json")
    with open(out, "w", encoding="utf-8") as fh:
        json.dump(catalog, fh, ensure_ascii=False, separators=(",", ":"))
    print(f"wrote {out}: {catalog['count']} of {catalog['total']} rows "
          f"({os.path.getsize(out) / 1e6:.1f} MB)")

    db = os.path.join(ROOT, "data", "catalog.db")
    conn = sqlite3.connect(db)
    conn.execute("DROP TABLE IF EXISTS apps")
    conn.execute("""CREATE TABLE apps (
        source TEXT, id TEXT, name TEXT, summary TEXT, description TEXT,
        category TEXT, developer TEXT, url TEXT)""")
    conn.executemany(
        "INSERT INTO apps VALUES (?,?,?,?,?,?,?,?)",
        [(r["source"], r["id"], r["name"], r["summary"], r["description"],
          r["category"], r["developer"], r["url"]) for r in merged])
    conn.execute("CREATE INDEX IF NOT EXISTS idx_name ON apps(name)")
    # FTS5 index: makes mine_gaps phrase checks fast over millions of rows
    conn.execute("DROP TABLE IF EXISTS apps_fts")
    conn.execute("""CREATE VIRTUAL TABLE apps_fts USING fts5(
        name, summary, category, developer, source UNINDEXED)""")
    conn.execute("""INSERT INTO apps_fts(rowid, name, summary, category, developer, source)
        SELECT rowid, name, summary, category, developer, source FROM apps""")
    conn.commit()
    conn.close()
    print(f"wrote {db}: {len(merged)} rows with full descriptions")


if __name__ == "__main__":
    main()
