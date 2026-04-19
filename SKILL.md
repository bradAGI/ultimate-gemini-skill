---
name: ultimate-gemini
description: Standalone image generation via Gemini 3.1 Flash Image (Nano Banana 2). Ships a self-contained Python CLI at `scripts/gemini_image.py` with two subcommands — `generate-image` and `batch-generate`. Use whenever the user asks to generate, create, make, design, or visualize an image, picture, photo, illustration, logo, banner, diagram, mockup, poster, character, or storyboard. Also for iterative refinement with reference images, multi-scene storyboards (batch), product shots, brand assets, and real-world-grounded generations (products, people, current events). Supports 14 aspect ratios, 512px–4K, PNG/JPEG/WebP, up to 14 reference images, Google Search + Image Search grounding, and parallel batches up to 8. Requires `GEMINI_API_KEY` (or `GOOGLE_API_KEY`). Do NOT use when the user wants a different backend (DALL·E, Midjourney, local diffusion).
---

# Ultimate Gemini

Self-contained image generation. Derived from [`anand-92/ultimate-image-gen-mcp`](https://github.com/anand-92/ultimate-image-gen-mcp) — tool surface, defaults, validation, and output shape mirror the original.

## Prerequisites

- `GEMINI_API_KEY` (or `GOOGLE_API_KEY`) in the environment. If missing, tell the user to set it — do not try to fix it yourself. Get one: https://aistudio.google.com/app/apikey.
- Python deps: `google-genai`, `pillow`. Install on first run if missing:
  ```bash
  pip install google-genai pillow
  ```

## The CLI

```
python3 <SKILL_DIR>/scripts/gemini_image.py generate-image --prompt "..." [flags]
python3 <SKILL_DIR>/scripts/gemini_image.py batch-generate --prompts "p1" "p2" ... [flags]
```

| Subcommand        | Purpose                                 |
|-------------------|-----------------------------------------|
| `generate-image`  | Single image                            |
| `batch-generate`  | Up to 8 prompts, run in parallel        |

Flag names are kebab-case (e.g. `--enable-google-search`, `--reference-image-paths`, `--thinking-level`). Defaults: `aspect_ratio=1:1`, `image_size=2K`, `output_format=png`, `thinking_level=minimal`, `batch_size=8`, `model=gemini-3.1-flash-image-preview`.

Images save to `$GEMINI_OUTPUT_DIR` (default `~/gemini_images`). The script prints a JSON result on stdout — parse it to report paths back to the user.

## User preference overrides

The user's global preferences override the defaults when invoking this skill (unless they explicitly ask for something else):

- `--image-size 1K` (the user prefers 1K)
- `--aspect-ratio 21:9` when generating banners / hero images

Apply these before falling back to script defaults.

## Decision tree

1. **One image** → `generate-image --prompt "..."`.
2. **Multiple related images** (storyboard, variations, product angles) → `batch-generate --prompts "..." "..."`. Runs in parallel — always faster than serial `generate-image` calls.
3. **Real product / person / current event** → add `--enable-google-search` so the model grounds on live data (e.g. "Tony Hawk", "Way of Wade 12 shoes", "2025 iPhone").
4. **Want visual style references from the web** → add `--enable-image-search`.
5. **Quality matters more than speed** → `--thinking-level high`. Default `minimal` is fast and fine for most asks.
   *(If either search flag is on, the script forces `minimal` to avoid `thought_signature` errors from the API — expected.)*
6. **User provided reference image paths** → `--reference-image-paths path1 path2 ...` (absolute paths, up to 14).

## Prompting principles

- **Less is more.** "Tony Hawk kickflip" beats a paragraph; the model + search fills the rest.
- **Don't pre-load style verbiage** the user didn't ask for. A "logo for Acme" is not automatically "cinematic, 8K, hyperdetailed".
- For polished results in a specific style, pick a template from `references/templates.md` — each gives a crafted prompt body plus recommended params.

## Common invocations

### Banner / hero (user default)
```bash
python3 <SKILL_DIR>/scripts/gemini_image.py generate-image \
  --prompt "..." \
  --aspect-ratio 21:9 \
  --image-size 1K
```

### Logo
```bash
python3 <SKILL_DIR>/scripts/gemini_image.py generate-image \
  --prompt "<style> logo for <brand>, flat vector, strong silhouette, transparent background" \
  --aspect-ratio 1:1 \
  --image-size 1K \
  --response-modalities IMAGE
```

### Product shot grounded in reality
```bash
python3 <SKILL_DIR>/scripts/gemini_image.py generate-image \
  --prompt "Way of Wade 12 shoes on studio white" \
  --aspect-ratio 1:1 \
  --image-size 1K \
  --enable-google-search --enable-image-search
```

### Storyboard / variations (parallel)
```bash
python3 <SKILL_DIR>/scripts/gemini_image.py batch-generate \
  --prompts "scene 1 ..." "scene 2 ..." "scene 3 ..." "scene 4 ..." \
  --aspect-ratio 16:9 \
  --image-size 1K
```

### With reference images
```bash
python3 <SKILL_DIR>/scripts/gemini_image.py generate-image \
  --prompt "same character in a new pose" \
  --reference-image-paths /abs/path/char1.png /abs/path/char2.png
```

## Output shape

`generate-image` output (JSON):
```json
{
  "success": true,
  "model": "gemini-3.1-flash-image-preview",
  "prompt": "...",
  "images_generated": 1,
  "images": [{"index": 0, "path": "...", "filename": "...", "size": 12345, "timestamp": "..."}],
  "text": null,
  "metadata": {"aspect_ratio": "1:1", "image_size": "2K", "output_format": "png", "thinking_level": "minimal"}
}
```

`batch-generate` output (JSON):
```json
{
  "success": true,
  "total_prompts": 4, "batch_size": 8, "image_size": "1K", "output_format": "png",
  "completed": 4, "failed": 0,
  "results": [{"prompt_index": 0, "prompt": "...", "success": true, "images": [...], ...}]
}
```

## Parameter reference

Full schema (14 aspect ratios, sizes, formats, modalities, batch semantics, env vars) is in `references/parameters.md`. Load it when the user pushes the edges or asks about options.

## Prompt templates

26 domain-specific prompt recipes (photography, cinematic, product mockup, logo, storyboard, macro, fashion, technical cutaway, flat lay, action freeze, night street, drone aerial, stylized 3D, SEM microscopy, double exposure, architectural viz, isometric, food, motion blur, typography, retro-futurism, surreal dreamscape, character sheet, PBR texture, historical, bioluminescent, silhouette) live in `references/templates.md`. Load only when the user's request clearly maps to one.

## After generation

- Parse stdout JSON and report the file path(s) to the user.
- If the user asked to "see" the image, open it:
  - Linux / WSL (Linux path): `xdg-open <path>`
  - WSL (Windows-reachable path like `/mnt/c/...`): `explorer.exe <path>`
  - macOS: `open <path>`
- If the script exits nonzero with an auth error, `GEMINI_API_KEY` is missing or expired — tell the user.
