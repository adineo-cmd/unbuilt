#!/usr/bin/env python3
"""Collect "already built" evidence from app and software catalogs.

Each fetcher writes one normalized JSON file into data/raw/:

    {"source": "flathub", "apps": [{
        "id": ..., "name": ..., "summary": ..., "description": ...,
        "category": ..., "developer": ..., "url": ...
    }]}

Sources:
  flathub   full catalog, from Flathub's public appstream dump (open)
  fdroid    full catalog, from F-Droid's public index (open)
  itunes    App Store top results per category via the official Search API
  play      Google Play top-per-category via google-play-scraper (capped,
            rate-limited; Play has no official bulk API — use modestly,
            it is against Google's ToS to scrape aggressively)
  npm       npm registry top packages by popularity (open search API)

Usage:
  python3 pipeline/ingest.py                  # everything except play
  python3 pipeline/ingest.py --only flathub,fdroid
  python3 pipeline/ingest.py --only play      # needs: pip install google-play-scraper
"""
import argparse
import gzip
import io
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(os.path.dirname(HERE), "data", "raw")
UA = "UnbuiltCensus/1.0 (catalog metadata for a personal research index; +https://github.com/adineo-cmd/unbuilt)"


def http_get(url, timeout=60, tries=3):
    last = None
    for attempt in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept-Encoding": "gzip"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                data = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    data = gzip.decompress(data)
                return data
        except Exception as e:  # noqa: BLE001 - retry any network hiccup
            last = e
            wait = 2 * (attempt + 1)
            print(f"    retry in {wait}s ({e})", file=sys.stderr)
            time.sleep(wait)
    raise RuntimeError(f"failed to fetch {url}: {last}")


def get_json(url, timeout=60):
    return json.loads(http_get(url, timeout=timeout))


def clean(text, limit=800):
    if not text:
        return ""
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&[a-z]+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit]


def save(name, apps):
    os.makedirs(RAW, exist_ok=True)
    path = os.path.join(RAW, name + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({"source": name, "apps": apps}, fh, ensure_ascii=False)
    print(f"  saved {len(apps)} apps -> {path}")
    return apps


# ---------------------------------------------------------------- flathub
def fetch_flathub():
    """Full Flathub catalog from the public appstream collection dump."""
    url = "https://dl.flathub.org/repo/appstream/x86_64/appstream.xml.gz"
    print("  downloading appstream dump...")
    raw = http_get(url, timeout=120)
    if raw[:2] == b"\x1f\x8b":  # the dump itself is a .gz file
        raw = gzip.decompress(raw)
    apps, seen = [], set()
    for event, elem in ET_iterparse(io.BytesIO(raw)):
        if not elem.tag.endswith("component"):
            continue
        app_id = (elem.findtext("id") or "").strip()
        name = (elem.findtext("name") or "").strip()
        if not app_id or not name or app_id in seen:
            continue
        seen.add(app_id)
        dev = elem.findtext("developer_name") or ""
        homepage = ""
        for u in elem.findall("url"):
            if u.get("type") == "homepage":
                homepage = (u.text or "").strip()
        cats = [c.text for c in elem.findall("categories/category") if c.text]
        apps.append({
            "id": app_id,
            "name": name,
            "summary": clean(elem.findtext("summary"), 300),
            "description": clean(elem.findtext("description")),
            "category": cats[0] if cats else "",
            "developer": clean(dev, 100),
            "url": homepage or "https://flathub.org/apps/" + app_id,
        })
        elem.clear()
    return save("flathub", apps)


def ET_iterparse(buf):
    import xml.etree.ElementTree as ET
    return ET.iterparse(buf, events=("end",))


# ---------------------------------------------------------------- fdroid
def fetch_fdroid():
    """Full F-Droid catalog from the public package index."""
    for url, version in (("https://f-droid.org/repo/index-v2.json", 2),
                         ("https://f-droid.org/repo/index-v1.json", 1)):
        try:
            print(f"  downloading F-Droid index-v{version}...")
            data = get_json(url, timeout=300)
            break
        except Exception as e:  # noqa: BLE001
            print(f"    index-v{version} failed: {e}", file=sys.stderr)
            data = None
    if data is None:
        raise RuntimeError("could not fetch any F-Droid index")

    apps, seen = [], set()
    if version == 2:
        def loc_text(v):
            # index-v2 stores text fields as {locale: text}
            if isinstance(v, dict):
                return v.get("en-US") or v.get("en-GB") or (next(iter(v.values())) if v else "")
            return v or ""

        for pkg, info in (data.get("packages") or {}).items():
            md = info.get("metadata") or {}
            name = (loc_text(md.get("name")) or "").strip()
            if not name or pkg in seen:
                continue
            seen.add(pkg)
            cats = md.get("categories") or []
            apps.append({
                "id": pkg,
                "name": name,
                "summary": clean(loc_text(md.get("summary")), 300),
                "description": clean(loc_text(md.get("description"))),
                "category": cats[0] if cats else "",
                "developer": clean(md.get("authorName") or "", 100),
                "url": md.get("webSite") or ("https://f-droid.org/packages/" + pkg),
            })
    else:
        for a in data.get("apps", []):
            pkg = a.get("packageName") or ""
            name = (a.get("name") or "").strip()
            if not name or pkg in seen:
                continue
            seen.add(pkg)
            cats = a.get("categories") or []
            apps.append({
                "id": pkg,
                "name": name,
                "summary": clean(a.get("summary"), 300),
                "description": clean(a.get("description")),
                "category": cats[0] if cats else "",
                "developer": clean(a.get("authorName") or a.get("site") or "", 100),
                "url": a.get("site") or ("https://f-droid.org/packages/" + pkg),
            })
    return save("fdroid", apps)


# ---------------------------------------------------------------- itunes
ITUNES_GENRES = [
    "Productivity", "Developer Tools", "Graphics & Design", "Education", "Health & Fitness",
    "Finance", "Social Networking", "Photo & Video", "Music", "Navigation", "Utilities",
    "News", "Books", "Business", "Travel", "Food & Drink", "Shopping", "Weather",
    "Entertainment", "Lifestyle", "Medical", "Sports", "Reference", "Games",
]


def fetch_itunes():
    """App Store apps via Apple's official (rate-limited) Search API."""
    apps, seen = [], set()
    for i, genre in enumerate(ITUNES_GENRES):
        q = urllib.parse.urlencode({
            "term": genre, "country": "us", "media": "software",
            "entity": "software", "limit": 200,
        })
        url = "https://itunes.apple.com/search?" + q
        try:
            data = get_json(url)
        except Exception as e:  # noqa: BLE001
            print(f"    {genre}: {e}", file=sys.stderr)
            continue
        got = 0
        for r in data.get("results", []):
            tid = r.get("trackId")
            name = (r.get("trackName") or "").strip()
            if not tid or not name or tid in seen:
                continue
            seen.add(tid)
            apps.append({
                "id": str(tid),
                "name": name,
                "summary": clean(r.get("description"), 300),
                "description": clean(r.get("description")),
                "category": r.get("primaryGenreName") or "",
                "developer": clean(r.get("sellerName") or r.get("artistName") or "", 100),
                "url": r.get("trackViewUrl") or "",
            })
            got += 1
        print(f"    {genre}: {got}")
        time.sleep(3.5)  # Apple's Search API allows roughly 20 calls/minute
    return save("itunes", apps)


# ---------------------------------------------------------------- npm
NPM_TERMS = [
    "tool", "app", "server", "cli", "test", "react", "vue", "web", "http", "json",
    "data", "database", "sql", "api", "ui", "css", "game", "ai", "image", "video",
    "audio", "crypto", "chart", "date", "text", "file", "math", "parser", "state",
    "component", "browser", "network", "security", "auth", "cache", "log", "string",
    "editor", "markdown", "pdf", "calendar", "map", "search", "build", "compiler",
]


def fetch_npm(pages=1):
    """Popular npm packages via the registry's public search API.

    The API requires a text query, so we page the top popularity-ranked
    results across a spread of common software keywords.
    """
    apps, seen = [], set()
    per = 250
    for term in NPM_TERMS:
        q = urllib.parse.urlencode({
            "text": term, "size": per, "from": 0, "popularity": "1.0",
        })
        url = "https://registry.npmjs.org/-/v1/search?" + q
        try:
            data = get_json(url)
        except Exception as e:  # noqa: BLE001
            print(f"    {term}: {e}", file=sys.stderr)
            continue
        objs = data.get("objects") or []
        new = 0
        for o in objs:
            p = o.get("package") or {}
            name = p.get("name") or ""
            if not name or name in seen:
                continue
            seen.add(name)
            links = p.get("links") or {}
            apps.append({
                "id": name,
                "name": name,
                "summary": clean(p.get("description"), 300),
                "description": clean(p.get("description")),
                "category": "npm package",
                "developer": clean((p.get("publisher") or {}).get("username") or "", 100),
                "url": links.get("npm") or ("https://www.npmjs.com/package/" + name),
            })
            new += 1
        print(f"    {term}: +{new}")
        if not new:
            break
        time.sleep(0.4)
    return save("npm", apps)


# ---------------------------------------------------------------- play
PLAY_TERMS = [
    "notes", "to do list", "habit tracker", "calendar", "task manager", "reminder",
    "camera", "photo editor", "video editor", "music player", "podcast", "voice recorder",
    "fitness", "meditation", "sleep", "meal planner", "water reminder", "weight tracker",
    "budget", "expense tracker", "bank", "wallet", "invoice", "tax",
    "messenger", "email client", "browser", "weather", "map", "navigation", "translator",
    "dictionary", "document scanner", "pdf reader", "password manager", "vpn",
    "launcher", "keyboard", "flashlight", "calculator", "whiteboard", "flashcards",
    "language learning", "news", "shopping list", "food delivery", "taxi", "inventory",
]


def fetch_play(n_hits=150):
    """Google Play apps via google-play-scraper's public search, capped.

    Google offers no bulk API and scraping all of it would violate its terms,
    so the pipeline takes popularity-ranked search results for a spread of
    app-domain terms and stops there. Keep the caps modest; data ages.
    """
    try:
        from google_play_scraper import search
    except ImportError:
        sys.exit("google-play-scraper is not installed:  pip install google-play-scraper")

    apps, seen = [], set()
    print(f"  searching {len(PLAY_TERMS)} terms (n={n_hits})...")
    for i, term in enumerate(PLAY_TERMS):
        try:
            results = search(term, n_hits=n_hits, lang="en", country="us")
        except Exception as e:  # noqa: BLE001
            print(f"    {term}: {e}", file=sys.stderr)
            continue
        got = 0
        for r in results:
            aid = r.get("appId") or ""
            name = (r.get("title") or "").strip()
            if not aid or not name or aid in seen:
                continue
            seen.add(aid)
            apps.append({
                "id": aid,
                "name": name,
                "summary": clean(r.get("summary") or r.get("description"), 300),
                "description": clean(r.get("description") or r.get("summary")),
                "category": r.get("genre") or "",
                "developer": clean(r.get("developer") or "", 100),
                "url": "https://play.google.com/store/apps/details?id=" + aid,
            })
            got += 1
        print(f"    [{i + 1}/{len(PLAY_TERMS)}] {term}: {got}")
        time.sleep(1)
    return save("play", apps)


SOURCES = {
    "flathub": fetch_flathub,
    "fdroid": fetch_fdroid,
    "itunes": fetch_itunes,
    "npm": fetch_npm,
    "play": fetch_play,
}


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--only", help="comma-separated subset: flathub,fdroid,itunes,npm,play")
    ap.add_argument("--list", action="store_true", help="list sources and exit")
    args = ap.parse_args()
    if args.list:
        print("\n".join(SOURCES))
        return
    chosen = (args.only.split(",") if args.only else
              [s for s in SOURCES if s != "play"])  # play is opt-in: see --only play
    for name in chosen:
        print(f"[{name}]")
        SOURCES[name]()


if __name__ == "__main__":
    main()
