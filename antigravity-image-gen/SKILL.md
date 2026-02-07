---
name: antigravity-image-gen
description: Generate images using Google's Antigravity API (Gemini image generation). Use when user requests to create, generate, or make an image/picture (e.g., "generate a cat picture", "create an image of a sunset"). Credentials stored securely in ~/.config/antigravity/ (never in project directories).
---

# Antigravity Image Generation

## Workflow

1. **Check credentials exist** — verify `~/.config/antigravity/accounts.json` exists
2. **If missing** — tell the user to run the auth script manually (it opens a browser, agent cannot do this):
   ```
   python scripts/auth.py
   ```
   Wait for the user to confirm sign-in before proceeding.
3. **Generate image** — run the generate script (non-interactive, safe for agent to execute):
   ```bash
   python scripts/generate_image.py --prompt "description" --output ./path.png
   ```
4. **If token error** — tell the user to re-run `python scripts/auth.py` to refresh credentials.

## generate_image.py Arguments

- `--prompt` (required): Image description
- `--output` (required): Output file path
- `--config` (optional): imageConfig JSON for aspect ratio

## Aspect Ratios

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

## Output

On success, prints the output file path to stdout.

## Credential Storage

All credentials live at `~/.config/antigravity/accounts.json` (permissions 600, gitignored). Never stored in project directories — safe to add this skill to any project.

## API Details

See [references/api.md](references/api.md) for endpoint and request/response format details.
