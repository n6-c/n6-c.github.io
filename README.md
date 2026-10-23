# n6-c.github.io

The public website for **Node-Six Cybernetics (N6C)**, published by GitHub Pages (GitHub Actions) at **https://n6c.org**.

- Portuguese is the default, at `/`; English is at `/en/`. Visitors whose browser has no Portuguese go to English automatically, and the PT/EN buttons remember the choice.
- The pages are generated: copy in `tools/content.py`, templates in `tools/build.py`. Run `python3 tools/build.py` after any change; there are no dependencies and no build step on the server.
- `assets/` holds the CSS, JS, self-hosted fonts and images; `assets/tl/` is the construction film on the home page (sheets, frames for desktop `d` and phone `m`, `data.json` with the captions).
- `demos/espelho-de-vendas/` is the Vale do Araçá sales-map demo (fictional data).
- Old URLs (`/team.html`, `/founder.html`, `/kestrel.html`, `/pt/...`) are small redirect pages written by `build.py`.
- `.github/workflows/pages.yml` publishes only the built files (pages, `en/`, `pt/`, `assets/`, `demos/`, `brand/` images, `CNAME`, `robots.txt`, `sitemap.xml`); `tools/` and this README stay out.

## Preview

```sh
python3 tools/build.py
python3 tools/serve.py 4747   # then open http://127.0.0.1:4747 (clean URLs and the 404 page, like Pages)
```

Pushing to `main` publishes the site.
