#!/usr/bin/env python3
"""SEO and integrity checks for the static site. Run before every commit:

    python3 tools/check-site.py

Exits with status 1 and lists the problems if any check fails. It checks:
  1. one canonical per indexable page, on https://www.adarshprojects.co.in, equal to the page URL
     (with a trailing slash), and og:url matching it
  2. every JSON-LD block parses, and no Product lacks offers
  3. every <img> has non-empty alt, width and height
  4. sitemap.xml lists only www URLs of real, indexable pages
  5. one <h1>, a <title> under 60 characters and a meta description under 160 on each indexable page
  6. every internal link and image path points to a file that exists
  7. no URL on the non-www host anywhere in the pages
  8. outbound links go only to government sites (*.gov.in, *.nic.in, rbi.org.in), and project
     pages have none at all (WhatsApp chat links are allowed everywhere)
"""
import html
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.adarshprojects.co.in"
GOV = re.compile(r"(\.gov\.in|\.nic\.in|^(www\.)?rbi\.org\.in)$")
SKIP_DIRS = {"partials", "tools", "media", "covers", "brand", "brochures", "assets", ".git", "node_modules"}
problems = []


def bad(page, msg):
    problems.append("%s: %s" % (page, msg))


def pages():
    for base, dirs, files in os.walk(ROOT):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for f in files:
            if f.endswith(".html"):
                yield os.path.relpath(os.path.join(base, f), ROOT)


def url_for(rel):
    if rel == "index.html":
        return SITE + "/"
    if rel.endswith("/index.html"):
        return SITE + "/" + rel[: -len("index.html")]
    return None  # e.g. 404.html


def exists(path):
    path = path.split("#")[0].split("?")[0]
    if not path.startswith("/"):
        return True
    p = os.path.join(ROOT, path.lstrip("/"))
    if path.endswith("/"):
        return os.path.isfile(os.path.join(p, "index.html"))
    return os.path.isfile(p) or os.path.isfile(os.path.join(p, "index.html"))


def all_types(node, out):
    if isinstance(node, list):
        for n in node:
            all_types(n, out)
    elif isinstance(node, dict):
        if "@type" in node:
            t = node["@type"]
            out.append((t if isinstance(t, list) else [t], node))
        for v in node.values():
            all_types(v, out)


indexable = set()
for rel in sorted(pages()):
    h = open(os.path.join(ROOT, rel), encoding="utf-8").read()
    noindex = bool(re.search(r'<meta name="robots" content="[^"]*noindex', h))
    own = url_for(rel)
    if own and not noindex:
        indexable.add(own)

    if "//adarshprojects.co.in" in h:
        bad(rel, "non-www URL in page")

    canon = re.findall(r'<link rel="canonical" href="([^"]+)"', h)
    if not noindex:
        if len(canon) != 1:
            bad(rel, "%d canonical tags" % len(canon))
        elif own and canon[0] != own:
            bad(rel, "canonical %s ≠ page URL %s" % (canon[0], own))
        ogu = re.search(r'<meta property="og:url" content="([^"]+)"', h)
        if canon and ogu and ogu.group(1) != canon[0]:
            bad(rel, "og:url ≠ canonical")

        titles = re.findall(r"<title>(.*?)</title>", h, re.S)
        if len(titles) != 1:
            bad(rel, "%d <title> tags" % len(titles))
        elif len(html.unescape(titles[0])) > 60:
            bad(rel, "title is %d chars (max 60)" % len(html.unescape(titles[0])))
        desc = re.search(r'<meta name="description" content="([^"]*)"', h)
        if not desc or not desc.group(1).strip():
            bad(rel, "no meta description")
        elif len(html.unescape(desc.group(1))) > 160:
            bad(rel, "description is %d chars (max 160)" % len(html.unescape(desc.group(1))))
        h1 = len(re.findall(r"<h1\b", h))
        if h1 != 1:
            bad(rel, "%d <h1> tags" % h1)

    for block in re.findall(r'<script type="application/ld\+json"[^>]*>(.*?)</script>', h, re.S):
        try:
            data = json.loads(block)
        except ValueError as e:
            bad(rel, "JSON-LD does not parse: %s" % e)
            continue
        found = []
        all_types(data, found)
        for t, node in found:
            if "Product" in t and not node.get("offers"):
                bad(rel, "Product without offers (%s)" % node.get("name"))

    for tag in re.findall(r"<img\b[^>]*>", h):
        src = (re.search(r'\ssrc="([^"]+)"', tag) or [None, "?"])[1]
        alt = re.search(r'\salt="([^"]*)"', tag)
        if not alt or not alt.group(1).strip():
            bad(rel, "empty alt on %s" % src)
        if not re.search(r'\swidth="\d+"', tag) or not re.search(r'\sheight="\d+"', tag):
            bad(rel, "missing width/height on %s" % src)
        for p in [src] + re.findall(r"(/[^\s,\"]+)\s+\d+w", tag):
            if not exists(p):
                bad(rel, "missing image file %s" % p)

    body = re.sub(r"<script.*?</script>", "", h, flags=re.S)
    is_project = rel.startswith("projects/") and rel != "projects/index.html"
    for ext in re.findall(r'<a\b[^>]*href="(https?://[^"]+)"', body):
        host = re.match(r"https?://([^/]+)", ext).group(1)
        if host == "wa.me":
            continue
        if is_project or rel == "projects/index.html":
            bad(rel, "outbound link on a project page: %s" % ext)
        elif not GOV.search(host):
            bad(rel, "outbound link to a non-government site: %s" % ext)
    for href in re.findall(r'\shref="(/[^"]*)"', body):
        if href.startswith("//"):
            continue
        if not exists(html.unescape(href)):
            bad(rel, "broken internal link %s" % href)

sm = open(os.path.join(ROOT, "sitemap.xml"), encoding="utf-8").read()
locs = re.findall(r"<loc>([^<]+)</loc>", sm)
for loc in locs:
    if not loc.startswith(SITE + "/"):
        bad("sitemap.xml", "non-www URL %s" % loc)
    elif loc not in indexable:
        bad("sitemap.xml", "%s is not an indexable page" % loc)
for img in re.findall(r"<image:loc>([^<]+)</image:loc>", sm):
    if not img.startswith(SITE + "/") or not exists(img[len(SITE):]):
        bad("sitemap.xml", "bad image %s" % img)
missing = sorted(indexable - set(locs))
for m in missing:
    bad("sitemap.xml", "indexable page not listed: %s" % m)

if problems:
    print("\n".join(problems))
    print("\n%d problem(s)." % len(problems))
    sys.exit(1)
print("All checks passed: %d pages, %d sitemap URLs." % (len(indexable), len(locs)))
