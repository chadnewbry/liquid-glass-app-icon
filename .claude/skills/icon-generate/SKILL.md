---
name: icon-generate
description: Generate ultra-minimal flat silhouette app icon PNGs for Apple Icon Composer liquid glass layers
trigger: generate icon, create icon, make icon layer, edit icon, icon for, app icon
---

# Icon Generate Skill

Generate Apple Icon Composer-ready 1024x1024 PNG icon layers with ultra-minimal flat silhouettes on pure black backgrounds.

## How to use

When the user asks to generate or create an icon, translate their request into a CLI invocation.

### Generate icons

Run the CLI via Bash to generate icon variants:

```bash
cd /Users/chadnewbry/dev/liquid-glass-app-icon && uv run python -m icon_skill generate "<description>" --variants <N>
```

- Parse the user's request into a concise description (e.g., "make me a rocket icon" becomes `"a rocket"`)
- Default to 3 variants unless the user specifies otherwise
- Use `--model gpt-image-1` (default) or `--model gpt-image-1.5` if requested

### Edit an existing icon

When the user wants to modify the last generated icon:

```bash
cd /Users/chadnewbry/dev/liquid-glass-app-icon && uv run python -m icon_skill edit "<change description>"
```

- Translate requests like "make it blue" into `edit "change the shape color to blue"`
- Translate "make it bigger" into `edit "make the silhouette larger while keeping it centered"`
- Use `--on <path>` to edit a specific image instead of the last generated one

### List generated icons

```bash
cd /Users/chadnewbry/dev/liquid-glass-app-icon && uv run python -m icon_skill list
```

### Set API key

```bash
cd /Users/chadnewbry/dev/liquid-glass-app-icon && uv run python -m icon_skill set-key <KEY>
```

## After running

- Report the file paths of generated/edited images to the user
- Report any validation warnings or errors
- If validation failed and retried, mention that a retry was attempted
- The output directory is `./Icon Composer Layers/`

## Important notes

- The tool requires an `OPENAI_API_KEY` environment variable or a key set via `set-key`
- Each generation creates a PNG and a sidecar `.json` metadata file
- Icons are pure black background with a single flat-color silhouette — ideal as icon layers for Apple's liquid glass effect
- The tool automatically validates output (size, corner colors, color count) and retries once on failure
