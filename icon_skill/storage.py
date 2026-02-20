"""File I/O, naming conventions, and session state management."""

import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path


def _slugify(text: str, max_len: int = 40) -> str:
    """Convert text to a filesystem-safe slug."""
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^\w\s-]", "", text.lower())
    text = re.sub(r"[-\s]+", "-", text).strip("-")
    return text[:max_len]


def get_output_dir() -> Path:
    """Return the output directory, creating it if needed."""
    local = Path.cwd() / "Icon Composer Layers"
    try:
        local.mkdir(parents=True, exist_ok=True)
        return local
    except OSError:
        fallback = Path.home() / "Icon Composer Layers"
        fallback.mkdir(parents=True, exist_ok=True)
        return fallback


def build_filename(description: str, variant_index: int) -> str:
    """Build a timestamped filename for a generated icon variant."""
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    slug = _slugify(description)
    return f"{stamp}_{slug}_v{variant_index}.png"


def build_edit_filename(source_path: str, edit_number: int) -> str:
    """Build a filename for an edit of an existing image."""
    p = Path(source_path)
    stem = p.stem
    # Strip any existing _editN suffix to get the base
    base = re.sub(r"_edit\d+$", "", stem)
    return f"{base}_edit{edit_number}.png"


def save_image(image_bytes: bytes, filename: str) -> Path:
    """Save raw PNG bytes to the output directory."""
    out_dir = get_output_dir()
    path = out_dir / filename
    path.write_bytes(image_bytes)
    return path


def save_metadata(
    output_path: Path,
    *,
    user_intent: str,
    compiled_prompt: str,
    model: str,
    variant_index: int | None = None,
    parent_image: str | None = None,
) -> Path:
    """Save sidecar JSON metadata next to a PNG."""
    meta = {
        "user_intent": user_intent,
        "compiled_prompt": compiled_prompt,
        "model": model,
        "created_at": datetime.now().isoformat(),
        "variant_index": variant_index,
        "parent_image": parent_image,
        "output_path": str(output_path),
    }
    meta_path = output_path.with_suffix(".json")
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta_path


# --- Session state ---

def _state_path() -> Path:
    return get_output_dir() / "session_state.json"


def load_session() -> dict:
    """Load session state from disk, or return defaults."""
    path = _state_path()
    if path.exists():
        try:
            return json.loads(path.read_text())
        except (json.JSONDecodeError, OSError):
            pass
    return {
        "last_generated": [],
        "last_description": "",
        "last_model": "",
        "edit_count": 0,
        "history": [],
    }


def save_session(state: dict) -> None:
    """Persist session state to disk."""
    path = _state_path()
    path.write_text(json.dumps(state, indent=2))


def update_session_after_generate(
    paths: list[str], description: str, model: str
) -> None:
    """Update session state after a generate command."""
    state = load_session()
    state["last_generated"] = paths
    state["last_description"] = description
    state["last_model"] = model
    state["edit_count"] = 0
    state["history"].append({
        "action": "generate",
        "description": description,
        "paths": paths,
        "timestamp": datetime.now().isoformat(),
    })
    save_session(state)


def update_session_after_edit(path: str, change: str) -> None:
    """Update session state after an edit command."""
    state = load_session()
    state["edit_count"] = state.get("edit_count", 0) + 1
    state["last_generated"] = [path]
    state["history"].append({
        "action": "edit",
        "change": change,
        "path": path,
        "timestamp": datetime.now().isoformat(),
    })
    save_session(state)


def list_generated_images() -> list[Path]:
    """List all generated PNGs in the output directory, newest first."""
    out_dir = get_output_dir()
    pngs = sorted(out_dir.glob("*.png"), key=lambda p: p.stat().st_mtime, reverse=True)
    return pngs
