"""Two pinned G6 artifacts: read-only, quarantine-only inspection, never loading.

No acquisition, extraction, installer, registration, model loader or dispatch API.
Frozen Slice 3C storage/path primitives are reused without changing its policy.
"""
from __future__ import annotations

from contextlib import ExitStack
import hashlib
import io
import math
from pathlib import Path
import stat
import struct
import zipfile

from .ecosystem_models import EcosystemError, normalize_candidate_path, parse_json_bytes, zero_authority
from .ecosystem_storage import open_stable_input, stable_read_bytes

POLICY = Path(__file__).resolve().parents[1] / "config/nexus-g6-local-model-intake-successor-v1.json"
POLICY_SHA256 = "16f8d981adfc798dc5baf1c2b84a6c111f3b60af0b557ce804b4afe7b555de65"
CHUNK = 1048576


class SuccessorHold(ValueError):
    """Closed diagnostics; never disclose input bytes, paths or backend errors."""


def _require(condition, code):
    if not condition:
        raise SuccessorHold(code)


def load_policy(path=POLICY):
    raw = stable_read_bytes(Path(path), maximum_bytes=32768)
    normalized = raw.decode("utf-8").replace("\r\n", "\n").encode("utf-8")
    _require(hashlib.sha256(normalized).hexdigest() == POLICY_SHA256, "G6_POLICY_IDENTITY")
    return parse_json_bytes(normalized, maximum_bytes=32768, label="G6 quarantine policy")


def _hash_input(stream, expected, aggregate):
    _require(stream.size == expected["bytes"], "G6_ARTIFACT_SIZE")
    digest = hashlib.sha256()
    total = 0
    while True:
        chunk = stream.read(min(CHUNK, expected["bytes"] - total + 1))
        if not chunk:
            break
        total += len(chunk)
        _require(total <= expected["bytes"] and aggregate + total <= 700000000, "G6_BYTE_BOUND")
        digest.update(chunk)
    stream.verify_unchanged()
    _require(total == expected["bytes"] and digest.hexdigest() == expected["sha256"], "G6_ARTIFACT_IDENTITY")
    stream.seek(0)
    return total


def _inspect_zip(raw, expected_members):
    """Flat, exact pinned inventory only; expanded bytes never touch a filesystem."""
    expected = {item["path"]: item for item in expected_members}
    _require(len(expected) == len(expected_members), "G6_ARCHIVE_INVENTORY")
    seen = set()
    total = 0
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        infos = archive.infolist()
        _require(len(infos) == len(expected) <= 64, "G6_ARCHIVE_INVENTORY")
        for info in infos:
            name = normalize_candidate_path(info.filename)
            _require(name == info.filename and "/" not in name and name in expected,
                     "G6_ARCHIVE_PATH")
            _require(name.casefold() not in seen, "G6_ARCHIVE_DUPLICATE")
            seen.add(name.casefold())
            kind = stat.S_IFMT(info.external_attr >> 16)
            _require(not info.is_dir() and kind in (0, stat.S_IFREG)
                     and not info.external_attr & (0x0200 | 0x0400)
                     and not info.flag_bits & 1 and info.compress_type in (0, 8), "G6_ARCHIVE_KIND")
            item = expected[name]
            _require(info.file_size == item["bytes"] and info.file_size <= 33554432,
                     "G6_ARCHIVE_SIZE")
            digest = hashlib.sha256()
            size = 0
            with archive.open(info) as member:
                while True:
                    chunk = member.read(min(CHUNK, item["bytes"] - size + 1))
                    if not chunk:
                        break
                    size += len(chunk)
                    total += len(chunk)
                    _require(size <= item["bytes"] and total <= 200000000, "G6_ARCHIVE_EXPANSION")
                    digest.update(chunk)
            _require(size == item["bytes"] and digest.hexdigest() == item["sha256"], "G6_MEMBER_IDENTITY")
    return {"members": len(seen), "expanded_bytes": total,
            "extracted": False, "execution_subset_approved": False}


def _inspect_gguf(stream):
    """Bounded structural check of this Qwen3 LE v3 subset; no tensor decoding.

    F32/F16/Q8_0 tensor intervals are checked, not interpreted. Unsupported types
    or layouts HOLD rather than widening this into a general model parser.
    """
    def take(size):
        _require(type(size) is int and 0 <= size <= 16777216
                 and stream.tell() + size <= min(stream.size, 67108864), "G6_GGUF_BOUND")
        raw = stream.read(size)
        _require(len(raw) == size, "G6_GGUF_TRUNCATED")
        return raw

    def number(fmt):
        return struct.unpack("<" + fmt, take(struct.calcsize("<" + fmt)))[0]

    def text(limit=1048576):
        size = number("Q")
        _require(size <= limit, "G6_GGUF_STRING")
        return take(size).decode("utf-8")

    formats = {0: "B", 1: "b", 2: "H", 3: "h", 4: "I", 5: "i", 6: "f", 7: "B", 10: "Q", 11: "q", 12: "d"}

    def value(kind, depth=0):
        _require(depth <= 1, "G6_GGUF_TYPE")
        if kind == 8:
            return text()
        if kind == 9:
            element, count = number("I"), number("Q")
            _require(depth == 0 and element in set(formats) | {8}
                     and count <= 500000, "G6_GGUF_ARRAY")
            for _ in range(count):
                value(element, depth + 1)
            return None  # Do not retain model strings or construct tokenizer arrays.
        _require(kind in formats, "G6_GGUF_TYPE")
        result = number(formats[kind])
        _require(kind != 7 or result in (0, 1), "G6_GGUF_BOOL")
        _require(kind not in (6, 12) or math.isfinite(result), "G6_GGUF_NUMBER")
        return result

    _require(take(4) == b"GGUF" and number("I") == 3, "G6_GGUF_VERSION")
    tensors, count = number("Q"), number("Q")
    _require(1 <= tensors <= 1024 and 1 <= count <= 256, "G6_GGUF_COUNT")
    keys, selected = set(), {}
    for _ in range(count):
        key = text(256)
        _require(key not in keys, "G6_GGUF_DUPLICATE")
        keys.add(key)
        kind = number("I")
        result = value(kind)
        if key in ("general.architecture", "general.alignment", "general.quantization_version"):
            selected[key] = (kind, result)
    _require(selected.get("general.architecture") == (8, "qwen3"), "G6_GGUF_ARCHITECTURE")
    _require(selected.get("general.alignment", (4, 32)) == (4, 32), "G6_GGUF_ALIGNMENT")
    tensor_names, spans, kinds = set(), [], set()
    sizes = {0: (1, 4), 1: (1, 2), 8: (32, 34)}
    for _ in range(tensors):
        name = text(64)
        _require(name and name not in tensor_names, "G6_GGUF_TENSOR_NAME")
        tensor_names.add(name)
        dimensions = number("I")
        _require(1 <= dimensions <= 4, "G6_GGUF_DIMENSIONS")
        shape = [number("Q") for _ in range(dimensions)]
        kind, offset = number("I"), number("Q")
        _require(kind in sizes and all(1 <= x <= 1000000 for x in shape), "G6_GGUF_TENSOR_TYPE")
        block, size = sizes[kind]
        _require(shape[0] % block == 0 and offset % 32 == 0, "G6_GGUF_TENSOR_ALIGNMENT")
        spans.append((offset, offset + math.prod(shape) // block * size))
        kinds.add(kind)
    data_start = (stream.tell() + 31) // 32 * 32
    _require(not any(take(data_start - stream.tell())), "G6_GGUF_PADDING")
    previous = 0
    for begin, end in sorted(spans):
        _require(begin == (previous + 31) // 32 * 32 and end <= stream.size - data_start,
                 "G6_GGUF_TENSOR_SPAN")
        stream.seek(data_start + previous)
        gap = stream.read(begin - previous)
        _require(len(gap) == begin - previous and not any(gap), "G6_GGUF_PADDING")
        previous = end
    _require(data_start + previous == stream.size, "G6_GGUF_TRAILER")
    if 8 in kinds:
        _require(selected.get("general.quantization_version") == (4, 2), "G6_GGUF_QUANTIZATION")
    return {"version": 3, "architecture": "qwen3", "metadata_fields": count,
            "tensors": tensors, "tensor_types": sorted(kinds), "tensor_data_offset": data_start,
            "loader_compatibility": "NOT_QUALIFIED", "model_loaded": False}


def inspect_quarantined(runtime_path, model_path, *, policy_path=POLICY):
    """Verify exactly two existing inert files; return evidence, never eligibility."""
    try:
        policy = load_policy(policy_path)
        with ExitStack() as stack:
            runtime = stack.enter_context(open_stable_input(Path(runtime_path), maximum_bytes=policy["runtime"]["bytes"]))
            model = stack.enter_context(open_stable_input(Path(model_path), maximum_bytes=650000000))
            _require(runtime.size + model.size <= 700000000, "G6_BYTE_BOUND")
            total = _hash_input(runtime, policy["runtime"], 0)
            total += _hash_input(model, policy["model"], total)
            archive = _inspect_zip(runtime.read(policy["runtime"]["bytes"] + 1), policy["runtime"]["members"])
            layout = _inspect_gguf(model)
            runtime.verify_unchanged()
            model.verify_unchanged()
        return {"schema": "nexus.g6.local-model-quarantine-result.v1", "status": "QUARANTINED_EXACT_BYTES",
                "policy_sha256": POLICY_SHA256, "proposal_sha256": policy["proposal_sha256"],
                "artifact_bytes": total, "runtime_sha256": policy["runtime"]["sha256"],
                "model_sha256": policy["model"]["sha256"], "archive": archive, "gguf": layout,
                "authority": zero_authority(), "execution": "DENY", "registration": "DENY",
                "privacy": "NOT_QUALIFIED", "restriction_enforcement": "NOT_QUALIFIED",
                "fresh_authenticated_exact_subject_decision": "REQUIRED_NOT_OBTAINED", "real_admission": "NO"}
    except SuccessorHold:
        raise
    except (EcosystemError, OSError, ValueError, TypeError, KeyError, EOFError, zipfile.BadZipFile, struct.error):
        raise SuccessorHold("G6_INTAKE_HOLD") from None
