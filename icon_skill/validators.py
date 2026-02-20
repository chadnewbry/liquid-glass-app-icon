"""Post-generation validation for icon images.

Checks that generated images conform to the strict constraints required
for Apple Icon Composer layers (size, black corners, minimal color palette).
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
    """All four corner pixels must be pure black (0,0,0)."""
    corners = [
        ((0, 0), "top-left"),
        ((1023, 0), "top-right"),
        ((0, 1023), "bottom-left"),
        ((1023, 1023), "bottom-right"),
    ]
    rgb = img.convert("RGB")
    for (x, y), label in corners:
        pixel = rgb.getpixel((x, y))
        if pixel != (0, 0, 0):
            result.passed = False
            result.errors.append(
                f"Corner {label} at ({x},{y}) is {pixel}, expected (0,0,0)"
            )


def check_color_count(img: Image.Image, result: ValidationResult) -> None:
    """Downsample to 256x256 and count unique colors.

    Ideal: 2 (black + one silhouette color).
    Warn: > 5 colors.
    Fail: > 20 colors.
    """
    small = img.convert("RGB").resize((256, 256), Image.NEAREST)
    colors = len(set(small.getdata()))
    if colors > 20:
        result.passed = False
        result.errors.append(
            f"Too many colors ({colors}) — image likely has gradients or details"
        )
    elif colors > 5:
        result.warnings.append(
            f"Color count is {colors} (ideal is 2) — may have anti-aliasing or slight variation"
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
