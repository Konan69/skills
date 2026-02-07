---
name: antigravity-image-gen
description: Generate images using Antigravity API. Use when user requests to create, generate, or create an image of something (e.g., "generate a cat picture"). Automatically sets up credentials via symlink on first run.
---

# Antigravity Image Generation

Generate images using Google's Antigravity API with your existing credentials.

## Usage

```bash
python scripts/generate_image.py --prompt "A cat sitting" --output ./cat.png
```

## Arguments

- `--prompt` (required): Image description
- `--output` (required): File path where image will be saved
- `--config` (optional): Full imageConfig JSON for advanced control
- `--refresh-token` (optional): Direct refresh token (overrides accounts file)
- `--project-id` (optional): Direct project ID (use with --refresh-token)

## Image Config Options

Use `--config` to pass image generation options. Agent should choose based on request.

- `aspectRatio`: Image aspect ratio
  - `"1:1"` (default): Square
  - `"16:9"`: Widescreen landscape
  - `"4:3"`: Landscape
  - `"9:16"`: Portrait
  - `"3:4"`: Tall portrait

Example:
```bash
python scripts/generate_image.py \
  --prompt "A sunset over mountains" \
  --output ./sunset.jpg \
  --config '{"aspectRatio":"16:9"}'
```

## Credentials

Skill automatically uses `~/.config/antigravity/accounts.json`. On first run, creates symlink from existing opencode config if needed.

## Output

Script prints output file path. Use this path to reference generated image.

## Future Enhancement

Direct credential management (OAuth login flow) will be added to match opencode plugin's auth setup.
