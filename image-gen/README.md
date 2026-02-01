# Antigravity Image Generation Skill

Generate images using Google's Antigravity API with your existing credentials.

## Installation

Copy the `.skill` file to your skills directory and install it.

## Usage

After installation, simply ask to generate an image:

```
Generate a picture of a cat
```

The skill will automatically handle credentials and generate the image.

## Credential Setup

The skill uses `~/.config/antigravity/accounts.json`. On first run, it automatically creates a symlink from your existing opencode antigravity-auth config if needed.
