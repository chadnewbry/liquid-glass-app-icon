"""CLI entrypoint with generate/edit/list/set-key subcommands and REPL."""

import argparse
import sys
from pathlib import Path

from icon_skill import openai_client, prompt_compiler, storage, validators


def _generate(description: str, variants: int = 3, model: str | None = None) -> None:
    """Generate icon variants from a description."""
    prompts = prompt_compiler.build_prompts(description, num_variants=variants)
    saved_paths: list[str] = []

    for i, prompt in enumerate(prompts, start=1):
        variant_label = f"v{i}/{len(prompts)}"
        print(f"  Generating {variant_label}...")

        image_bytes = openai_client.generate_image(prompt, model=model)
        filename = storage.build_filename(description, i)
        path = storage.save_image(image_bytes, filename)
        storage.save_metadata(
            path,
            user_intent=description,
            compiled_prompt=prompt,
            model=openai_client._get_model(model),
            variant_index=i,
        )

        # Validate
        result = validators.validate(path)
        if not result.ok:
            print(f"  {variant_label} validation failed: {'; '.join(result.errors)}")
            print(f"  Retrying with strengthened constraints...")
            stronger = prompt + prompt_compiler.strengthened_suffix()
            image_bytes = openai_client.generate_image(stronger, model=model)
            path.write_bytes(image_bytes)
            result = validators.validate(path)
            if not result.ok:
                print(f"  {variant_label} still has issues: {'; '.join(result.errors)}")
            else:
                print(f"  {variant_label} passed on retry")
        else:
            if result.warnings:
                print(f"  {variant_label} warnings: {'; '.join(result.warnings)}")
            else:
                print(f"  {variant_label} passed validation")

        saved_paths.append(str(path))
        print(f"  Saved: {path}")

    storage.update_session_after_generate(saved_paths, description, openai_client._get_model(model))
    print(f"\nGenerated {len(saved_paths)} icon(s) in: {storage.get_output_dir()}")


def _edit(change: str, source_path: str | None = None, model: str | None = None) -> None:
    """Edit an existing icon image."""
    if source_path is None:
        state = storage.load_session()
        if not state["last_generated"]:
            print("Error: No previous generation found. Use --on to specify an image.")
            sys.exit(1)
        source_path = state["last_generated"][0]

    if not Path(source_path).exists():
        print(f"Error: Source image not found: {source_path}")
        sys.exit(1)

    state = storage.load_session()
    edit_num = state.get("edit_count", 0) + 1

    print(f"  Editing: {source_path}")
    prompt = prompt_compiler.build_edit_prompt(change)
    image_bytes = openai_client.edit_image(source_path, prompt, model=model)

    filename = storage.build_edit_filename(source_path, edit_num)
    path = storage.save_image(image_bytes, filename)
    storage.save_metadata(
        path,
        user_intent=change,
        compiled_prompt=prompt,
        model=openai_client._get_model(model),
        parent_image=source_path,
    )

    result = validators.validate(path)
    if not result.ok:
        print(f"  Validation failed: {'; '.join(result.errors)}")
        print(f"  Retrying with strengthened constraints...")
        stronger = prompt + prompt_compiler.strengthened_suffix()
        image_bytes = openai_client.edit_image(source_path, stronger, model=model)
        path.write_bytes(image_bytes)
        result = validators.validate(path)
        if not result.ok:
            print(f"  Still has issues: {'; '.join(result.errors)}")
        else:
            print(f"  Passed on retry")
    else:
        if result.warnings:
            print(f"  Warnings: {'; '.join(result.warnings)}")
        else:
            print(f"  Passed validation")

    storage.update_session_after_edit(str(path), change)
    print(f"  Saved: {path}")


def _list_images() -> None:
    """List all generated images."""
    images = storage.list_generated_images()
    if not images:
        print("No generated images found.")
        return
    print(f"Generated images ({len(images)}):")
    for img in images:
        meta_path = img.with_suffix(".json")
        label = ""
        if meta_path.exists():
            import json
            meta = json.loads(meta_path.read_text())
            label = f" — {meta.get('user_intent', '')}"
        print(f"  {img.name}{label}")


def _set_key(key: str) -> None:
    """Store an OpenAI API key in session state."""
    state = storage.load_session()
    state["api_key"] = key
    storage.save_session(state)
    print("API key saved to session state.")


def _repl() -> None:
    """Interactive REPL mode."""
    print("Liquid Glass Icon Generator — Interactive Mode")
    print("Commands: generate <desc>, edit <change>, list, set-key <key>, quit")
    print()

    while True:
        try:
            line = input("icon> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break

        if not line:
            continue

        parts = line.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("quit", "exit", "q"):
            break
        elif cmd == "generate":
            if not arg:
                print("Usage: generate <description>")
                continue
            _generate(arg)
        elif cmd == "edit":
            if not arg:
                print("Usage: edit <change description>")
                continue
            _edit(arg)
        elif cmd == "list":
            _list_images()
        elif cmd == "set-key":
            if not arg:
                print("Usage: set-key <OPENAI_API_KEY>")
                continue
            _set_key(arg)
        else:
            print(f"Unknown command: {cmd}")
            print("Commands: generate <desc>, edit <change>, list, set-key <key>, quit")


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="icon-skill",
        description="Liquid Glass App Icon Generator",
    )
    sub = parser.add_subparsers(dest="command")

    # generate
    gen = sub.add_parser("generate", help="Generate icon variants")
    gen.add_argument("description", help="What the icon should depict")
    gen.add_argument("--variants", type=int, default=3, help="Number of variants (default: 3)")
    gen.add_argument("--model", help="OpenAI image model to use")

    # edit
    ed = sub.add_parser("edit", help="Edit the last generated icon")
    ed.add_argument("change", help="Describe the change to make")
    ed.add_argument("--on", dest="source", help="Path to source image (default: last generated)")
    ed.add_argument("--model", help="OpenAI image model to use")

    # list
    sub.add_parser("list", help="List generated images")

    # set-key
    sk = sub.add_parser("set-key", help="Store OpenAI API key")
    sk.add_argument("key", help="Your OpenAI API key")

    args = parser.parse_args()

    if args.command is None:
        _repl()
    elif args.command == "generate":
        _generate(args.description, variants=args.variants, model=args.model)
    elif args.command == "edit":
        _edit(args.change, source_path=args.source, model=args.model)
    elif args.command == "list":
        _list_images()
    elif args.command == "set-key":
        _set_key(args.key)


if __name__ == "__main__":
    main()
