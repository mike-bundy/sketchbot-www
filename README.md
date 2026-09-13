# Sketchbot Studios — site rebuild (`~/www/stevetalkowski`)

The new **sketchbot.tv**: a static, spatial-web-first site for Steve Talkowski's Sketchbot Studios, plus the
complete archive and documentation of the old Squarespace site it replaces.

```
archive/        Everything from www.sketchbot.tv (Sept 2026): raw HTML + Squarespace JSON, 564 originals,
                per-page Markdown, projects.json / posts.json, the crawler, Steve's spatial-assets listing.
docs/           SITE-DOCUMENTATION.md (brand, voice, every page, clients, spatial footprint, known errors)
                + appendices (all pages with image lists, all 179 posts, the demo-reel breakdown).
content/        Curated inputs for the build: site.json (nav, socials, clients), projects.json (22 projects).
build.py        Static-site generator (Python 3.9+, stdlib only). Reads content/ + archive/, writes site/.
site/           The built site. Deploy this folder as-is (Cloudflare Pages, Netlify, GitHub Pages, S3, Laravel public/…).
```

## Build & preview

```bash
python3 build.py                       # ~1 s, 217 pages
python3 -m http.server 8765 -d site    # http://localhost:8765
```

Image derivatives (`site/assets/img/{full,thumb}`) are produced once by `archive/optimize.sh` (uses macOS `sips`);
re-run it only if you add images to `archive/images/`.

## What's in the site

- **Home** — new positioning: *Design. Create. Animate. Now in your space.*
- **/spatial/** — the studio's Apple Vision Pro work: Quads (flagship app), Immersive website environments
  (TRON: The Grid + Backrooms, live), USDZ asset production, Radial Menu (open source), Services, Lab.
- **/work/** — 22 project pages with full galleries and a native `<dialog>` lightbox; filterable index.
- **/reel/**, **/about/**, **/contact/**, **/shop/** (Sketchbot vinyl editions), **/news/** (all 179 posts, 2007–2015).
- `sitemap.xml`, `feed.xml`, `robots.txt`, `llms.txt`, `manifest.webmanifest`, `404.html`, JSON-LD on every page.

## Spatial web tiers (`site/assets/js/spatial.js`)

| Browser | 3D models (`.stage`) | Environments (`.immersive`) |
|---|---|---|
| Safari, visionOS 27 | native `<model stagemode="orbit">`, drag-out into the room | `model.requestImmersive()` + Web Audio loop |
| iOS / macOS Safari | three.js USDLoader + **AR Quick Look** chip | poster + copy |
| Chrome / Firefox / Edge | three.js USDLoader (same USDZ), orbit + auto-spin | poster + copy |

Environment USDZ files are streamed from Steve's public `stevetalkowski.github.io/spatial-assets` (CORS `*`);
small models and posters are local under `site/assets/spatial/` and `site/assets/quads/`.

## Editing content

- Copy for the Spatial pages, About, Contact, Shop, Reel lives in `build.py` (one function per page).
- Projects: edit `content/projects.json` (title, blurb, body, roles, tools, `hero` index into the archive gallery).
- Blog posts come straight from `archive/posts.json` + the Squarespace body HTML (images re-pointed locally).
- Design tokens (orange `#f5921f`, blue `#0184ff`, type, radii) are at the top of `site/assets/css/site.css`.

## Before going live

1. Point `BASE_URL` in `build.py` at the final domain if it isn't `https://www.sketchbot.tv`.
2. Upload; set 301s from old Squarespace slugs if desired (old → new map is in `docs/SITE-DOCUMENTATION.md` §5).
3. Test on a Vision Pro: `/spatial/environments/` (Enter The Grid) and `/spatial/quads/` (pinch a model out of the page).
4. Replace the Quads "Coming soon" CTAs with the App Store link when it ships.
