// A food-picture-01 entry (Node 22, standard library only): the picture
// is entry.png beside this file, drawn programmatically by gen4.py
// (PIL + numpy + scipy renderer: 3/4 hero angle, bowl cropped at the
// frame bottom so the broth is the hero, bigger jammy egg, clean seared
// chashu, curved nori sunk into the broth, fBm wood table, stronger
// steam, warmer broth with key-light specular, unsharp mask for 300px
// crispness).
// This program copies it to /output/entry.png. Copying is byte-exact,
// so two runs write identical bytes. Entry fingerprint (checked):
// entry.png, 1024x1024, 796712 bytes,
// sha256 b9136036e65a91e2ab384bf0b641f72830052c7be6acf85e9831d744c039fbad.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
