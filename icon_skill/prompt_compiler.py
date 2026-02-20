"""Prompt engineering for icon generation.

Every prompt starts with CONSTRAINTS_PREAMBLE to enforce the strict visual
rules required for Apple Icon Composer layers.  Variant guides add stylistic
diversity across the generated silhouettes.
"""

from __future__ import annotations

import re

# ---------------------------------------------------------------------------
# Core constraint block — prepended to every generation prompt
# ---------------------------------------------------------------------------

CONSTRAINTS_PREAMBLE = """\
Generate a 1024x1024 PNG icon layer with ALL of these rules:

BACKGROUND: Pure black background (RGB 0,0,0) filling the entire canvas.
SHAPE: Exactly ONE continuous silhouette shape — no separate pieces, no floating elements.
COLOR: The silhouette must be ONE solid flat color — absolutely NO gradients, shadows, highlights, glow, outlines, textures, or internal details.
GEOMETRY: Large smooth rounded curves. Avoid thin lines, small details, or intricate features.
COMPOSITION: Centered on the canvas with approximately 60px margin on all sides. Bold, geometric, and readable at small sizes.
CORNERS: All four corners of the image MUST be pure black (RGB 0,0,0).
STYLE: Ultra-minimal flat design. Think of a single-color vinyl sticker silhouette.
"""

# ---------------------------------------------------------------------------
# Variant style guides — each encourages a different silhouette approach
# ---------------------------------------------------------------------------

VARIANT_GUIDES = [
    "STYLE GUIDE: Bold, rounded, balanced silhouette. Symmetric and compact.",
    "STYLE GUIDE: Outer contour suggests a layered or dimensional form, but without any interior lines or detail. One solid filled shape only.",
    "STYLE GUIDE: Thick crescent or arc-based silhouette. Simple, readable, with generous curves.",
]

# ---------------------------------------------------------------------------
# Words to sanitize from prompts (they tend to trigger unwanted detail)
# ---------------------------------------------------------------------------

_BANNED_WORDS = {"petal", "petals"}


def _sanitize(text: str) -> str:
    """Replace banned words that cause the model to add unwanted detail."""
    for word in _BANNED_WORDS:
        pattern = re.compile(re.escape(word), re.IGNORECASE)
        text = pattern.sub("rounded leaf-like form", text)
    return text


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_prompts(description: str, num_variants: int = 3) -> list[str]:
    """Build a list of fully-constrained prompts for icon generation.

    Each prompt combines the constraints preamble, a variant style guide,
    and the user's description.
    """
    prompts = []
    for i in range(num_variants):
        guide = VARIANT_GUIDES[i % len(VARIANT_GUIDES)]
        raw = f"{CONSTRAINTS_PREAMBLE}\n{guide}\n\nSUBJECT: {description}"
        prompts.append(_sanitize(raw))
    return prompts


def build_edit_prompt(change_request: str) -> str:
    """Build a prompt for editing an existing icon image.

    Restates abbreviated constraints so the model doesn't drift, then
    appends the user's specific change request.
    """
    abbreviated = (
        "This is an icon layer. Maintain these rules: "
        "pure black background (RGB 0,0,0), exactly ONE continuous silhouette shape, "
        "ONE solid flat color with NO gradients/shadows/highlights/glow/outlines/textures/details, "
        "large smooth rounded curves, centered with ~60px margin, all four corners pure black."
    )
    raw = f"{abbreviated}\n\nREQUESTED CHANGE: {change_request}"
    return _sanitize(raw)


def strengthened_suffix() -> str:
    """Return a suffix to append when validation fails and we retry."""
    return (
        "\n\nCRITICAL REMINDER: The four corners MUST be pure black. "
        "Use ONLY ONE flat color for the silhouette — no gradients, no shading, "
        "no highlights. The background must be completely black. "
        "Keep the shape simple with smooth curves."
    )
