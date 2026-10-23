# Apple homepage source package

Included:
- `apple.com-source-beautified.html` — the HTML file you uploaded.
- `download_assets.py` — downloads same-origin CSS, JavaScript, and other linked resources from `www.apple.com` into `assets/`, and follows CSS `@import` / `url(...)` references.
- `asset-manifest.txt` — created after running the downloader.

## Get the CSS and JS assets

1. Extract this ZIP.
2. Install Python 3 if needed.
3. Make sure your computer is connected to the internet.
4. Open Terminal / PowerShell in this folder.
5. Run:

   `python download_assets.py`

The downloader can only retrieve resources that Apple serves publicly and may miss resources hosted on other domains, dynamic/API content, or assets protected by server rules. The original HTML may reference changing versioned paths, so some files may no longer be available.

This package does not contain Apple's full live website or guarantee an exact offline clone. It is a starting point for personal learning and inspection. Respect Apple's terms and applicable copyright rules.
