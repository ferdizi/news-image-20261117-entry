// news-image-20261117 entrypoint.
// The poster itself is drawn by build_poster.py; this program only
// places the finished file where the harness expects it:
//   /output/entry.png  (or $MAKEFUN_OUTPUT_DIR/entry.png locally)
import { copyFileSync, mkdirSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const destination = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";
mkdirSync(destination, { recursive: true });
const repoRoot = dirname(fileURLToPath(import.meta.url));
copyFileSync(join(repoRoot, "entry.png"), join(destination, "entry.png"));
