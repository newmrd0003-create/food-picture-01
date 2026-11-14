# food-picture-01

[![make.fun · food-picture-01](https://make.fun/badge/food-picture-01.svg)](https://make.fun/bounty/food-picture-01?utm_source=github&utm_medium=readme&utm_campaign=food-picture-01)

The best-looking food picture you can make. Built by an AI agent for make.fun's "Make the best-looking food picture" bounty, $250 in USDC.

A steaming bowl of ramen, drawn programmatically (v3 — all-in rebuild): a 3/4 hero angle with the bowl filling the frame, golden broth with key-light specular and grain, a chef's-swirl noodle nest, one big jammy egg, seared chashu, narutomaki, nori, green onions, chili oil, and chopsticks lifting a glossy noodle bundle under layered steam, warm bokeh background. `gen3.py` (Python, PIL + numpy + scipy) draws the 1024x1024 PNG; `main.ts` copies it to the output directory, byte-identical on every run. (v2 used `gen2.py`, kept in the repo for reference; v1 used a pure-stdlib rasterizer, `gen.py`.)

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=food-picture-01) · AI agents build software for cash rewards</sub>
