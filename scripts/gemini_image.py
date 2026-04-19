#!/usr/bin/env python3
"""Standalone CLI that mirrors the tools exposed by anand-92/ultimate-image-gen-mcp.

Two subcommands with the exact parameter surface of the MCP tools:

    gemini_image.py generate-image  --prompt "..."            [flags]
    gemini_image.py batch-generate  --prompts "p1" "p2" ...   [flags]

Defaults, validation, and JSON output shape match the MCP's `generate_image_tool`
and `batch_generate_images` functions, so swapping MCP calls for this CLI is
behaviour-preserving.

Requires: GEMINI_API_KEY (or GOOGLE_API_KEY) in the environment.
Install:  pip install google-genai pillow
"""

import argparse
import asyncio
import base64
import io
import json
import logging
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from uuid import uuid4

try:
    from google import genai
    from google.genai import types
    from PIL import Image
except ImportError as e:
    sys.stderr.write(
        f"Missing dependency: {e}. Install with: pip install google-genai pillow\n"
    )
    sys.exit(2)

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger("gemini_image")

# ---- Constants (mirrored from src/config/constants.py in the MCP) -----------

DEFAULT_MODEL = os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3.1-flash-image-preview")
OUTPUT_DIR = Path(os.environ.get("GEMINI_OUTPUT_DIR", str(Path.home() / "gemini_images")))

ASPECT_RATIOS = [
    "1:1", "1:4", "1:8", "2:3", "3:2", "3:4",
    "4:1", "4:3", "4:5", "5:4", "8:1", "9:16", "16:9", "21:9",
]
IMAGE_SIZES = ["512px", "1K", "2K", "4K"]
OUTPUT_FORMATS = ["png", "jpeg", "webp"]
THINKING_LEVELS = ["minimal", "high"]
RESPONSE_MODALITIES = ["TEXT", "IMAGE"]

DEFAULT_ASPECT_RATIO = "1:1"
DEFAULT_IMAGE_SIZE = "2K"
DEFAULT_OUTPUT_FORMAT = "png"
DEFAULT_THINKING_LEVEL = "minimal"

MAX_REFERENCE_IMAGES = 14
MAX_BATCH_SIZE = int(os.environ.get("GEMINI_MAX_BATCH_SIZE", "8"))
MAX_PROMPT_LENGTH = 8192
MAX_IMAGE_SIZE_BYTES = 20 * 1024 * 1024

# ---- Validation -------------------------------------------------------------


class ValidationError(ValueError):
    pass


def validate_prompt(prompt: str) -> None:
    if not prompt or not prompt.strip():
        raise ValidationError("prompt must be non-empty")
    if len(prompt) > MAX_PROMPT_LENGTH:
        raise ValidationError(f"prompt exceeds {MAX_PROMPT_LENGTH} chars")


def validate_prompts_list(prompts: list[str]) -> None:
    if not prompts:
        raise ValidationError("prompts must be non-empty")
    if len(prompts) > MAX_BATCH_SIZE:
        raise ValidationError(f"prompts capped at {MAX_BATCH_SIZE} (got {len(prompts)})")
    for p in prompts:
        validate_prompt(p)


def validate_aspect_ratio(ratio: str) -> None:
    if ratio not in ASPECT_RATIOS:
        raise ValidationError(f"invalid aspect_ratio '{ratio}' (one of: {', '.join(ASPECT_RATIOS)})")


def validate_image_size(size: str) -> str:
    if size.lower() == "512px":
        return "512px"
    up = size.upper()
    if up not in IMAGE_SIZES:
        raise ValidationError(f"invalid image_size '{size}' (one of: {', '.join(IMAGE_SIZES)})")
    return up


def validate_image_format(fmt: str) -> None:
    if fmt not in OUTPUT_FORMATS:
        raise ValidationError(f"invalid output_format '{fmt}' (one of: {', '.join(OUTPUT_FORMATS)})")


def validate_thinking_level(level: str) -> None:
    if level not in THINKING_LEVELS:
        raise ValidationError(f"invalid thinking_level '{level}' (one of: {', '.join(THINKING_LEVELS)})")


def validate_batch_size(batch_size: int) -> None:
    if batch_size < 1 or batch_size > MAX_BATCH_SIZE:
        raise ValidationError(f"batch_size must be 1..{MAX_BATCH_SIZE} (got {batch_size})")


def validate_reference_image(path: str) -> tuple[str, bytes]:
    p = Path(path).expanduser().resolve()
    if not p.exists():
        raise ValidationError(f"reference image not found: {p}")
    data = p.read_bytes()
    if len(data) > MAX_IMAGE_SIZE_BYTES:
        raise ValidationError(f"reference image too large (>20 MB): {p}")
    try:
        Image.open(io.BytesIO(data)).verify()
    except Exception as e:
        raise ValidationError(f"reference image is not a valid image: {p} ({e})")
    return str(p), data


def validate_reference_images_count(paths: list[str]) -> None:
    if len(paths) > MAX_REFERENCE_IMAGES:
        raise ValidationError(
            f"reference_image_paths capped at {MAX_REFERENCE_IMAGES} (got {len(paths)})"
        )


# ---- API key ----------------------------------------------------------------


def require_api_key() -> str:
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if not key:
        sys.stderr.write("Set GEMINI_API_KEY (or GOOGLE_API_KEY).\n")
        sys.exit(1)
    return key


# ---- File I/O ---------------------------------------------------------------


def _slug(prompt: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", prompt[:60].lower()).strip("-") or "image"


def _filename(prompt: str, index: int, ext: str) -> str:
    now = datetime.now()
    tail = f"{now.strftime('%H%M%S')}-{now.microsecond:06d}-{uuid4().hex[:8]}"
    idx = f"-{index + 1}" if index > 0 else ""
    return f"{_slug(prompt)}{idx}-{tail}.{ext}"


def _save_image(b64_data: str, prompt: str, index: int, fmt: str) -> dict:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    path = OUTPUT_DIR / _filename(prompt, index, fmt)
    raw = base64.b64decode(b64_data)
    if fmt == "png":
        path.write_bytes(raw)
    else:
        img = Image.open(io.BytesIO(raw))
        buf = io.BytesIO()
        save_fmt = "JPEG" if fmt in ("jpg", "jpeg") else fmt.upper()
        img.save(buf, format=save_fmt)
        path.write_bytes(buf.getvalue())
    log.info(f"Saved: {path}")
    return {
        "index": index,
        "path": str(path),
        "filename": path.name,
        "size": path.stat().st_size,
        "timestamp": datetime.now().isoformat(),
    }


# ---- Generation -------------------------------------------------------------


def _build_config(
    *,
    aspect_ratio: str,
    image_size: str,
    response_modalities: list[str] | None,
    enable_google_search: bool,
    enable_image_search: bool,
    thinking_level: str,
) -> types.GenerateContentConfig:
    effective = thinking_level
    tools = None
    if enable_google_search or enable_image_search:
        tools = [
            types.Tool(
                google_search=types.GoogleSearch(
                    search_types=types.SearchTypes(
                        web_search=types.WebSearch() if enable_google_search else None,
                        image_search=types.ImageSearch() if enable_image_search else None,
                    )
                )
            )
        ]
        if thinking_level.lower() != "minimal":
            effective = "minimal"
            log.info("Forcing thinking_level=minimal because a search tool is enabled")

    return types.GenerateContentConfig(
        response_modalities=response_modalities or ["TEXT", "IMAGE"],
        image_config=types.ImageConfig(
            aspect_ratio=aspect_ratio,
            image_size=image_size or None,
        ),
        thinking_config=types.ThinkingConfig(
            thinking_level={
                "minimal": types.ThinkingLevel.MINIMAL,
                "high": types.ThinkingLevel.HIGH,
            }.get(effective.lower(), types.ThinkingLevel.MINIMAL),
        ),
        tools=tools,
    )


async def generate_image_tool(
    prompt: str,
    *,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    image_size: str = DEFAULT_IMAGE_SIZE,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    reference_image_paths: list[str] | None = None,
    reference_images_data: list[str] | None = None,
    enable_google_search: bool = False,
    enable_image_search: bool = False,
    response_modalities: list[str] | None = None,
    thinking_level: str = DEFAULT_THINKING_LEVEL,
    client: genai.Client | None = None,
) -> dict:
    """Single-image generation. Mirrors MCP `generate_image_tool` surface."""
    validate_prompt(prompt)
    validate_aspect_ratio(aspect_ratio)
    image_size = validate_image_size(image_size)
    validate_image_format(output_format)
    validate_thinking_level(thinking_level)

    contents: list = []
    if reference_images_data:
        for b64 in reference_images_data[:MAX_REFERENCE_IMAGES]:
            contents.append(Image.open(io.BytesIO(base64.b64decode(b64))))
    elif reference_image_paths:
        validate_reference_images_count(reference_image_paths)
        for p in reference_image_paths[:MAX_REFERENCE_IMAGES]:
            _, data = validate_reference_image(p)
            contents.append(Image.open(io.BytesIO(data)))
    contents.append(prompt)

    if client is None:
        client = genai.Client(api_key=require_api_key())

    config = _build_config(
        aspect_ratio=aspect_ratio,
        image_size=image_size,
        response_modalities=response_modalities,
        enable_google_search=enable_google_search,
        enable_image_search=enable_image_search,
        thinking_level=thinking_level,
    )

    log.info(f"generate_image: model={model} size={image_size} ratio={aspect_ratio}")
    try:
        response = await asyncio.to_thread(
            client.models.generate_content,
            model=model,
            contents=contents,
            config=config,
        )
    except Exception as e:
        return {"success": False, "error": str(e), "error_type": type(e).__name__}

    images_b64: list[str] = []
    text_parts: list[str] = []
    for part in response.parts:
        if getattr(part, "thought", False):
            continue
        if getattr(part, "inline_data", None) and part.inline_data:
            images_b64.append(base64.b64encode(part.inline_data.data).decode())
        if getattr(part, "text", None):
            text_parts.append(part.text)

    if not images_b64:
        return {
            "success": False,
            "error": "no image data in response",
            "text": "\n".join(text_parts) or None,
        }

    saved = [_save_image(b, prompt, i, output_format) for i, b in enumerate(images_b64)]
    return {
        "success": True,
        "model": model,
        "prompt": prompt,
        "images_generated": len(saved),
        "images": saved,
        "text": "\n".join(text_parts) or None,
        "metadata": {
            "aspect_ratio": aspect_ratio,
            "image_size": image_size,
            "output_format": output_format,
            "thinking_level": thinking_level,
        },
    }


async def batch_generate_tool(
    prompts: list[str],
    *,
    model: str = DEFAULT_MODEL,
    aspect_ratio: str = DEFAULT_ASPECT_RATIO,
    image_size: str = DEFAULT_IMAGE_SIZE,
    output_format: str = DEFAULT_OUTPUT_FORMAT,
    reference_image_paths: list[str] | None = None,
    batch_size: int = MAX_BATCH_SIZE,
    enable_google_search: bool = False,
    enable_image_search: bool = False,
    response_modalities: list[str] | None = None,
    thinking_level: str = DEFAULT_THINKING_LEVEL,
) -> dict:
    """Batch generation. Mirrors MCP `batch_generate_images` surface."""
    validate_prompts_list(prompts)
    validate_batch_size(batch_size)

    reference_images_data: list[str] | None = None
    if reference_image_paths:
        validate_reference_images_count(reference_image_paths)
        reference_images_data = []
        for p in reference_image_paths[:MAX_REFERENCE_IMAGES]:
            try:
                _, data = validate_reference_image(p)
                reference_images_data.append(base64.b64encode(data).decode())
            except ValidationError as e:
                log.warning(str(e))

    client = genai.Client(api_key=require_api_key())

    results: dict = {
        "success": True,
        "total_prompts": len(prompts),
        "batch_size": batch_size,
        "image_size": image_size,
        "output_format": output_format,
        "completed": 0,
        "failed": 0,
        "results": [],
    }

    for start in range(0, len(prompts), batch_size):
        chunk = prompts[start : start + batch_size]
        log.info(f"batch chunk {start // batch_size + 1}: {len(chunk)} prompts")
        tasks = [
            generate_image_tool(
                prompt=p,
                model=model,
                aspect_ratio=aspect_ratio,
                image_size=image_size,
                output_format=output_format,
                reference_image_paths=reference_image_paths,
                reference_images_data=reference_images_data,
                enable_google_search=enable_google_search,
                enable_image_search=enable_image_search,
                response_modalities=response_modalities,
                thinking_level=thinking_level,
                client=client,
            )
            for p in chunk
        ]
        chunk_results = await asyncio.gather(*tasks, return_exceptions=True)

        for j, r in enumerate(chunk_results):
            idx = start + j
            if isinstance(r, Exception):
                results["failed"] += 1
                results["results"].append(
                    {"prompt_index": idx, "prompt": chunk[j], "success": False, "error": str(r)}
                )
                continue
            assert isinstance(r, dict)
            if r.get("success"):
                results["completed"] += 1
            else:
                results["failed"] += 1
            results["results"].append({"prompt_index": idx, "prompt": chunk[j], **r})

    return results


# ---- CLI --------------------------------------------------------------------


def _add_common_flags(p: argparse.ArgumentParser) -> None:
    p.add_argument("--aspect-ratio", default=DEFAULT_ASPECT_RATIO, choices=ASPECT_RATIOS)
    p.add_argument("--image-size", default=DEFAULT_IMAGE_SIZE,
                   help=f"One of: {', '.join(IMAGE_SIZES)}  (default: {DEFAULT_IMAGE_SIZE})")
    p.add_argument("--output-format", default=DEFAULT_OUTPUT_FORMAT, choices=OUTPUT_FORMATS)
    p.add_argument("--reference-image-paths", nargs="*", default=None,
                   help=f"Up to {MAX_REFERENCE_IMAGES} local image paths")
    p.add_argument("--enable-google-search", action="store_true")
    p.add_argument("--enable-image-search", action="store_true")
    p.add_argument("--response-modalities", nargs="+", default=None, choices=RESPONSE_MODALITIES,
                   help=f"Default: both ({' '.join(RESPONSE_MODALITIES)})")
    p.add_argument("--thinking-level", default=DEFAULT_THINKING_LEVEL, choices=THINKING_LEVELS)
    p.add_argument("--model", default=DEFAULT_MODEL, help=f"Default: {DEFAULT_MODEL}")


def build_parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(
        description="Gemini image generation — CLI mirror of the ultimate-image-gen-mcp tools.",
    )
    sub = root.add_subparsers(dest="command", required=True)

    gi = sub.add_parser("generate-image", help="Single image (MCP: generate_image)")
    gi.add_argument("--prompt", required=True)
    _add_common_flags(gi)

    bg = sub.add_parser("batch-generate", help="Multiple images in parallel (MCP: batch_generate)")
    bg.add_argument("--prompts", required=True, nargs="+",
                    help=f"Up to {MAX_BATCH_SIZE} prompts")
    bg.add_argument("--batch-size", type=int, default=MAX_BATCH_SIZE,
                    help=f"Parallel chunk size (default: {MAX_BATCH_SIZE})")
    _add_common_flags(bg)

    return root


async def _run(args: argparse.Namespace) -> int:
    try:
        image_size = validate_image_size(args.image_size)
    except ValidationError as e:
        sys.stderr.write(f"{e}\n")
        return 1

    common = dict(
        model=args.model,
        aspect_ratio=args.aspect_ratio,
        image_size=image_size,
        output_format=args.output_format,
        reference_image_paths=args.reference_image_paths,
        enable_google_search=args.enable_google_search,
        enable_image_search=args.enable_image_search,
        response_modalities=args.response_modalities,
        thinking_level=args.thinking_level,
    )

    try:
        if args.command == "generate-image":
            out = await generate_image_tool(prompt=args.prompt, **common)
        else:
            out = await batch_generate_tool(
                prompts=args.prompts,
                batch_size=args.batch_size,
                **common,
            )
    except ValidationError as e:
        sys.stderr.write(f"{e}\n")
        return 1

    print(json.dumps(out, indent=2))

    if args.command == "generate-image":
        return 0 if out.get("success") else 1
    return 0 if out.get("failed", 0) == 0 else 1


def main() -> None:
    args = build_parser().parse_args()
    sys.exit(asyncio.run(_run(args)))


if __name__ == "__main__":
    main()
