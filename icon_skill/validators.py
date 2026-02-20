"""Post-generation validation for icon images.

Checks that generated images conform to the strict constraints required
for Apple Icon Composer layers (size, transparent corners, minimal color palette).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image


@dataclass
class ValidationResult:
    """Outcome of validating a single image."""

    passed: bool = True
    warnings: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return self.passed and not self.errors


def check_size(img: Image.Image, result: ValidationResult) -> None:
    """Image must be exactly 1024x1024."""
    if img.size != (1024, 1024):
        result.passed = False
        result.errors.append(f"Expected 1024x1024, got {img.size[0]}x{img.size[1]}")


def check_corners(img: Image.Image, result: ValidationResult) -> None:
    """All four corner pixels must be transparent (alpha=0) or near-black with low alpha."""
    rgba = img.convert("RGBA")
    corners = [
        ((0, 0), "top-left"),
        ((1023, 0), "top-right"),
        ((0, 1023), "bottom-left"),
        ((1023, 1023), "bottom-right"),
    ]
    for (x, y), label in corners:
        pixel = rgba.getpixel((x, y))
        alpha = pixel[3]
        # Allow fully transparent or near-transparent corners
        if alpha > 10:
            result.passed = False
            result.errors.append(
                f"Corner {label} at ({x},{y}) is RGBA{pixel}, expected transparent (alpha=0)"
            )


def check_color_count(img: Image.Image, result: ValidationResult) -> None:
    """Downsample to 256x256 and count unique opaque colors.

    Ideal: 1 opaque color (the silhouette) + transparent.
    Warn: > 5 opaque colors.
    Fail: > 20 opaque colors.
    """
    small = img.convert("RGBA").resize((256, 256), Image.NEAREST)
    # Count unique colors among non-transparent pixels only
    opaque_colors = set()
    for pixel in small.getdata():
        if pixel[3] > 10:  # Not transparent
            opaque_colors.add(pixel[:3])
    colors = len(opaque_colors)
    if colors > 20:
        result.passed = False
        result.errors.append(
            f"Too many opaque colors ({colors}) — image likely has gradients or details"
        )
    elif colors > 5:
        result.warnings.append(
            f"Opaque color count is {colors} (ideal is 1) — may have anti-aliasing or slight variation"
        )


def validate(image_path: str | Path) -> ValidationResult:
    """Run all validation checks on an image file."""
    result = ValidationResult()
    img = Image.open(image_path)
    check_size(img, result)
    if img.size == (1024, 1024):
        check_corners(img, result)
    check_color_count(img, result)
    return result
