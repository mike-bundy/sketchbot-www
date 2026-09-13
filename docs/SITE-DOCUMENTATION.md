# sketchbot.tv — Complete Site Documentation (archived 2026-09-12)

This document captures **everything on the current Sketchbot Studios website** (www.sketchbot.tv, Squarespace 7.1)
so the rebuild has a faithful base of content, language, imagery and links. The raw archive lives in `../archive/`:

| Path | What it is |
|---|---|
| `archive/raw/html/*.html` | Every page and blog post, as served (226 + home) |
| `archive/raw/json/*.json` | Squarespace's structured JSON for each page (`?format=json-pretty`) |
| `archive/pages/*.md` | Per-page Markdown extraction: title, description, text, videos, external links, image list |
| `archive/images/` + `manifest.json` | 564 original images at up to 2500px, mapped back to source URL and page |
| `archive/projects.json` | Every portfolio page: ordered images, captions, headings, paragraphs, dimensions |
| `archive/posts.json` | All 179 blog posts, newest first: title, date, excerpt, full body, tags, image |
| `archive/inventory.json` | Page inventory with word/image counts |
| `archive/spatial-assets/` | Listing of Steve's `spatial-assets` GitHub repo + READMEs of his visionOS repos |
| `archive/crawl.py` | The crawler (re-runnable) |

---

## 1. Identity

- **Studio:** Sketchbot Studios — founded 2008 by **Steve Talkowski**, Los Angeles, CA (previously Brooklyn / NYC).
- **Domain:** sketchbot.tv (canonical `http://www.sketchbot.tv`). Email: **steve@sketchbot.tv**.
- **Site tagline (meta description):** *"Sketchbot is the designer toy created by Steve Talkowski. Sketchbot Studios is the content creator."*
- **Homepage headline:** **Design. Create. Animate.** — "Welcome to Sketchbot Studios" — then the five-beat ladder:
  **Dream it. Build it. Grow it. Sell it. VR it.**
- **Mascot / IP:** **Sketchbot** — a retro-styled, pencil-wielding, one-eyed (cyclops) orange robot with chrome arms, "sb" chest badge.
  Related cast: the **Eye Pilots** (blue/pink/yellow spherical eyeball robots), **BuddhaBot**, **TikiBot**, **RefBot**, **Pumpkin Giant**,
  **Browser Bots**, **Guavaroo**, **MoneyGrip**, **Surge Protector**, **EntryBot**, **HeartBot**, **OctoBot**, **USBot**.
- **Visual language:** saturated Sketchbot **orange** (~`#F5921F`), Eye-Pilot **blue** (~`#1E7BE8` — close to the Quads brand blue `#0184ff`), chrome, cream, big single eyes, toy-photography on white, cinematic Unreal/KeyShot renders.
- **Fonts on the current site:** Poppins 700 (headings), Manrope (body) — Squarespace hosted.
- **Social:** Instagram `@stevetalkowski` · Vimeo `vimeo.com/stevetalkowski` · LinkedIn `linkedin.com/in/stevetalkowski` · Pinterest `pinterest.com/stevetalkowski` · Tumblr `sketchbot.tumblr.com` · Facebook (personal id 562536268) · Sketchfab `sketchfab.com/stevetalkowski` · GitHub `github.com/stevetalkowski`.

## 2. Voice & language

Steve writes first-person, warm, direct, enthusiastic, craft-focused. Hallmarks:

- Short declaratives and imperative ladders ("Dream it. Build it. Grow it. Sell it. VR it.").
- Tool-literate: names the pipeline (Maya, ZBrush, KeyShot, Substance Painter, Unreal Engine, Reality Composer Pro, After Effects).
- Credits shot-by-shot ("Modeling, Rigging, Animation, Lighting, Render, Composite").
- Community-minded: shout-outs to collaborators, galleries, shows (My Plastic Heart, Munky King, Toy Art Gallery, APW, DesignerCon, SDCC, NYCC, Pictoplasma).
- Playful sign-offs and in-jokes ("END OF LINE" on the TRON page; "Botober").
- Contact CTA: **"Upcoming Gig? Let's Talk."** — asks for description, budget, deadline; NDAs to email.
- Availability line: *"I'm currently available for Art Direction, Animation Directing, Character/Concept Design and 3D Modeling (Maya, ZBrush)."*

## 3. Bio (verbatim, ABOUT page)

> **Steve Talkowski** — A 20+ year veteran of the computer animation scene, I have worked as an Art Director, Animation Director,
> Character Designer/Modeler and Animator on hundreds of national brands ranging from Beats by Dre, BMW, Pepsi, General Mills,
> Target, Reese's and M&M's, to the feature films Joe's Apartment, Ice Age, Alien Resurrection and the 1988 Academy Award
> winning short, Bunny. In 2008, I launched Sketchbot Studios and self-produced my first foray into the designer toy scene —
> the retro-styled, pencil-wielding robot, Sketchbot. In 2010, the Sketchbot platform served as the basis for two highly
> successful DIY custom shows held in NYC and LA. Recently relocated to Los Angeles, CA, I am currently in development
> bringing my robot creations to life as an animated series.

Third-person version (Museum of Untold Possibilities page) adds: senior animator at **Blue Sky Studios**; clients Google, Adobe,
Autodesk; "continues to design original characters for toy and branding properties, freelances on film and commercials, and
continues developing his world of robots into a 3d animated TV series." Elsewhere: "Working as a professional 3d artist over the
past 30 years."

## 4. Navigation (as live)

`PROJECTS ▾` (folder) → Sketchbot Designer Vinyl Toy · Afternoon At The Museum · Jammin' Alpacas · Autodesk Maya M4Y4 · GIBCO Cells ·
SCOOB 3D Concept Art · Adobe VR Bot · backrooms · BuddhaBot · Keyshot 6 Avatar · Beats by Dre · Inktober 2012 · Botober 2013 ·
March of Robots 2014 · March of Robots 2016 · Ref Bot · TikiBot · Browser Bots · 3D Misc · TRON
`SHOP` · `ABOUT` · `NEWS` (blog) · `DEMO REEL` · `CONTACT`

Not in nav but live: `/museum-of-untold-possibilities` (Epic MegaGrant pitch), `/sketchbot_museum`, `/pgiant`, `/surge-protector`,
`/usdz-files`, `/projects-gallery/*` (an unfinished Squarespace portfolio draft with lorem-style placeholder copy), `/cover-page`.

## 5. Pages — content summary

### Home `/`
Cover page: "Design. Create. Animate. / Welcome to Sketchbot Studios / Dream it. Build it. Grow it. Sell it. VR it." Hero image:
Eye Pilot with clipboard in a factory (`sketchbotPilotClipboard.png`).

### Sketchbot Designer Vinyl Toy `/sketchbot`
14 product photographs of the Sketchbot vinyl figure (V1 orange with pencil, box, variants). No copy on page — copy lives in blog posts:
2008 prototype sculpt series, 2009 3D-print/mold progress, 2010 release + signings (My Plastic Heart NYC, Crewest LA), Variants 3/4/5
(2011: magenta V3 at TOYSTREET NYC; V4 at SDCC 2011; V5 pre-release at NYCC 2011 via My Plastic Heart), DesignerCon 2011 resin casts by
Pretty In Plastic ($60, edition of 30, six colours), Sketchbot Custom Shows 2010 (NYC + LA), Stikalicious iPad stickers, MOLD3D 3D-print shop.

### Afternoon At The Museum `/sketchbot_museum`
"Proof of concept for EPIC Games Megagrant, created with Unreal Engine." 10 Unreal stills of Eye Pilots exploring a concrete museum.

### The Museum of Untold Possibilities `/museum-of-untold-possibilities` (1,456 words)
Full **Epic MegaGrant pitch**: "CoCo VR meets the World of Sketchbot!" — a non-game VR museum (Quest 2 first, then PC/mobile) with
galleries (Sketchbot history, Inktober, March of Robots, Nuthin' But Mech, guest artists Dacosta Bayley / Chocolate Soop and Brandt Peters),
an AI robot docent, and an **Art Lab** where visitors build DIY robots, export STL for 3D printing, view in AR, output GIFs.
Three phases (VR museum → Eye Pilot game → short-form TV series in Unreal). Team: Steve (Creative Director), Erik Anderson (Unreal engineer,
eriksgames.com), Erik Desiderio (composer, anomalyaudio.com). Section headings: Elevator Pitch · Explore · Discover · Create · Funding Needs ·
Project Breakdown · Meet The Team · Thank You!

### Jammin' Alpacas `/jammin_alpacas` — 12 cinematic stills (space billboard, character reactions). Animated short/pitch.
### Autodesk Maya M4Y4 `/m4y4` — "I was brought on to design, model and render the new mascot for Autodesk Maya's Learning Channel. One of the key requirements was the character be real-time compliant for use in Maya's viewport for training purposes." 9 images (magnifying-glass hero, banner, group pose).
### GIBCO Cells `/gibco` — 8 images: cell-character concepts for GIBCO (Thermo Fisher).
### SCOOB 3D Concept Art `/scoob` — 9 images: Mean Machine 3D concept tests for the SCOOB! feature.
### Adobe VR Bot `/adobe_vr_bot5` — 9 images: neon-tube robot for Adobe, VR-themed renders.
### backrooms `/backrooms` — 1 image: Sketchbot in the Backrooms (liminal office). A 20 MB `backrooms_env_V4_optimized.usdz` exists in the spatial-assets repo — this is a Vision Pro environment.
### BuddhaBot `/buddhabot` — 5 images incl. original sketch and 3D World cover (TDW191).
### KeyShot 6 Avatar `/keyshot-6-avatar` — 11 images; the official KeyShot 6 avatar robot; 4-page tutorial in 3D World #198.
### Beats by Dre `/beats-by-dre-1` — 16 character designs (pirate, Elvis, Kingston, etc.) for Beats.
### Inktober 2012 `/photographs` — 36 ink sketches. ### Botober 2013 `/botober2013` — 19 daily robot renders.
### March of Robots 2014 `/marchofrobots2014` — 14. ### March of Robots 2016 `/march_of_robots_2016` — 27.
### Ref Bot `/refbot` — 4 (soccer referee bot; World Cup Crewest 2010). ### TikiBot `/tikibot` — 13 incl. sketchbook scan.
### Browser Bots `/browserbots-1` — 8: Chrome, Firefox, IE, Opera, Safari, Verold bots.
### 3D Misc `/3d-misc-1` — 39: Meet Mat Sketchbot, HeartBot, Eye Pilot clipboard, OctoBot Beach Patrol, USBot, VR Eye Pilot, more.
### Pumpkin Giant `/pgiant` — 10. ### Surge Protector `/surge-protector` — 6 (Disney-style test after Bill Schwab reference).
### TRON `/tron` — **TRON IMMERSIVE** — Steve's first **spatial website environment for Apple Vision Pro** (homage to the 1982 film,
timed to TRON: Ares). Instructions for enabling Safari "Website environments" feature flag on visionOS 26; on visionOS 27 the page uses the
`<model>` element with `requestImmersive()`. "Two Interactive 3D models will display stereoscopically inline on Vision Pro"
(Recognizer and Tank USDZ). Programs: Modeled and animated in Autodesk Maya · Textured in Adobe Substance Painter · Assembled in Reality
Composer Pro. YouTube embed `-bEEAq0T6U0`. Sign-off "END OF LINE". Assets hosted at `stevetalkowski.github.io/spatial-assets/`.
The full working script is preserved in `archive/raw/html/tron.html` (search `gridBanner`).
### USDZ FILES `/usdz-files` — Sketchfab embed: "Alien Head_V2 — ZBrush for iPad test".
### Demo Reel `/demo-reel` — 2012 reel (Vimeo) + full **shot breakdown** (50 entries) — see Appendix C.
### Shop `/shop` — Squarespace commerce, currently **no products**.
### About `/about` — bio + portrait (`about_image.jpg`, Steve in front of a Sketchbot eye).
### Contact `/contact` — "Upcoming Gig? Let's Talk." + availability + email. Hero image `download.jpeg`.
### News `/blog` — 179 posts, 2007-11 → 2015-12 (2008 = 103 posts). Tag cloud led by *sketchbot, My Plastic Heart, Custom, 3d, Custom Show,
prototype, SDCC, APW Gallery, NYCC, Munky King, Maya*. Newest: Nuthin' But Mech 3 (Dec 2015), KeyShot 6 Avatar Tutorial, Fun With MatCaps
in KeyShot 6, KeyShot 6 Teaser, MOLD3D Shop is LIVE!, Surge Protector, EntryBot, ZBrush Sketches, New Year New Site (Jan 2015).

## 6. Clients & credits (aggregated from About + Demo Reel + Museum page)

Beats by Dre · BMW · Pepsi · General Mills (Cocoa Puffs, Honey Nut Cheerios) · Target · Reese's · M&M's · Google · Adobe · Autodesk · Yoplait ·
TheraFlu · SanDisk · TruGreen · Efficiency Vermont · Sticker Book Inc. · Capital Cube · Sony Ericsson · French's · Quaker · Nasonex · Nickelodeon ·
Chapstick · Canon PowerShot · AT&T · Band-Aid · Trident · Capri-Sun · Marvel · GMC/NFL · MAC Cosmetics · Ice Breakers · Mott's · KeyShot (Luxion) ·
GIBCO (Thermo Fisher) · Warner Bros (SCOOB) · Blue Sky Studios.
**Film:** Joe's Apartment · Ice Age (3D layout) · Alien Resurrection (rigger/animator) · Bunny (1998 Academy Award, Best Animated Short — the site says "1988"; the film is 1998).
**Press:** 3D World Magazine (#191 cover BuddhaBot; #198 KeyShot tutorial) · Nuthin' But Mech Vol 3 & 4 (Design Studio Press) · Creative Bloq.

## 7. Spatial computing footprint (the seed for the new layer)

| Item | Where | Notes |
|---|---|---|
| **Quads** | quads.vision · `~/code/quads` | Spatial box-modeler for Apple Vision Pro: hands-first, Logitech Muse stylus, Catmull-Clark SubD, sculpt, voxel remesh, USDZ/OBJ export, SharePlay co-modeling, community gallery. Bundle `com.sketchbot.quads`. |
| **TRON Immersive** | sketchbot.tv/tron | Website environment (`<link rel=spatial-backdrop>` / `model.requestImmersive()`), inline stereoscopic `<model>`s, spatial audio. |
| **Backrooms** | sketchbot.tv/backrooms + `backrooms_env_V4_optimized.usdz` | Second immersive environment. |
| **spatial-assets** repo | github.com/stevetalkowski/spatial-assets | theGrid (many versions), recognizer, tank, Immersive.usdz, website.usdz, cube_env, audio_scene, HDR/EXR envs. |
| **radial-menu** | github.com/stevetalkowski/radial-menu | Open-source tunable radial/vertical/horizontal menu for visionOS/macOS/iPadOS/iOS; one Swift file + tuning app; born as a Quads spike. |
| **VRNavDemo** | github.com/stevetalkowski/VRNavDemo | VR navigation sandbox for Vision Pro. |
| **Museum of Untold Possibilities** | sketchbot.tv/museum-of-untold-possibilities | Unreal VR museum pitch (Quest). |
| **Adobe VR Bot**, **ZBrush for iPad** Sketchfab | — | Earlier XR-adjacent work. |

## 8. Technical notes on the old site
Squarespace 7.1, template with folder nav, gallery grid pages, commerce (empty), blog imported from Blogger (2007–2012 posts keep `.html` slugs).
Images served from `images.squarespace-cdn.com` (`?format=2500w` max). Vimeo/YouTube embeds. Custom code block on TRON page. `sitemap.xml`
has 231 URLs (188 blog). No structured data beyond OG/Twitter cards. Not mobile-optimized on the cover page (large hero).

## 9. Known gaps / errors to fix in the rebuild
- "1988 Academy Award winning short, Bunny" → Bunny won the 1998 Oscar.
- Shop is empty; Sketchbot vinyl figures are only documented in blog posts.
- `/projects-gallery/*` draft pages contain Squarespace placeholder copy ("It all begins with an idea…") — do not migrate.
- Nothing on the site mentions **Quads**, the radial-menu library, or a spatial-services offering — the current site reads as 2015 + one TRON page.
- No SSL canonical (`http://`), no dark mode, no `<model>`/AR fallbacks outside TRON.

See Appendix files: `APPENDIX-A-pages.md` (every page with image list), `APPENDIX-B-posts.md` (all blog posts), `APPENDIX-C-reel.md` (shot breakdown).
