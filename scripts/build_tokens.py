#!/usr/bin/env python3
"""Minimal token pipeline for MVP.

- Validates required token categories.
- Resolves simple alias references like {color.bg.primary}.
- Emits CSS custom properties and resolved JSON for app/package usage.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = ROOT / "dist"
REQUIRED_TOP_LEVEL_KEYS = ["color", "space", "radius", "typography", "component"]


def load_tokens(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("token file must contain a JSON object at root")
    return data


def ensure_required_categories(data: dict[str, Any]) -> None:
    missing = [key for key in REQUIRED_TOP_LEVEL_KEYS if key not in data]
    if missing:
        raise ValueError(f"Missing required top-level categories: {', '.join(missing)}")


def flatten(obj: Any, prefix: str = "") -> dict[str, Any]:
    flat: dict[str, Any] = {}
    if isinstance(obj, dict):
        for key, value in obj.items():
            path = f"{prefix}.{key}" if prefix else key
            flat.update(flatten(value, path))
    else:
        flat[prefix] = obj
    return flat


def resolve_aliases(flat_tokens: dict[str, Any], max_passes: int = 10) -> dict[str, Any]:
    resolved = dict(flat_tokens)

    for _ in range(max_passes):
        changed = False
        for key, value in resolved.items():
            if isinstance(value, str) and value.startswith("{") and value.endswith("}"):
                ref = value[1:-1]
                if ref not in resolved:
                    raise ValueError(f"Alias reference not found: {value} in '{key}'")
                target = resolved[ref]
                if target != value:
                    resolved[key] = target
                    changed = True
        if not changed:
            break
    else:
        raise ValueError("Alias resolution exceeded maximum passes; possible cyclic alias")

    unresolved = [
        key
        for key, value in resolved.items()
        if isinstance(value, str) and value.startswith("{") and value.endswith("}")
    ]
    if unresolved:
        raise ValueError(f"Unresolved aliases remain: {', '.join(unresolved)}")

    return resolved


def normalize_css_var_name(token_path: str) -> str:
    return "--" + token_path.replace(".", "-")


def emit_css(flat_tokens: dict[str, Any], css_path: Path, selector: str = ":root") -> None:
    lines = [f"{selector} {{"]
    for key in sorted(flat_tokens):
        value = flat_tokens[key]
        lines.append(f"  {normalize_css_var_name(key)}: {value};")
    lines.append("}")
    css_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def emit_resolved_json(flat_tokens: dict[str, Any], json_path: Path) -> None:
    json_path.write_text(json.dumps(flat_tokens, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def derive_output_name(path: Path, output_name: str | None) -> str:
    if output_name:
        return output_name
    return path.stem.replace(".", "-")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate and build design tokens")
    parser.add_argument("--check", action="store_true", help="Validate only")
    parser.add_argument("--build", action="store_true", help="Validate and build outputs")
    parser.add_argument("--input", default="tokens/tokens.json", help="Input token JSON path (repo relative)")
    parser.add_argument("--output-name", help="Output file prefix (default: input filename stem)")
    parser.add_argument("--selector", default=":root", help="CSS selector for emitted variables")
    args = parser.parse_args()

    if not args.check and not args.build:
        parser.error("Specify at least one of --check or --build")

    input_path = ROOT / args.input
    if not input_path.exists():
        raise FileNotFoundError(f"Input token file not found: {args.input}")

    tokens = load_tokens(input_path)
    ensure_required_categories(tokens)

    flat = flatten(tokens)
    resolved = resolve_aliases(flat)

    if args.build:
        DIST_DIR.mkdir(parents=True, exist_ok=True)
        output_name = derive_output_name(input_path, args.output_name)
        resolved_json_path = DIST_DIR / f"{output_name}.resolved.json"
        css_path = DIST_DIR / f"{output_name}.css"
        emit_resolved_json(resolved, resolved_json_path)
        emit_css(resolved, css_path, selector=args.selector)
        print(f"Built: {resolved_json_path.relative_to(ROOT)}")
        print(f"Built: {css_path.relative_to(ROOT)}")

    print(f"Token validation passed: {args.input}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
