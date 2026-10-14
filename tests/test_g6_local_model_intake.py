"""Meaningful inert fixtures; never approve, execute or load an external model."""
from __future__ import annotations

import ast
import hashlib
import io
import json
import os
from pathlib import Path
import stat
import struct
import tempfile
import unittest
from unittest.mock import patch
import zipfile

from ash import g6_local_model_intake as intake


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


class Memory(io.BytesIO):
    def __init__(self, raw):
        super().__init__(raw)
        self.size = len(raw)
        self.verified = False
        self.read_sizes = []

    def verify_unchanged(self):
        self.verified = True

    def read(self, size=-1):
        self.read_sizes.append(size)
        return super().read(size)


def text(value):
    raw = value.encode()
    return struct.pack("<Q", len(raw)) + raw


def model(*, version=3, architecture="qwen3", tensor_type=8, offset=0,
          dimensions=(32,), quantization=2, duplicate=False, padding=0, trailer=b""):
    kv = [("general.architecture", 8, text(architecture)),
          ("general.quantization_version", 4, struct.pack("<I", quantization))]
    if duplicate:
        kv.append(kv[0])
    raw = b"GGUF" + struct.pack("<IQQ", version, 1, len(kv))
    for key, kind, value in kv:
        raw += text(key) + struct.pack("<I", kind) + value
    raw += text("weight") + struct.pack("<I", len(dimensions))
    raw += b"".join(struct.pack("<Q", x) for x in dimensions)
    raw += struct.pack("<IQ", tensor_type, offset)
    raw += bytes([padding]) * ((-len(raw)) % 32)
    return raw + b"\0" * 34 + trailer


def archive(name="llama-completion.exe", *, special=None, duplicate=False, contents=b"INERT"):
    raw = io.BytesIO()
    item = zipfile.ZipInfo(name)
    item.create_system = 3
    item.external_attr = ((special or stat.S_IFREG) | 0o644) << 16
    with zipfile.ZipFile(raw, "w") as target:
        target.writestr(item, contents)
        if duplicate:
            import warnings
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                target.writestr(item, contents)
    expected = [{"path": name, "bytes": len(contents), "sha256": sha(contents)}]
    return raw.getvalue(), expected


class LocalModelIntakeTests(unittest.TestCase):
    def test_exact_policy_is_inert_and_pins_only_approved_candidates(self):
        policy = intake.load_policy()
        self.assertEqual(policy["mode"], "QUARANTINE_ONLY")
        self.assertIs(policy["execution_allowed"], False)
        self.assertIs(policy["registration_allowed"], False)
        self.assertEqual(len(policy["runtime"]["members"]), 51)
        self.assertEqual(policy["runtime"]["bytes"] + policy["model"]["bytes"], 658965306)
        self.assertEqual(policy["limits"], {"aggregate_artifact_bytes":700000000,
                                          "model_bytes":650000000,"unpacked_runtime_bytes":200000000})

    def test_changed_policy_cannot_select_new_subject_or_raise_bounds(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "policy.json"
            policy = intake.load_policy()
            for field in ("limits", "model", "execution_allowed", "registration_allowed"):
                original = policy[field]
                policy[field] = True
                path.write_text(json.dumps(policy), encoding="utf-8")
                with self.assertRaisesRegex(intake.SuccessorHold, "G6_POLICY_IDENTITY"), patch.object(intake,"open_stable_input") as opener:
                    intake.inspect_quarantined("absent-runtime", "absent-model", policy_path=path)
                opener.assert_not_called()
                policy[field] = original

    def test_malformed_or_missing_input_is_sanitized_not_authority(self):
        with self.assertRaisesRegex(intake.SuccessorHold, "^G6_INTAKE_HOLD$"):
            intake.inspect_quarantined("missing-sensitive-path", "also-missing")

    def test_stream_hash_bounds_size_identity_and_rewind(self):
        raw = b"fixture" * (intake.CHUNK // 7 + 10)
        stream = Memory(raw)
        self.assertEqual(intake._hash_input(stream, {"bytes":len(raw),"sha256":sha(raw)}, 0),len(raw))
        self.assertTrue(stream.verified)
        self.assertEqual(stream.tell(),0)
        self.assertLessEqual(max(stream.read_sizes),intake.CHUNK)
        for expected, base in (({"bytes":1,"sha256":sha(raw)},0),
                               ({"bytes":len(raw),"sha256":"0"*64},0),
                               ({"bytes":len(raw),"sha256":sha(raw)},700000000)):
            with self.assertRaises(intake.SuccessorHold):
                intake._hash_input(Memory(raw),expected,base)

    def test_actual_stable_reader_rejects_hardlinked_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp)/"source";path.write_bytes(b"x")
            os.link(path,Path(tmp)/"alias")
            with self.assertRaises(intake.SuccessorHold):
                intake.inspect_quarantined(path,path)

    def test_flat_exact_inventory_is_inspected_without_extraction(self):
        raw,expected=archive()
        result=intake._inspect_zip(raw,expected)
        self.assertEqual(result,{"members":1,"expanded_bytes":5,"extracted":False,"execution_subset_approved":False})

    def test_traversal_absolute_reserved_and_nonflat_members_rejected(self):
        for name in ("../escape","/absolute","a/b","NUL.exe","x.","x\\y","C:stream"):
            raw,expected=archive(name)
            with self.subTest(name=name),self.assertRaises((intake.SuccessorHold,ValueError)):
                intake._inspect_zip(raw,expected)

    def test_duplicate_unexpected_missing_and_case_alias_inventory_rejected(self):
        raw,expected=archive(duplicate=True)
        with self.assertRaises(intake.SuccessorHold):intake._inspect_zip(raw,expected)
        raw,expected=archive()
        for altered in ([],expected+expected,[{**expected[0],"path":"other"}]):
            with self.assertRaises(intake.SuccessorHold):intake._inspect_zip(raw,altered)

    def test_symlink_fifo_and_directory_entry_rejected(self):
        for kind in (stat.S_IFLNK,stat.S_IFIFO,stat.S_IFDIR):
            raw,expected=archive(special=kind)
            with self.assertRaises(intake.SuccessorHold):intake._inspect_zip(raw,expected)

    def test_member_hash_size_corruption_and_truncation_rejected(self):
        raw,expected=archive()
        for bad in ({**expected[0],"bytes":4},{**expected[0],"sha256":"0"*64}):
            with self.assertRaises(intake.SuccessorHold):intake._inspect_zip(raw,[bad])
        with self.assertRaises(zipfile.BadZipFile):intake._inspect_zip(raw[:-10],expected)

    def test_gguf_layout_checks_data_ranges_without_loading_tensors(self):
        result=intake._inspect_gguf(Memory(model()))
        self.assertEqual(result["tensor_types"],[8])
        self.assertEqual(result["tensors"],1)
        self.assertIs(result["model_loaded"],False)
        self.assertEqual(result["loader_compatibility"],"NOT_QUALIFIED")

    def test_version_architecture_quantization_and_duplicate_metadata_rejected(self):
        for args in ({"version":2},{"architecture":"other"},{"quantization":1},{"duplicate":True}):
            with self.subTest(args=args),self.assertRaises(intake.SuccessorHold):
                intake._inspect_gguf(Memory(model(**args)))

    def test_tensor_alignment_type_dimensions_and_trailer_rejected(self):
        for args in ({"tensor_type":99},{"offset":1},{"offset":32},{"dimensions":(31,)},
                     {"dimensions":()},{"dimensions":(0,)},{"padding":1},{"trailer":b"x"}):
            with self.subTest(args=args),self.assertRaises(intake.SuccessorHold):
                intake._inspect_gguf(Memory(model(**args)))

    def test_truncation_magic_and_metadata_resource_bombs_rejected(self):
        for raw in (model()[:12],b"NOPE"+model()[4:],
                    b"GGUF"+struct.pack("<IQQ",3,9999999,2),
                    b"GGUF"+struct.pack("<IQQQ",3,1,1,9999999999)):
            with self.assertRaises(intake.SuccessorHold):intake._inspect_gguf(Memory(raw))

    def test_tensor_data_padding_is_checked_without_loading_weights(self):
        header=b"GGUF"+struct.pack("<IQQ",3,2,2)
        header+=text("general.architecture")+struct.pack("<I",8)+text("qwen3")
        header+=text("general.quantization_version")+struct.pack("<II",4,2)
        for name,offset in (("first",0),("second",64)):
            header+=text(name)+struct.pack("<IQIQ",1,32,8,offset)
        header+=b"\0"*((-len(header))%32)
        self.assertEqual(intake._inspect_gguf(Memory(header+b"\0"*98))["tensors"],2)
        with self.assertRaisesRegex(intake.SuccessorHold,"G6_GGUF_PADDING"):
            intake._inspect_gguf(Memory(header+b"\0"*34+b"\1"+b"\0"*63))

    def test_production_module_has_no_execution_acquisition_or_registration_import(self):
        source=Path(intake.__file__).read_text("utf-8")
        tree=ast.parse(source)
        imports={n.module.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.ImportFrom) and n.module}
        imports.update(a.name.split('.')[0] for n in ast.walk(tree) if isinstance(n,ast.Import) for a in n.names)
        self.assertFalse(imports & {"subprocess","socket","urllib","requests","ctypes","importlib","tests"})
        self.assertNotIn("extractall",source)
        self.assertNotIn("extract(",source)


if __name__=="__main__":unittest.main()
