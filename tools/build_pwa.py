"""Build the offline app (PWA) for GitHub Pages from the question bank.

Usage:  python3 -I build_pwa.py <fragebank-dir> <site-dir>

Reads <fragebank-dir>/index.html (the app) and <fragebank-dir>/data/*.json
(run build.py first), and writes into <site-dir>:
  index.html, manifest.webmanifest, sw.js, icons/, .nojekyll
The service-worker cache name is a hash of the content, so every new build
replaces the old offline copy on the next start of the app.
Does not change anything in <fragebank-dir>.
"""
import hashlib, json, os, re, shutil, sys

root, site = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
os.makedirs(site, exist_ok=True)

# ---- questions: embed freshly from data/ (same as embed.py, but in memory) ----
idx = json.load(open(os.path.join(root, "data/index.json"), encoding="utf8"))
decks = {d["file"]: json.load(open(os.path.join(root, "data", d["file"]), encoding="utf8"))
         for d in idx["decks"] if d.get("file")}
blob = json.dumps({"index": idx, "decks": decks}, ensure_ascii=False).replace("</", "<\\/")
nq = sum(len(d["questions"]) for d in decks.values())

body = open(os.path.join(root, "index.html"), encoding="utf8").read()
body = re.sub(r'<script type="application/json" id="qdata">.*?</script>\n', "", body, flags=re.S)
body = re.sub(r'<meta name="claude:[^>]*>\n?', "", body)
m = re.match(r"\s*<title>.*?</title>\n", body, flags=re.S)
title = m.group(0) if m else "<title>NCH Fragebank</title>\n"
body = body[m.end():] if m else body
head_extra, body = body.split("</style>", 1)  # fonts + style block stay in <head>
head_extra += "</style>\n"

version = hashlib.sha256((body + blob + head_extra).encode("utf8")).hexdigest()[:10]

footer = open(os.path.join(here, "footer.html"), encoding="utf8").read()
footer = footer.replace("{{VERSION}}", version).replace("{{COUNT}}", str(nq))
qdata = '<script type="application/json" id="qdata">' + blob + "</script>\n"
assert "\n<script>\n(function () {" in body, "app script marker not found"
body = body.replace("\n<script>\n(function () {", "\n" + footer + qdata + "<script>\n(function () {", 1)

html = f"""<!doctype html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
{title}<meta name="theme-color" content="#0e5a70">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-title" content="NCH Fragebank">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="robots" content="noindex">
<link rel="manifest" href="manifest.webmanifest">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<link rel="apple-touch-icon" href="icons/apple-touch-icon.png">
{head_extra}</head>
<body>
{body}
</body>
</html>
"""
open(os.path.join(site, "index.html"), "w", encoding="utf8").write(html)

manifest = {
    "name": "NCH Fragebank", "short_name": "NCH Fragen", "id": "./", "start_url": "./",
    "scope": "./", "display": "standalone", "background_color": "#f2f5f6", "theme_color": "#0e5a70",
    "lang": "de", "description": "Neurochirurgie-Fragebank (MCQ, offene Fragen, Fälle), offline nutzbar.",
    "icons": [
        {"src": "icons/icon-192.png", "sizes": "192x192", "type": "image/png"},
        {"src": "icons/icon-512.png", "sizes": "512x512", "type": "image/png"},
        {"src": "icons/icon-maskable-512.png", "sizes": "512x512", "type": "image/png", "purpose": "maskable"},
    ],
}
json.dump(manifest, open(os.path.join(site, "manifest.webmanifest"), "w", encoding="utf8"), ensure_ascii=False, indent=1)

sw = open(os.path.join(here, "sw.template.js"), encoding="utf8").read().replace("{{VERSION}}", version)
open(os.path.join(site, "sw.js"), "w", encoding="utf8").write(sw)

shutil.copytree(os.path.join(here, "icons"), os.path.join(site, "icons"), dirs_exist_ok=True)
open(os.path.join(site, ".nojekyll"), "w").close()
print(f"PWA built: version {version}, {nq} questions, {len(html)//1024} KB -> {site}")
