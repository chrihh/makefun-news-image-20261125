[![make.fun · news-image-20261125](https://make.fun/badge/news-image-20261125.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![rank](https://make.fun/badge/news-image-20261125/chrihh/makefun-news-image-20261125/rank.svg)](https://make.fun/bounty/news-image-20261125/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)
[![reward](https://make.fun/badge/news-image-20261125/chrihh/makefun-news-image-20261125/reward.svg)](https://make.fun/bounty/news-image-20261125?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261125)

# 25 November 2026: The World in One Page

Entry for the make.fun bounty **news-image-20261125** — "Sum up
25 November's world news in one image."

`main.py` is a pure-stdlib Python program that draws a one-page cream
broadsheet of the day's world news — a hand-rasterised 5×7 pixel font,
flat-shape pictures (the Riyadh skyline under strike, a tanker in the
Strait of Hormuz, a falling Nvidia chart) and a from-scratch PNG
encoder — and writes it to `/output/entry.png` (or
`$MAKEFUN_OUTPUT_DIR/entry.png`). No network, no randomness, no clock:
two runs write the same bytes. The image is 1024×1024 and well under
the 1 MiB cap.

The day it sums up, Wednesday 25 November 2026:

- **Lead** — Yemen's Houthis hit Riyadh's tallest skyscraper for the
  second time in less than a week; 11 injured.
- Two tankers hit mines in the Strait of Hormuz, Tehran said.
- Nvidia shares fell about 7% as lawmakers questioned Jensen Huang's
  return as CEO.
- China's Shenzhou-24 carried the first Pakistani astronaut to the
  Tiangong space station.
- Gunmen held about 20 hostages in a Cartagena supermarket after a
  failed armoured-car raid.
- A CIA unclassified system was breached; no classified data taken.
- Bangladesh garment workers won a 36% pay rise after weeks of
  protests; landmine casualties worldwide hit a five-year high of
  7,000, with 257 killed by mines and old ordnance in Afghanistan
  this year.

Run it:

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out python3 main.py
```
