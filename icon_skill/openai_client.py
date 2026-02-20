"""OpenAI Image API wrapper with retry logic."""

import base64
import os
import time
from pathlib import Path

from openai import APIError, OpenAI


DEFAULT_MODEL = "gpt-image-1"
DEFAULT_SIZE = "1024x1024"
DEFAULT_QUALITY = "high"


def get_client(api_key: str | None = None) -> OpenAI:
    """Create an OpenAI client from explicit key, env var, or session state."""
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        # Try loading from session state
        from icon_skill.storage import load_session
        state = load_session()
        key = state.get("api_key")
    if not key:
        raise ValueError(
            "No OpenAI API key found. Set OPENAI_API_KEY env var, "
            "or run: python -m icon_skill set-key <KEY>"
        )
    return OpenAI(api_key=key)


def _get_model(model: str | None = None) -> str:
    """Resolve model from argument, env var, or default."""
    return model or os.environ.get("OPENAI_IMAGE_MODEL", DEFAULT_MODEL)


def generate_image(
    prompt: str,
    model: str | None = None,
    size: str = DEFAULT_SIZE,
    quality: str = DEFAULT_QUALITY,
    api_key: str | None = None,
) -> bytes:
    """Generate an image and return decoded PNG bytes.

    Retries once on APIError with a 2-second backoff.
    """
    client = get_client(api_key)
    resolved_model = _get_model(model)

    for attempt in range(2):
        try:
            response = client.images.generate(
                model=resolved_model,
                prompt=prompt,
                n=1,
                size=size,
                quality=quality,
                output_format="b64_json",
            )
            b64_data = response.data[0].b64_json
            return base64.b64decode(b64_data)
        except APIError:
            if attempt == 0:
                time.sleep(2)
                continue
            raise


def edit_image(
    image_path: str | Path,
    prompt: str,
    model: str | None = None,
    size: str = DEFAULT_SIZE,
    quality: str = DEFAULT_QUALITY,
    api_key: str | None = None,
) -> bytes:
    """Edit an existing image and return decoded PNG bytes.

    Uses the images.edit endpoint; gpt-image-1 infers the edit region from the prompt.
    Retries once on APIError with a 2-second backoff.
    """
    client = get_client(api_key)
    resolved_model = _get_model(model)
    image_path = Path(image_path)

    for attempt in range(2):
        try:
            with open(image_path, "rb") as img_file:
                response = client.images.edit(
                    model=resolved_model,
                    image=img_file,
                    prompt=prompt,
                    n=1,
                    size=size,
                    quality=quality,
                )
            b64_data = response.data[0].b64_json
            return base64.b64decode(b64_data)
        except APIError:
            if attempt == 0:
                time.sleep(2)
                continue
            raise
