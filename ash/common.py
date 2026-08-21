from __future__ import annotations

import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


TOKEN_RE = re.compile(r"[a-z0-9][a-z0-9+.#/-]*", re.IGNORECASE)
FRONTMATTER_LIMIT = 16 * 1024
STOPWORDS = {
    "a", "an", "and", "as", "at", "be", "by", "for", "from", "in", "is", "it", "of", "on",
    "or", "the", "this", "that", "to", "with", "using", "please", "create", "make", "improve",
}


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def tokenize(value: str) -> set[str]:
    tokens: set[str] = set()
    for match in TOKEN_RE.finditer(value):
        # TOKEN_RE retains dots for useful identifiers such as ``package.json``.
        # Strip only sentence punctuation at token boundaries so a normal final
        # period does not turn ``presentation.`` into a non-matching token.
        token = match.group(0).lower().strip(".,;:!?")
        if not token:
            continue
        if token not in STOPWORDS:
            tokens.add(token)
        # Preserve the compound identifier while exposing useful role/capability
        # words from names such as engineering-multi-agent-systems-architect.
        for part in re.split(r"[-/]", token):
            if part and part not in STOPWORDS:
                tokens.add(part)
    return tokens


def stable_id(kind: str, path: Path) -> str:
    return f"{kind}:{hashlib.sha256(str(path).lower().encode('utf-8')).hexdigest()[:16]}"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def read_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        return default


def write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith(("\"", "[", "{")):
        try:
            return json.loads(value)
        except json.JSONDecodeError:
            pass
    if (value.startswith("'") and value.endswith("'")) or (value.startswith('"') and value.endswith('"')):
        return value[1:-1]
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    return value


def parse_frontmatter_prefix(path: Path) -> tuple[dict[str, Any], str | None, str]:
    """Read only the opening metadata block; never load a full skill during discovery."""
    try:
        with path.open("r", encoding="utf-8") as handle:
            prefix = handle.read(FRONTMATTER_LIMIT)
    except (OSError, UnicodeDecodeError) as exc:
        return {}, f"unreadable: {exc}", ""
    if not prefix.startswith("---"):
        return {}, "missing opening frontmatter delimiter", prefix
    closing = re.search(r"\n---\s*(?:\n|$)", prefix[3:])
    if not closing:
        return {}, "frontmatter is missing a closing delimiter within scan limit", prefix
    block = prefix[3 : 3 + closing.start()].strip("\r\n")
    metadata: dict[str, Any] = {}
    lines = block.splitlines()
    line_index = 0
    while line_index < len(lines):
        raw = lines[line_index]
        if not raw.strip() or raw.lstrip().startswith("#"):
            line_index += 1
            continue
        if raw[0].isspace() or ":" not in raw:
            line_index += 1
            continue
        key, value = raw.split(":", 1)
        marker = value.strip()
        if marker in {">", ">-", "|", "|-"}:
            # The Hub deliberately avoids a YAML dependency, but common Skills
            # use a folded multi-line description.  Preserve that metadata at
            # discovery time so routing sees the real trigger text.  Nested YAML
            # structures remain out of scope for this lightweight parser.
            line_index += 1
            parts: list[str] = []
            while line_index < len(lines) and lines[line_index][:1].isspace():
                parts.append(lines[line_index].strip())
                line_index += 1
            separator = "\n" if marker.startswith("|") else " "
            metadata[key.strip()] = separator.join(part for part in parts if part).strip()
            continue
        normalized_key = key.strip()
        if not marker and normalized_key == "metadata":
            # Skills created with the official skill-creator keep extension
            # fields under YAML ``metadata``.  Parse the small scalar/list
            # subset the Hub needs without adding PyYAML to its runtime.
            line_index += 1
            nested: dict[str, Any] = {}
            while line_index < len(lines) and lines[line_index][:1].isspace():
                nested_raw = lines[line_index].strip()
                if ":" in nested_raw and not nested_raw.startswith("#"):
                    nested_key, nested_value = nested_raw.split(":", 1)
                    nested[nested_key.strip()] = _scalar(nested_value)
                line_index += 1
            metadata[normalized_key] = nested
            continue
        metadata[normalized_key] = _scalar(value)
        line_index += 1
    return metadata, None, prefix


def first_heading(prefix: str) -> str | None:
    for line in prefix.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return None


def relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)
