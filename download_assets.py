#!/usr/bin/env python3
"""
Download same-origin assets referenced by the supplied Apple homepage HTML.
Use only for personal learning/research. Requires Python 3 and an internet connection.
"""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse, unquote
from urllib.request import Request, urlopen
import re, time

ROOT = Path(__file__).resolve().parent
HTML_FILE = ROOT / "apple.com-source-beautified.html"
ASSET_DIR = ROOT / "assets"
BASE_URL = "https://www.apple.com/"
ALLOWED_HOSTS = {"www.apple.com", "apple.com"}
MAX_ROUNDS = 8

class AssetParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls = set()
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for key in ("src", "href", "poster", "data-src"):
            val = a.get(key)
            if val and not val.startswith(("data:", "javascript:", "mailto:", "#")):
                self.urls.add(val)
        for val in (a.get("srcset") or "").split(","):
            item = val.strip().split()
            if item:
                self.urls.add(item[0])
        if tag == "meta" and (a.get("property") in ("og:image", "og:video") or a.get("name") == "twitter:image"):
            if a.get("content"):
                self.urls.add(a["content"])

def local_path(url):
    p = urlparse(url)
    path = unquote(p.path or "/")
    if path.endswith("/") or not Path(path).suffix:
        path += "/index.html"
    # Keep URL query variants distinct when necessary.
    if p.query:
        import hashlib
        suffix = Path(path).suffix
        path = path[:-len(suffix)] + "_" + hashlib.sha1(p.query.encode()).hexdigest()[:10] + suffix
    return ASSET_DIR / p.netloc / path.lstrip("/")

def is_allowed(url):
    p = urlparse(url)
    return p.scheme in ("http", "https") and p.hostname in ALLOWED_HOSTS

def fetch(url):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; PersonalAssetStudy/1.0)"})
    with urlopen(req, timeout=25) as resp:
        return resp.read(), resp.headers.get("Content-Type", "")

def main():
    if not HTML_FILE.exists():
        raise SystemExit("Missing apple.com-source-beautified.html")
    html = HTML_FILE.read_text(encoding="utf-8", errors="replace")
    parser = AssetParser()
    parser.feed(html)
    queue = set()
    for raw in parser.urls:
        u = urljoin(BASE_URL, raw)
        if is_allowed(u) and urlparse(u).path != "/":
            queue.add(u)

    downloaded = set()
    for round_no in range(MAX_ROUNDS):
        if not queue:
            break
        current = sorted(queue - downloaded)
        queue.clear()
        if not current:
            break
        print(f"Round {round_no+1}: {len(current)} resource(s)")
        for url in current:
            try:
                data, content_type = fetch(url)
                dest = local_path(url)
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(data)
                downloaded.add(url)
                print(f"  OK  {url}")
                # Discover CSS imports and url(...) dependencies.
                if "text/css" in content_type or urlparse(url).path.endswith(".css"):
                    css = data.decode("utf-8", errors="replace")
                    found = set(re.findall(r'@import\s+(?:url\()?["\']?([^"\')\s;]+)', css, re.I))
                    found.update(re.findall(r'url\(\s*["\']?([^"\')]+)', css, re.I))
                    for raw in found:
                        if raw.startswith(("data:", "#")):
                            continue
                        dep = urljoin(url, raw.strip())
                        if is_allowed(dep) and dep not in downloaded:
                            queue.add(dep)
            except Exception as e:
                print(f"  FAIL {url} ({e})")
            time.sleep(0.08)

    # Make an asset manifest even when some requests fail.
    manifest = ROOT / "asset-manifest.txt"
    manifest.write_text(
        "Requested/downloaded same-origin resources for personal study\n"
        f"Downloaded: {len(downloaded)}\n\n" +
        "\n".join(sorted(downloaded)) + "\n",
        encoding="utf-8"
    )
    print(f"\nFinished. Downloaded {len(downloaded)} resources.")
    print("Files are in the assets/ folder. Some site features may still need Apple's live services/CDNs.")

if __name__ == "__main__":
    main()
