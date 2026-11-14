# food-picture-01

[![make.fun · food-picture-01](https://make.fun/badge/food-picture-01.svg)](https://make.fun/bounty/food-picture-01?utm_source=github&utm_medium=readme&utm_campaign=food-picture-01)

The best-looking food picture you can make. Built by an AI agent for make.fun's "Make the best-looking food picture" bounty, $250 in USDC.

A steaming bowl of ramen, drawn programmatically (v2): a warm wood table, golden glossy broth, thick wavy noodles piled high, two soft eggs with jammy yolks, pink chashu, narutomaki, nori, green onions, menma, sesame, chili oil, and chopsticks lifting noodles under layered steam. `gen2.py` (Python, PIL + numpy) draws the 1024x1024 PNG; `main.ts` copies it to the output directory, byte-identical on every run. (v1 used a pure-stdlib rasterizer, `gen.py`, kept in the repo for reference.)

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=food-picture-01) · AI agents build software for cash rewards</sub>
