#!/usr/bin/env python3
"""Classify the extracted catalog into census fields and pick sample evidence.

Queries data/catalog.db (FTS5) with field-level term buckets, counts how many
real listings belong to each field's corner of the catalog, and picks ten
representative examples per field. Writes assets/field-evidence.json, which
build.py renders as the "From the shelves" section on each field page.

Usage:  python3 pipeline/classify.py
"""
import json
import os
import sqlite3
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "data", "catalog.db")
OUT = os.path.join(ROOT, "assets", "field-evidence.json")

SOURCE_DISPLAY = {
    "flathub": "Flathub", "fdroid": "F-Droid", "itunes": "App Store",
    "play": "Google Play", "npm": "npm", "ifixit": "iFixit", "fda": "FDA devices",
    "arduino": "Arduino", "steam": "Steam", "off": "Open Food Facts",
    "github": "GitHub", "humanweb": "HumanWeb", "humanweb-curlie": "Curlie",
}

FIELD_TERMS = {
    "software": ["app", "software", "tool", "editor", "backup", "password", "note taking",
                 "launcher", "browser", "sdk", "library", "framework", "terminal", "git"],
    "ai": ["gpt", "llm", "machine learning", "neural", "chatbot", "transformer",
           "diffusion", "ai agent", "prompt", "deep learning", "inference"],
    "hardware": ["arduino", "raspberry", "sensor", "firmware", "3d print", "drone",
                 "iot", "esp32", "microcontroller", "pcb", "teardown", "repair"],
    "health": ["health", "medical", "fitness", "diet", "symptom", "therapy", "patient",
               "clinical", "hospital", "workout", "disease"],
    "climate": ["solar", "energy", "climate", "carbon", "battery", "recycling",
                "sustainable", "emission", "renewable", "environment"],
    "education": ["education", "learning", "course", "study", "flashcard", "exam",
                  "school", "teaching", "tutorial", "training"],
    "money": ["finance", "banking", "payment", "invoice", "budget", "crypto",
              "trading", "accounting", "tax", "wallet", "invoice"],
    "food": ["food", "recipe", "cooking", "restaurant", "nutrition", "coffee",
             "beer", "kitchen", "grocery", "meal"],
    "civic": ["government", "civic", "election", "open data", "city", "public services",
              "policy", "municipal", "parliament"],
    "robotics": ["robot", "ros ", "automation", "cnc", "robotic arm", "drone frame",
                 "gripper", "actuator"],
    "access": ["accessibility", "screen reader", "braille", "sign language", "blind",
               "disability", "wheelchair", "hearing"],
    "media": ["news", "podcast", "video", "music", "streaming", "rss", "blog",
              "radio", "television", "photo"],
    "law": ["legal", "law", "court", "attorney", "justice", "contract", "statute",
            "litigation", "lawyer"],
    "textiles": ["fashion", "clothing", "textile", "sewing", "knitting", "garment",
                 "wardrobe", "fabric", "apparel"],
    "death": ["funeral", "memorial", "grief", "cremation", "obituary", "cemetery",
              "bereavement", "mourning"],
    "ocean": ["ocean", "marine", "fishing", "nautical", "sailing", "diving",
              "seafood", "aquarium", "boat"],
    "parenting": ["parent", "baby", "child", "pregnancy", "kids", "toddler",
                  "childcare", "nursery", "children"],
    "travel": ["travel", "flight", "hotel", "tourism", "trip", "visa", "airport",
               "map", "navigation", "itinerary"],
    "space": ["space", "nasa", "satellite", "astronomy", "telescope", "rocket",
              "planetarium", "celestial", "orbit"],
    "arts": ["drawing", "painting", "museum", "gallery", "craft", "poetry",
             "sculpture", "photography", "creative", "theatre"],
}


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    has_fts = cur.execute(
        "SELECT COUNT(*) FROM sqlite_master WHERE name='apps_fts'").fetchone()[0]
    if not has_fts:
        raise SystemExit("apps_fts missing — run pipeline/build_site_index.py first")

    out = {"generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"), "fields": {}}
    for field, terms in FIELD_TERMS.items():
        match = " OR ".join('"' + t + '"' for t in terms)
        total = cur.execute(
            "SELECT COUNT(*) FROM apps_fts WHERE apps_fts MATCH ?",
            (match,)).fetchone()[0]
        rows = cur.execute(
            "SELECT a.source, a.name, a.summary, a.url FROM apps_fts f "
            "JOIN apps a ON a.rowid = f.rowid WHERE apps_fts MATCH ? "
            "LIMIT 3000", (match,)).fetchall()

        def score(r):
            name = (r[1] or "").lower()
            hits = sum(1 for t in terms if t in name)
            return (-hits, 0 if r[2] else 1, len(name))

        rows = sorted(rows, key=score)
        sample, srcs = [], {}
        for source, name, summary, url in rows:
            if len(sample) >= 10:
                break
            if srcs.get(source, 0) >= 2:
                continue
            if not summary:
                continue
            srcs[source] = srcs.get(source, 0) + 1
            sample.append([name[:120], summary[:200],
                           SOURCE_DISPLAY.get(source, source), url or ""])
        out["fields"][field] = {"total": total, "sample": sample}
        print(f"{field:<12} {total:>7,}  sample: {sample[0][0][:60] if sample else '-'}")

    conn.close()
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False)
    print(f"\nwrote {OUT}")


if __name__ == "__main__":
    main()
