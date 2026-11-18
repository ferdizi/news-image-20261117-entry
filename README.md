# Tuesday 17 November 2026 — one front page, 30 stories, 6 continents

[![make.fun](https://img.shields.io/badge/make.fun-news--image--20261117-blue)](https://make.fun/c/news-image-20261117)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Entry for the make.fun competition **"Sum up 17 November's world news in one image"**
($250, free entry). The program writes one image to `/output/entry.png`.

## The poster

A 1024×1024 newspaper front page, drawn programmatically with Pillow
(`build_poster.py`, deterministic — two runs are byte-identical):

- **Masthead:** "Tuesday 17 November 2026" — 30 stories, 6 continents, one day.
- **12 numbered, illustrated main panels**, ordered the way the day's
  consensus ranked them: Kerch Bridge falls, Iran's drones at a US radar in
  Bahrain, Trump in Manila ahead of the first-ever Trump–Xi–Putin summit,
  Nvidia's record $115.8bn quarter, Ebola past 11,000 cases in DR Congo,
  Mongolia's president saying he will resign, the COP31 fossil-fuel split,
  Japan scrambling jets at a Russian incursion, the Dow down 849, Pope Leo XIV
  flying home, the US losing measles-free status, and Australia tightening
  backpacker visa rules (the honest Oceania main — most front pages fake it).
- **"Where it happened" world map** with numbered dots matching the panels,
  plus a region colour legend.
- **"Also on Tuesday 17 November"** — 18 more one-line stories (13–30).
- **Footer:** every story was reported on Tuesday 17 November 2026; disputed
  claims are attributed in the decks ("Bahrain says it intercepted…",
  "Russia says it downed 1,441 drones…"). Sources: AP, Reuters, AFP, BBC,
  Al Jazeera, UN News, WHO. Original drawings.

Every main story was verified against live reporting on 17 November 2026.
Stories that only *look* like 17 November news were left out or reframed to
their true 17 November angle — e.g. Nvidia's story is the earnings and the
board refusing to reinstate Huang (he stepped down on 12 November), and
Microsoft's is its 17 November post-incident report on last week's outage,
not the outage itself.

## Build

```bash
python3 build_poster.py   # writes entry.png (1024x1024, ~175 KB)
```

## Run

```bash
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts   # copies entry.png to out/entry.png
```

## License

MIT — see [LICENSE](LICENSE).
