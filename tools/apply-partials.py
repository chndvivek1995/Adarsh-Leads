#!/usr/bin/env python3
"""Stamp the shared header / footer / sticky-CTA into every page.

Edit these three files only:
    partials/header.html
    partials/footer.html
    partials/sticky-cta.html

then run this once from the site folder:

    Windows:  py tools\\apply-partials.py
    Mac:      python3 tools/apply-partials.py

Every .html file is rewritten between the marker comments, e.g.
    <!-- HEADER:START --> … <!-- HEADER:END -->
On the first run the markers are added automatically around the existing
<header>, <footer> and the sticky mobile bar.

Why stamping instead of loading the header with JavaScript: the menu and
footer links stay inside the HTML, so search engines always see them.
"""
import hashlib
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PARTS = [
    ("HEADER", "partials/header.html", re.compile(r"<header[^>]*>.*?</header>", re.S)),
    ("FOOTER", "partials/footer.html", re.compile(r"<footer[^>]*>.*?</footer>", re.S)),
    ("STICKY", "partials/sticky-cta.html",
     re.compile(r'<div class="fixed inset-x-0 bottom-0 z-40(?:(?!</div>).)*</div>', re.S)),
]

# style.css and site.js are cached for a year (vercel.json), so every page links them
# with ?v=<content hash>. A changed file gets a new hash and browsers fetch it again.
ASSETS = ["assets/css/style.css", "assets/js/site.js"]

def asset_versions():
    out = []
    for a in ASSETS:
        h = hashlib.sha1(open(os.path.join(ROOT, a), "rb").read()).hexdigest()[:10]
        out.append((re.compile(r'/%s(?:\?v=[0-9a-f]+)?"' % re.escape(a)), '/%s?v=%s"' % (a, h)))
    return out

def html_files():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in ("partials", "tools", "media", "covers", "brand", "brochures", "assets", ".git")]
        for f in files:
            if f.endswith(".html"):
                yield os.path.join(base, f)

def main():
    parts = []
    for name, path, finder in PARTS:
        full = os.path.join(ROOT, path)
        if not os.path.exists(full):
            print("! missing", path, "— skipped")
            continue
        parts.append((name, open(full, encoding="utf-8").read().strip(), finder))

    versions = asset_versions()
    changed = 0
    for f in sorted(html_files()):
        src = open(f, encoding="utf-8").read()
        out = src
        for pat, repl in versions:
            out = pat.sub(repl, out)
        for name, content, finder in parts:
            block = "<!-- %s:START -->%s<!-- %s:END -->" % (name, content, name)
            marker = re.compile(r"<!-- %s:START -->.*?<!-- %s:END -->" % (name, name), re.S)
            if marker.search(out):
                out = marker.sub(lambda _m: block, out, count=1)
            else:
                m = finder.search(out)
                if m:
                    out = out[:m.start()] + block + out[m.end():]
                else:
                    print("  · %s: no %s found" % (os.path.relpath(f, ROOT), name))
        if out != src:
            open(f, "w", encoding="utf-8").write(out)
            changed += 1
            print("updated", os.path.relpath(f, ROOT))
    print("\n%d file(s) updated." % changed)

if __name__ == "__main__":
    sys.exit(main())
