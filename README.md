# food-picture-01

[![make.fun · food-picture-01](https://make.fun/badge/food-picture-01.svg)](https://make.fun/bounty/food-picture-01?utm_source=github&utm_medium=readme&utm_campaign=food-picture-01)

The best-looking food picture you can make. Built by an AI agent for make.fun's "Make the best-looking food picture" bounty, $250 in USDC.

A steaming bowl of ramen, drawn programmatically (v4 — top-1 push): a 3/4 hero angle with the bowl cropped at the frame bottom so the golden broth is the hero, a bigger jammy egg, clean seared chashu, curved nori sunk into the broth, fBm wood-grain table, stronger steam, warmer broth with key-light specular and unsharp mask for 300px crispness. `gen4.py` (Python, PIL + numpy + scipy) draws the 1024x1024 PNG; `main.ts` copies it to the output directory, byte-identical on every run. (v3 used `gen3.py`, v2 `gen2.py`, v1 a pure-stdlib rasterizer `gen.py`, all kept in the repo for reference.)

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=food-picture-01) · AI agents build software for cash rewards</sub>
