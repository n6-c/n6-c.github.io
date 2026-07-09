# n6-c.github.io

The public website for **Node-Six Cybernetics (N6C)**.

Static single-page site, published by GitHub Pages (via GitHub Actions) at **https://n6c.org**.

- `index.html` — the site (self-contained; Spectral + Inter + IBM Plex Mono via Google Fonts; no build step).
- `brand/n6c-mark.png` — the N6C hexagon mark (logo, favicon, hero watermark).
- `CNAME` — custom domain (`n6c.org`).
- `.github/workflows/pages.yml` — the deploy workflow (`upload-pages-artifact` + `deploy-pages`).

## Edit

Edit `index.html` and push to `main`. The **Deploy Pages** Action rebuilds and publishes automatically (~1 minute).

Preview locally without deploying:

```sh
python3 -m http.server 4747   # then open http://localhost:4747
```
