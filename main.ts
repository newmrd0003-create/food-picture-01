// A food-picture-01 entry (Node 22, standard library only): the picture
// is entry.png beside this file, drawn programmatically by gen.py
// (pure-stdlib Python rasterizer: gradients, noodles, egg, steam).
// This program copies it to /output/entry.png. Copying is byte-exact,
// so two runs write identical bytes. Entry fingerprint (checked):
// entry.png, 1024x1024, 324421 bytes,
// sha256 cc7c8700ebb48e0da6129bdb10d226ce1399d1f0793e8b64137563d0759961f1.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
