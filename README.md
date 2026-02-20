# 🧊 Liquid Glass App Icon Generator

I built this repo so that I could quickly and easily generate images to be used in Icon Composer to make iOS app icons. I packaged it this way so that Claude can easily add this as a skill, and then you can simply ask Claude to generate an app icon for you, and it will find the skill and do so.

Generate ultra-minimal, flat silhouette **1024×1024 PNGs** for Apple's liquid glass icon layers — powered by the OpenAI Image API.

<p align="center">
  <img src="Example/rocket-icon-composer-iOS-Dark-256x256@2x.png" width="256" alt="Rocket icon with liquid glass effect">
</p>

<p align="center">
  <img src="Icon Composer Layers/2026-02-20_122837_a-rocket_v1.png" width="200" alt="Orange rocket icon">
  <img src="Icon Composer Layers/2026-02-20_123000_a-rocket_v2.png" width="200" alt="Black rocket icon">
  <img src="Icon Composer Layers/2026-02-20_123539_a-rocket-deep-burnt-orange-silhouette-co_v1.png" width="200" alt="Deep orange rocket icon">
</p>

## ✨ Features

- 🎨 Single flat-color silhouette on transparent background
- 🔁 Auto-validates output (size, transparency, color count) and retries on failure
- ✏️ Edit existing icons with natural language ("make it blue")
- 🤖 Ships as a [Claude Code](https://claude.ai/claude-code) skill (`/icon-generate`)
- 📦 Sidecar `.json` metadata for every generated PNG

## 🚀 Quickstart

1. Open [Claude Code](https://claude.ai/claude-code)
2. Ask Claude:
   ```
   Can you add the skill from this project? https://github.com/chadnewbry/liquid-glass-app-icon
   ```
3. Start generating icons:
   ```
   Generate me an app icon of a rocket in deep orange
   ```

## 📥 Installation

```bash
git clone https://github.com/chadnewbry/liquid-glass-app-icon.git
cd liquid-glass-app-icon
uv venv && uv pip install -e .
export OPENAI_API_KEY=sk-...
```

## 📖 Usage

### Generate

```bash
python -m icon_skill generate "a rocket" --variants 3
```

### Edit

```bash
python -m icon_skill edit "make the color deeper orange"
python -m icon_skill edit "make it blue" --on path/to/icon.png
```

### List

```bash
python -m icon_skill list
```

### Store API key

```bash
python -m icon_skill set-key sk-...
```

### Interactive REPL

```bash
python -m icon_skill
```

## 🤖 Claude Code Skill

Clone this repo and the `/icon-generate` skill is available automatically:

```
> /icon-generate a camera icon in white
```

## 📁 Output

Icons are saved to `./Icon Composer Layers/` with timestamped filenames:

```
Icon Composer Layers/
├── 2026-02-20_122837_a-rocket_v1.png
├── 2026-02-20_122837_a-rocket_v1.json   ← metadata
└── ...
```

## ⚙️ Options

| Flag | Default | Description |
|---|---|---|
| `--variants N` | `3` | Number of variants to generate |
| `--model MODEL` | `gpt-image-1` | OpenAI image model |
| `--on PATH` | last generated | Source image for edits |

Set `OPENAI_IMAGE_MODEL` env var to change the default model.

## 📋 Requirements

- Python ≥ 3.11
- [uv](https://docs.astral.sh/uv/) (recommended) or pip
- OpenAI API key with image generation access
