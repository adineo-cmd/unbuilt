#!/usr/bin/env python3
"""Run "shelves checks": match every not-built claim against the collected catalogs.

For each card id in SEEDS, count how many rows of data/catalog.db (name, summary,
category, developer) match any of the card's query terms, and pick up to three
representative examples. Writes assets/gap-evidence.json, which build.py renders
as the "Shelves check" line on each card.

A check of zero means "not in our ten catalogs" — not "does not exist anywhere".
Run after pipeline/ingest.py + pipeline/build_site_index.py.

Usage:  python3 pipeline/mine_gaps.py
"""
import json
import os
import sqlite3
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DB = os.path.join(ROOT, "data", "catalog.db")
OUT = os.path.join(ROOT, "assets", "gap-evidence.json")

SOURCE_DISPLAY = {
    "flathub": "Flathub", "fdroid": "F-Droid", "itunes": "App Store",
    "play": "Google Play", "npm": "npm", "ifixit": "iFixit", "fda": "FDA devices",
    "arduino": "Arduino", "steam": "Steam", "off": "Open Food Facts",
}

# card id -> query terms (matched as whole tokens on name/summary/category/developer)
SEEDS = {
    # ---- existing not-built cards
    "c-software-u0": ["download my data", "gdpr export", "data export", "takeout"],
    "c-software-u1": ["end of life", "abandonware", "sunset notice"],
    "c-software-u2": ["internet speed", "network diagnostic", "dns test"],
    "c-software-u3": ["digital legacy", "dead man switch", "inheritance"],
    "c-software-u4": ["medical bill", "bill scan", "explain bill"],
    "c-ai-u0": ["hallucination", "fact check", "citation"],
    "c-ai-u1": ["license compliance", "copyleft", "license audit"],
    "c-ai-u2": ["low resource language", "minority language", "underresourced language"],
    "c-ai-u3": ["permit", "visa", "government form"],
    "c-ai-u4": ["model evaluation", "ai benchmark", "llm eval"],
    "c-hardware-u0": ["braille"],
    "c-hardware-u1": ["hearing aid", "audiogram"],
    "c-hardware-u2": ["battery storage", "second life battery", "ev battery"],
    "c-hardware-u3": ["teardown", "repair manual", "service manual", "spare part"],
    "c-hardware-u4": ["water quality", "water test"],
    "c-health-u0": ["menopause"],
    "c-health-u1": ["blood test", "lab result", "blood panel"],
    "c-health-u2": ["drug interaction", "medication interaction"],
    "c-health-u3": ["phage", "antibiotic resistance"],
    "c-health-u4": ["therapist", "find a doctor", "book doctor"],
    "c-climate-u0": ["air conditioner", "ac control"],
    "c-climate-u1": ["heat pump"],
    "c-climate-u2": ["water heater"],
    "c-climate-u3": ["battery health", "cell grader", "battery test"],
    "c-climate-u4": ["crop rotation", "planting calendar", "crop planning"],
    "c-education-u0": ["spaced repetition", "flashcard"],
    "c-education-u1": ["science kit", "virtual lab"],
    "c-education-u2": ["apprentice", "trade school", "vocational"],
    "c-education-u3": ["portfolio", "verified skill"],
    "c-education-u4": ["physics simulator", "physics"],
    "c-money-u0": ["portable benefits", "gig benefits"],
    "c-money-u1": ["pension", "micro pension"],
    "c-money-u2": ["medical bill", "insurance claim"],
    "c-money-u3": ["payroll", "contractor payment", "employer of record"],
    "c-money-u4": ["microinsurance", "index insurance", "takaful"],
    "c-food-u0": ["fridge", "pantry"],
    "c-food-u1": ["agronomy", "farm advisory", "crop advice"],
    "c-food-u2": ["food waste"],
    "c-food-u3": ["tractor", "farm equipment"],
    "c-food-u4": ["compost"],
    "c-civic-u0": ["fixmystreet", "see click fix", "city works"],
    "c-civic-u1": ["what3words", "plus code", "address"],
    "c-civic-u2": ["municipal code", "ordinance", "city ordinance"],
    "c-civic-u3": ["mesh network", "community network", "broadband"],
    "c-civic-u4": ["panic button", "sos beacon", "emergency sos"],
    "c-robotics-u0": ["laundry", "fold clothes"],
    "c-robotics-u1": ["dexterous hand", "robot gripper", "bionic hand"],
    "c-robotics-u2": ["cooking robot", "kitchen robot"],
    "c-robotics-u3": ["pick and place", "assembly line"],
    "c-robotics-u4": ["recycling", "waste sorting"],
    "c-access-u0": ["sign language"],
    "c-access-u1": ["audio description", "described video"],
    "c-access-u2": ["wheelchair", "curb cut"],
    "c-access-u3": ["screen reader"],
    "c-access-u4": ["brain injury", "memory prosthesis"],
    "c-media-u0": ["content credentials", "c2pa", "provenance"],
    "c-media-u1": ["social media backup", "account archive"],
    "c-media-u2": ["cookie consent", "gdpr banner", "privacy consent"],
    "c-media-u3": ["fact check"],
    "c-media-u4": ["forum", "bbs", "community board"],
    # ---- new not-built cards
    "c-software-u5": ["personal data api", "quantified self", "data vault", "own your data"],
    "c-ai-u5": ["voice clone", "voice cloning", "voice print"],
    "c-ai-u6": ["ai liability", "ai insurance"],
    "c-hardware-u5": ["service manual", "repair manual", "spare parts"],
    "c-health-u5": ["caregiver", "elder care", "aging parent"],
    "c-climate-u5": ["demand response", "virtual power plant", "grid services"],
    "c-money-u5": ["freelancer", "gig work", "reputation"],
    "c-access-u6": ["symptom tracker", "pain scale", "patient reported"],
    "c-media-u6": ["webmention", "comment system", "comments plugin"],
    # ---- new half-built cards
    "c-software-h5": ["local ai", "offline ai", "private ai", "on device model"],
    "c-ai-h5": ["live translation", "translator", "interpretation"],
    "c-hardware-h5": ["energy monitor", "power monitor", "home energy"],
    "c-hardware-h6": ["air quality", "weather station", "environment sensor"],
    "c-health-h5": ["hearing aid", "audiogram", "hearing test"],
    "c-climate-h5": ["ev battery", "battery health", "used battery"],
    "c-money-h5": ["acorns", "micro investing", "roundups", "spare change"],
    "c-food-h5": ["food waste", "expiry", "surplus food"],
    "c-civic-h5": ["see click fix", "city works", "fixmystreet"],
    "c-robotics-h5": ["mower", "automower", "lawn"],
    "c-access-h5": ["haptic", "smart cane", "navigation wearable"],
    "c-media-h5": ["immich", "photoprism", "photo sync", "photo gallery"],
    # ---- extra cards in existing fields
    "c-software-u6": ["undo send", "recall message", "unsend"],
    "c-climate-u6": ["flood risk", "flood map", "flood insurance"],
    "c-civic-u5": ["city council", "public meeting", "council meeting"],
    "c-media-u7": ["paywall", "news subscription"],
    "c-health-h6": ["wound care", "wound dressing", "tele dermatology"],
    # ---- law & justice
    "c-law-u0": ["plain language", "legal jargon", "law explained"],
    "c-law-u1": ["court docket", "court filing", "federal court"],
    "c-law-u2": ["legal insurance", "legal protection", "legal expenses"],
    "c-law-u3": ["small claims", "demand letter"],
    "c-law-h0": ["online dispute", "mediation", "arbitration"],
    "c-law-h1": ["legal aid", "pro bono", "lawyer referral"],
    "c-law-h2": ["tenant rights", "eviction", "landlord"],
    "c-law-h3": ["expungement", "record sealing", "criminal record"],
    # ---- textiles & clothing
    "c-textiles-u0": ["digital product passport", "garment passport", "product passport"],
    "c-textiles-u1": ["made to measure", "custom tailoring", "custom fit"],
    "c-textiles-u2": ["care label", "laundry symbol", "washing instruction"],
    "c-textiles-u3": ["wardrobe", "closet organizer", "outfit planner"],
    "c-textiles-h0": ["resale", "thrift", "second hand"],
    "c-textiles-h1": ["size chart", "fit finder", "body measurement"],
    "c-textiles-h2": ["textile recycling", "fabric recycling", "clothing recycling"],
    "c-textiles-h3": ["clothing repair", "tailor", "sewing service"],
    # ---- death & legacy
    "c-death-u0": ["probate", "estate administration", "letters testamentary"],
    "c-death-u1": ["heirloom", "keepsake", "family treasure"],
    "c-death-u2": ["organ donation", "body donation", "donor registry"],
    "c-death-u3": ["small estate", "probate avoid"],
    "c-death-h0": ["digital estate", "estate settlement", "after death"],
    "c-death-h1": ["advance directive", "living will", "palliative"],
    "c-death-h2": ["green burial", "human composting", "natural burial"],
    "c-death-h3": ["grief", "bereavement", "mourning"],
    # ---- ocean & water
    "c-ocean-u0": ["groundwater", "aquifer", "well water"],
    "c-ocean-u1": ["fishery", "fishing quota", "catch log"],
    "c-ocean-u2": ["rip current", "beach flag", "swim safety"],
    "c-ocean-u3": ["wetland", "mangrove", "land use change"],
    "c-ocean-h0": ["flood warning", "storm surge", "tide alert"],
    "c-ocean-h1": ["desalination", "water purification", "reverse osmosis"],
    "c-ocean-h2": ["sustainable seafood", "fish provenance", "seafood label"],
    "c-ocean-h3": ["river cleanup", "ocean plastic", "beach cleaning"],
    # ---- parenting & childcare
    "c-parenting-u0": ["childcare co op", "babysitting swap", "parent rota"],
    "c-parenting-u1": ["developmental milestone", "early intervention", "baby development"],
    "c-parenting-u2": ["parental leave", "maternity benefit", "self employed leave"],
    "c-parenting-u3": ["screen time", "parental control"],
    "c-parenting-h0": ["daycare", "childcare", "nursery school"],
    "c-parenting-h1": ["co parenting", "custody schedule", "shared custody"],
    "c-parenting-h2": ["pediatric", "child symptom", "baby health"],
    "c-parenting-h3": ["hand me down", "baby clothes", "kids items"],
    # ---- travel & borders
    "c-travel-u0": ["border wait", "customs queue", "border crossing"],
    "c-travel-u1": ["visa application", "residency permit", "immigration paperwork"],
    "c-travel-u2": ["travel insurance", "trip delay", "trip cancellation"],
    "c-travel-u3": ["document translation", "form translation", "sign translation"],
    "c-travel-h0": ["visa requirements", "visa policy", "timatic"],
    "c-travel-h1": ["travel wallet", "vaccine passport", "digital identity"],
    "c-travel-h2": ["overland", "train planner", "bus travel"],
    "c-travel-h3": ["lost luggage", "baggage tracking", "delayed bag"],
    # ---- space
    "c-space-u0": ["space weather", "aurora forecast", "gps outage"],
    "c-space-u1": ["satellite data", "earth observation", "imagery cooperative"],
    "c-space-u2": ["satellite insurance", "space insurance"],
    "c-space-u3": ["satellite bus", "cubesat", "spacecraft platform"],
    "c-space-h0": ["ground station", "satnogs", "satellite antenna"],
    "c-space-h1": ["satellite imagery", "ndvi", "crop monitoring"],
    "c-space-h2": ["space debris", "satellite conjunction", "debris avoidance"],
    "c-space-h3": ["satellite servicing", "orbital refueling", "on orbit servicing"],
    # ---- arts & culture
    "c-arts-u0": ["heritage craft", "dying craft", "artisan apprentice"],
    "c-arts-u1": ["endangered language", "language preservation", "language archive"],
    "c-arts-u2": ["public art", "art commission", "call for artists"],
    "c-arts-u3": ["setlist", "performance royalty", "session musician"],
    "c-arts-h0": ["artist rights", "art catalogue", "royalty management"],
    "c-arts-h1": ["art provenance", "certificate of authenticity"],
    "c-arts-h2": ["repatriation", "provenance research", "museum collection"],
    "c-arts-h3": ["gig listing", "live music", "tour planning"],
}


def pick_examples(rows, terms):
    def score(r):
        name = r[1].lower()
        for t in terms:
            if name.startswith(t):
                return 0
        for t in terms:
            if t in name:
                return 1
        return 2

    rows = sorted(rows, key=lambda r: (score(r), len(r[1])))
    picked, srcs = [], {}
    for source, name, _summary in rows:
        if len(picked) >= 3:
            break
        if srcs.get(source, 0) >= 2:
            continue
        srcs[source] = srcs.get(source, 0) + 1
        picked.append(f"{name} ({SOURCE_DISPLAY.get(source, source)})")
    return picked


def main():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    catalog_total = cur.execute("SELECT COUNT(*) FROM apps").fetchone()[0]

    checks = {}
    for cid, terms in SEEDS.items():
        cond = " OR ".join(
            "instr(' ' || lower(name || ' ' || coalesce(summary,'') || ' ' || "
            "coalesce(category,'') || ' ' || coalesce(developer,'')) || ' ', ?) > 0"
            for _ in terms)
        params = [f" {t.lower()} " for t in terms]
        rows = cur.execute(
            f"SELECT source, name, summary FROM apps WHERE {cond}", params
        ).fetchall()
        checks[cid] = {
            "queries": terms,
            "total": len(rows),
            "examples": pick_examples(rows, [t.lower() for t in terms]),
        }
        exs = "; ".join(checks[cid]["examples"][:2]) or "-"
        print(f"{cid:<18} {len(rows):>5}  {exs[:90]}")

    conn.close()
    payload = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%d"),
        "catalog_total": catalog_total,
        "method": "whole-token matches on name, summary, category and developer",
        "checks": checks,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=1)
    print(f"\nwrote {OUT}: {len(checks)} checks over {catalog_total:,} rows")


if __name__ == "__main__":
    main()
