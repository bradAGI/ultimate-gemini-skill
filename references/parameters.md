# Parameter Reference

Complete schemas for the two subcommands exposed by `scripts/gemini_image.py`. These are a 1:1 mirror of the `bradAGI/ultimate-image-gen-mcp` tools, so MCP param ↔ CLI flag mapping is just snake_case → kebab-case (e.g. `enable_google_search` → `--enable-google-search`).

## Contents

- [generate-image](#generate-image) (MCP: `generate_image`)
- [batch-generate](#batch-generate) (MCP: `batch_generate`)
- [Allowed values](#allowed-values)
- [Environment variables](#environment-variables)

## generate-image

| MCP param | CLI flag | Type | Default | Notes |
|---|---|---|---|---|
| `prompt` | `--prompt` | string | required | Keep it short. Model fills detail via search and priors. |
| `aspect_ratio` | `--aspect-ratio` | string | `1:1` | See allowed values. |
| `image_size` | `--image-size` | string | `2K` | User pref: `1K`. `512px` \| `1K` \| `2K` \| `4K`. |
| `output_format` | `--output-format` | string | `png` | `png` \| `jpeg` \| `webp`. |
| `reference_image_paths` | `--reference-image-paths` | list[str] | `[]` | Absolute local paths. Up to 14 total (10 objects + 4 characters). |
| `enable_google_search` | `--enable-google-search` | bool | `false` | Grounds on live web for products, people, events. |
| `enable_image_search` | `--enable-image-search` | bool | `false` | Pulls visual references from Google Images. |
| `response_modalities` | `--response-modalities` | list[str] | `["TEXT","IMAGE"]` | Any subset of `TEXT`, `IMAGE`. |
| `thinking_level` | `--thinking-level` | string | `minimal` | `minimal` (fast) \| `high` (quality). |
| — | `--model` | string | `gemini-3.1-flash-image-preview` | Override via `GEMINI_IMAGE_MODEL` env var. |

## batch-generate

Shares all the flags above plus:

| MCP param | CLI flag | Type | Default | Notes |
|---|---|---|---|---|
| `prompts` | `--prompts` | list[str] | required | Up to 8 prompts (capped by `MAX_BATCH_SIZE`). |
| `batch_size` | `--batch-size` | int | `8` | Parallel chunk size within the list. |

All other flags (aspect ratio, size, format, reference images, search toggles, response modalities, thinking level, model) behave identically to `generate-image` and apply to every prompt in the list. Unlike what the MCP README suggests, `batch-generate` **does** accept `reference_image_paths` and `enable_google_search` — the underlying MCP implementation does too.

## Allowed values

### Aspect ratios (14)

`1:1`, `2:3`, `3:2`, `3:4`, `4:3`, `4:5`, `5:4`, `9:16`, `16:9`, `21:9`, `1:4`, `1:8`, `4:1`, `8:1`

Common mapping:
- **Square / social** → `1:1`
- **Portrait photo** → `4:5`, `2:3`
- **Landscape photo** → `3:2`, `4:3`
- **Mobile / story** → `9:16`
- **YouTube / widescreen** → `16:9`
- **Cinematic / banner / hero** → `21:9` *(user default for banners)*
- **Ultra-wide skyscraper / pano strips** → `4:1`, `8:1`, `1:4`, `1:8`

### Image sizes

- `512px` — thumbnails, quick iterations
- `1K` — **user default**
- `2K` — server default, balanced
- `4K` — print, hero, only when asked

### Output formats

- `png` — default, lossless, transparency
- `jpeg` — photographs, smaller files
- `webp` — web assets

### Thinking levels

- `minimal` — default, fast
- `high` — slower, higher quality; use for hero shots, final deliverables

### Response modalities

- `["TEXT","IMAGE"]` — image plus model commentary (default)
- `["IMAGE"]` — image only; cleaner for logos, textures, no narrative
- `["TEXT"]` — text only (no image); rarely needed

## Environment variables

Read at script startup.

| Env var | Default | Notes |
|---|---|---|
| `GEMINI_API_KEY` | — | **Required.** Script also accepts `GOOGLE_API_KEY`. |
| `GEMINI_OUTPUT_DIR` | `~/gemini_images` | Where generated images save. |
| `GEMINI_IMAGE_MODEL` | `gemini-3.1-flash-image-preview` | Override the default model. |
| `GEMINI_MAX_BATCH_SIZE` | `8` | Cap on `--prompts` and `--batch-size`. |
