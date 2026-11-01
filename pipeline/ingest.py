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
  ifixit    every hardware device in iFixit's repair catalog (open API)
  fda       regulated medical devices from openFDA (official US open data)
  arduino   embedded/firmware libraries from Arduino's library index (open)
  steam     Steam games and software via community search (per term)
  off       real food products from Open Food Facts (open API, capped)

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


# ---------------------------------------------------------------- ifixit
def fetch_ifixit():
    """Every hardware device in iFixit's repair catalog, from its open API.

    /api/2.0/categories returns the full nested device tree; every key is a
    real device, family or category people repair. Leaves get device URLs.
    """
    print("  downloading device tree...")
    tree = get_json("https://www.ifixit.com/api/2.0/categories", timeout=120)
    apps, seen = [], set()

    def walk(node, top):
        if isinstance(node, dict):
            for key, child in node.items():
                key = (key or "").strip()
                if not key:
                    continue
                walk(child, key if top is None else top)
        # a leaf device: record it once we know its top-level category

    def walk2(node, top, path):
        if isinstance(node, dict):
            for key, child in node.items():
                key = (key or "").strip()
                if not key or key in seen:
                    continue
                seen.add(key)
                cat = top or ""
                apps.append({
                    "id": key.lower().replace(" ", "-"),
                    "name": key,
                    "summary": f"Repair guide subject on iFixit ({path})" if child is None else f"Device family on iFixit ({path})",
                    "description": "",
                    "category": cat,
                    "developer": "",
                    "url": ("https://www.ifixit.com/Device/" + urllib.parse.quote(key)) if child is None else "",
                })
                walk2(child, cat, path if child is None else key)
        return

    walk2(tree, None, "")
    return save("ifixit", apps)


# ---------------------------------------------------------------- fda
def fetch_fda():
    """Regulated medical devices from openFDA's device classification database.

    Official US government open data — every device type the FDA regulates.
    """
    apps, seen, skip = [], set(), 0
    while True:
        url = f"https://api.fda.gov/device/classification.json?limit=100&skip={skip}"
        try:
            data = get_json(url)
        except Exception as e:  # noqa: BLE001
            print(f"    skip={skip}: {e}", file=sys.stderr)
            break
        results = data.get("results") or []
        if not results:
            break
        for r in results:
            name = (r.get("device_name") or "").strip()
            if not name or name in seen:
                continue
            seen.add(name)
            reg = (r.get("regulation_number") or "").strip()
            part = reg.split(".")[0] if reg else ""
            apps.append({
                "id": r.get("product_code") or name.lower(),
                "name": name,
                "summary": f"FDA class {r.get('device_class', '?')} regulated device type",
                "description": "",
                "category": (r.get("medical_specialty") or "").strip() or "Medical devices",
                "developer": "",
                "url": (f"https://www.ecfr.gov/current/title-21/chapter-I/subchapter-H/part/{part}"
                        if part else ""),
            })
        skip += len(results)
        print(f"    {skip} of {data.get('meta', {}).get('results', {}).get('total', '?')}")
        time.sleep(0.3)
        if skip > 20000:
            break
    return save("fda", apps)


# ---------------------------------------------------------------- arduino
def fetch_arduino():
    """Embedded/firmware libraries from Arduino's public library index."""
    data = get_json("https://downloads.arduino.cc/libraries/library_index.json", timeout=120)
    libs, seen = {}, set()
    for lib in data.get("libraries", []):
        name = (lib.get("name") or "").strip()
        if not name:
            continue
        if name in libs:  # keep the newest release (index is version-sorted)
            continue
        libs[name] = lib
    apps = []
    for name, lib in libs.items():
        if name.lower() in seen:
            continue
        seen.add(name.lower())
        cat = (lib.get("category") or "").strip()
        apps.append({
            "id": name,
            "name": name,
            "summary": clean(lib.get("sentence"), 300),
            "description": clean(lib.get("paragraph")),
            "category": cat or "Embedded library",
            "developer": clean(lib.get("owner") or "", 100),
            "url": (lib.get("website") or "").strip(),
        })
    return save("arduino", apps)


STEAM_TERMS = [
    "games", "rpg", "strategy", "simulation", "roguelike", "puzzle", "platformer",
    "shooter", "horror", "racing", "sports", "football", "chess", "card game",
    "city builder", "farming", "flight simulator", "space", "zombies", "anime",
    "pixel", "vr", "survival", "sandbox", "tower defense", "metroidvania",
    "golf", "rhythm", "typing", "programming", "hacking", "cooking", "fishing",
    "war", "multiplayer", "co-op", "mmorpg", "darts", "pool", "wrestling",
    "skateboarding", "skiing", "baseball", "cricket", "tennis", "boxing",
]


# ---------------------------------------------------------------- steam
def fetch_steam():
    """Steam games and software via the community search API, per term.

    The official GetAppList endpoint is name-only; this surfaces the popular
    titles with logos for a spread of gaming and software terms.
    """
    apps, seen = [], set()
    for i, term in enumerate(STEAM_TERMS):
        url = "https://steamcommunity.com/actions/SearchApps/" + urllib.parse.quote(term)
        try:
            results = get_json(url)
        except Exception as e:  # noqa: BLE001
            print(f"    {term}: {e}", file=sys.stderr)
            continue
        got = 0
        for r in results or []:
            aid = str(r.get("appid") or "")
            name = (r.get("name") or "").strip()
            if not aid or not name or aid in seen:
                continue
            seen.add(aid)
            apps.append({
                "id": aid,
                "name": name,
                "summary": "",
                "description": "",
                "category": "Steam game / software",
                "developer": "",
                "url": "https://store.steampowered.com/app/" + aid,
            })
            got += 1
        print(f"    [{i + 1}/{len(STEAM_TERMS)}] {term}: {got}")
        time.sleep(0.8)
    return save("steam", apps)


# ---------------------------------------------------------------- off
def fetch_off(pages=60):
    """Real food products from Open Food Facts' open API (capped)."""
    apps, seen, fails = [], set(), 0
    for page in range(1, pages + 1):
        q = urllib.parse.urlencode({
            "page": page, "page_size": 100,
            "fields": "code,product_name,brands,categories_en",
        })
        url = "https://world.openfoodfacts.org/api/v2/search?" + q
        try:
            data = get_json(url)
        except Exception as e:  # noqa: BLE001
            print(f"    page {page}: {e}", file=sys.stderr)
            fails += 1
            if fails >= 3:
                break
            continue
        fails = 0
        products = data.get("products") or []
        if not products:
            break
        new = 0
        for r in products:
            name = (r.get("product_name") or "").strip()
            if not name:
                continue
            key = (name.lower(), (r.get("brands") or "").lower())
            if key in seen:
                continue
            seen.add(key)
            code = (r.get("code") or "").strip()
            cats = (r.get("categories_en") or "").split(",")
            apps.append({
                "id": code,
                "name": name,
                "summary": clean(r.get("brands"), 150),
                "description": "",
                "category": (cats[0].replace("en:", "").strip() if cats and cats[0] else "Food product"),
                "developer": clean(r.get("brands"), 100),
                "url": f"https://world.openfoodfacts.org/product/{code}" if code else "",
            })
            new += 1
        print(f"    page {page}: +{new}")
        if new < 10:
            break
        time.sleep(1.5)
    return save("off", apps)


SOURCES = {
    "flathub": fetch_flathub,
    "fdroid": fetch_fdroid,
    "itunes": fetch_itunes,
    "npm": fetch_npm,
    "play": fetch_play,
    "ifixit": fetch_ifixit,
    "fda": fetch_fda,
    "arduino": fetch_arduino,
    "steam": fetch_steam,
    "off": fetch_off,
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
