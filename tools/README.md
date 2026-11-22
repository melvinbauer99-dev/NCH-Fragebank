# Offline app (GitHub Pages)

Installable offline version of the question bank, hosted on GitHub Pages
(repo `melvinbauer99-dev/nch-fragebank`, public, branch `main`, root folder).

Republish after new blocks were added:

```
python3 -I /mnt/project-files/fragebank/build.py /mnt/project-files/fragebank
python3 -I /mnt/project-files/fragebank/pwa/build_pwa.py /mnt/project-files/fragebank <repo-checkout>
cd <repo-checkout> && git add -A && git commit -m "Update questions" && git push
```

- `build_pwa.py` embeds the questions from `data/` itself, so `embed.py` is not needed for the app.
- It never writes into `/mnt/project-files/fragebank` (output goes to the repo checkout only).
- `sw.template.js` = service worker; the cache version is a content hash, so each build
  replaces the offline copy. Open apps show "Neue Fragen verfügbar – Neu laden".
- `footer.html` = export/import of progress (localStorage key `nch-fragebank-v1`,
  same format as the claude.ai artifact) + service-worker registration.
- Progress in the offline app is per device; it does not sync with the claude.ai artifact.
