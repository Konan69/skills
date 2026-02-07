---
name: antigravity-image-gen
description: Generate images using Google's Antigravity API (Gemini image generation). Use when user requests to create, generate, or make an image/picture (e.g., "generate a cat picture", "create an image of a sunset"). Handles OAuth authentication and credential storage automatically. Credentials stored securely in ~/.config/antigravity/ (never in project directories).
---

# Antigravity Image Generation

## Authentication

Credentials are stored at `~/.config/antigravity/accounts.json` (file permissions 600). Never stored in project directories.

**First-time setup** — run the auth script to sign in via browser:
```bash
python scripts/auth.py
```

If generation fails with a token error, re-run `python scripts/auth.py`.

## Generating Images

```bash
python scripts/generate_image.py --prompt "A cat sitting on a windowsill" --output ./cat.png
```

### Arguments

- `--prompt` (required): Image description
- `--output` (required): Output file path
- `--config` (optional): imageConfig JSON for aspect ratio control

### Aspect Ratios

Pass via `--config`:
- `"1:1"` — Square (default)
- `"16:9"` — Widescreen
- `"4:3"` — Landscape
- `"9:16"` — Portrait
- `"3:4"` — Tall portrait

```bash
python scripts/generate_image.py \
  --prompt "A sunset over mountains" \
  --output ./sunset.jpg \
  --config '{"aspectRatio":"16:9"}'
```

### Output

On success, prints the output file path to stdout. Use this path to reference the generated image.

## API Details

See [references/api.md](references/api.md) for endpoint details and request/response formats.
