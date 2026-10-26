#!/usr/bin/env python3
"""Bundle docs/ into one self-contained HTML file.

The published site loads its data with fetch(), which browsers block on
file:// URLs. This build inlines the stylesheet, the script and every data
payload so the result opens by double-clicking, with no server and no network
beyond the webfonts (which fall back cleanly if offline).

Usage:  python scripts/build_preview.py [-o OUTPUT.html]
"""

import argparse
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS = os.path.join(ROOT, "docs")
DATA = os.path.join(DOCS, "data")


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def safe_json(obj):
    """JSON safe to embed in a <script> block."""
    return (
        json.dumps(obj, ensure_ascii=False, separators=(",", ":"))
        .replace("<", "\\u003c")
        .replace(">", "\\u003e")
        .replace("&", "\\u0026")
        .replace(" ", "\\u2028")
        .replace(" ", "\\u2029")
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default=os.path.join(ROOT, "asurre-preview.html"))
    args = ap.parse_args()

    html = read(os.path.join(DOCS, "index.html"))
    css = read(os.path.join(DOCS, "styles.css"))
    js = read(os.path.join(DOCS, "app.js"))

    payloads = {}
    for fn in sorted(os.listdir(DATA)):
        if fn.endswith(".json"):
            with open(os.path.join(DATA, fn), encoding="utf-8") as fh:
                payloads[fn[:-5]] = json.load(fh)

    html = html.replace(
        '<link rel="stylesheet" href="styles.css">',
        f"<style>\n{css}\n</style>",
    )
    html = html.replace(
        '<script src="app.js"></script>',
        f"<script>window.__ASURRE_DATA__ = {safe_json(payloads)};</script>\n"
        f"<script>\n{js}\n</script>",
    )

    # The repository links in the footer are fine as absolute URLs; the banner
    # below makes clear this file is a local preview, not the published site.
    html = html.replace(
        '<main>',
        '<div class="preview-banner">Local preview — a single self-contained file. '
        'The published version lives under <code>docs/</code> and loads its data '
        'from <code>docs/data/</code>.</div>\n<main>',
    )
    html = html.replace(
        "</style>",
        """
.preview-banner {
  background: var(--machine-wash);
  border-bottom: 1px solid var(--rule);
  color: var(--ink-soft);
  font-size: 12.5px;
  padding: 8px var(--gutter);
  text-align: center;
}
</style>""",
    )

    with open(args.output, "w", encoding="utf-8") as fh:
        fh.write(html)

    size = os.path.getsize(args.output)
    print(f"{args.output}  {size/1024/1024:.1f} MiB  ({len(payloads)} payloads inlined)")


if __name__ == "__main__":
    main()
