// A food-picture-01 entry (Node 22, standard library only): the picture
// is entry.png beside this file, drawn programmatically by gen2.py
// (PIL + numpy renderer: warm wood table, glossy golden broth, thick
// wavy noodles, jammy egg halves, chashu, narutomaki, nori, green
// onions, menma, chili oil, chopsticks lifting noodles, layered steam).
// This program copies it to /output/entry.png. Copying is byte-exact,
// so two runs write identical bytes. Entry fingerprint (checked):
// entry.png, 1024x1024, 530232 bytes,
// sha256 bfbed0cf59535575cb5f782ef866110cb397e868d6bddc7fa45455a5adb30a8b.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
