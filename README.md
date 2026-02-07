# Skills

Claude Code agent skills.

## antigravity-image-gen

Generate images using Google's Antigravity API (Gemini image generation).

### Setup

```bash
# One-time auth (opens browser for Google sign-in)
python antigravity-image-gen/scripts/auth.py
```

Credentials are stored at `~/.config/antigravity/accounts.json` — never in project directories.

### Usage

```bash
python antigravity-image-gen/scripts/generate_image.py \
  --prompt "A cat sitting on a windowsill" \
  --output ./cat.png
```

With aspect ratio:
```bash
python antigravity-image-gen/scripts/generate_image.py \
  --prompt "A sunset over mountains" \
  --output ./sunset.jpg \
  --config '{"aspectRatio":"16:9"}'
```
