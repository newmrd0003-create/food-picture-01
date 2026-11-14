// A food-picture-01 entry (Node 22, standard library only): the picture
// is entry.png beside this file, drawn programmatically by gen3.py
// (PIL + numpy + scipy renderer: 3/4 hero angle, bowl fills the frame,
// golden broth with key-light specular and grain, chef's-swirl noodle
// nest, one big jammy egg, seared chashu, lifted noodle bundle under
// layered steam, warm bokeh background).
// This program copies it to /output/entry.png. Copying is byte-exact,
// so two runs write identical bytes. Entry fingerprint (checked):
// entry.png, 1024x1024, 592658 bytes,
// sha256 be5c2ff79399b3887c365cbfc8012d26657ce4b96f47afdf735746ee5e0b8f68.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
