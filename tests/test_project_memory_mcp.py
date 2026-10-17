from __future__ import annotations

import asyncio
from copy import deepcopy
import hashlib
import json
import os
from pathlib import Path
import sys
import unittest

from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from ash import project_memory as m
from ash.project_memory_context import ProjectMemoryReader, attach_context
from ash.project_memory_store import MemoryStore
from tests.test_project_memory import fixture, temporary

ROOT = Path(__file__).resolve().parents[1]
SERVER = r'''
import asyncio,json,os,runpy,stat,sys
from pathlib import Path
sys.path.insert(0,sys.argv[1])
from ash.mcp.adapter import NexusMcpRuntime
NexusMcpRuntime._build_catalog=staticmethod(lambda:{'skills':[],'agents':[]})
entry,config,audit_path=sys.argv[2:]
audit_handle=open(audit_path,'w',encoding='utf-8')
events={'network_attempts':[],'write_attempts':[]}
original_run=asyncio.run
def audit(event,args):
    if event in {'socket.connect','socket.getaddrinfo','socket.sendto','urllib.Request','subprocess.Popen','os.system'}:
        events['network_attempts'].append(event)
        raise RuntimeError('planning network forbidden')
    mutation=event in {'os.mkdir','os.remove','os.rename','os.rmdir','os.truncate','os.utime','os.chmod','os.link','os.symlink'}
    if event=='open' and not (isinstance(args[0],int) and stat.S_ISFIFO(os.fstat(args[0]).st_mode)):
        mode,flags=args[1:3]
        mutation=(isinstance(mode,str) and any(c in mode for c in 'wax+')) or (isinstance(flags,int) and bool(flags&(os.O_WRONLY|os.O_RDWR|os.O_CREAT|os.O_TRUNC|os.O_APPEND)))
    if mutation:
        events['write_attempts'].append(event)
        raise RuntimeError('planning write forbidden')
def guarded_run(coro,**kwargs):
    async def wrapped():
        sys.addaudithook(audit)
        return await coro
    try:
        return original_run(wrapped(),**kwargs)
    finally:
        audit_handle.write(json.dumps(events))
        audit_handle.flush()
asyncio.run=guarded_run
sys.argv=[entry,'--workspace-config',config]
runpy.run_path(entry,run_name='__main__')
'''


class MemoryMcpTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.temp = temporary()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.proposal, self.workspace = fixture(self.root)
        self.proposal["artifacts"] = [dict(id="artifact", locator="artifact.txt", sha256=hashlib.sha256((self.workspace.root / "artifact.txt").read_bytes()).hexdigest())]
        self.config = dict(schema_version="nexus.project-memory.config.v1", enabled=True,
                           root=str(self.root / "memory"), required_drive="D:")
        self.workspace_config = self.root / "workspaces.json"
        foreign = self.root / "foreign"
        foreign.mkdir()
        self.workspace_config.write_bytes(m.encoded({"schema_version": "nexus.mcp.workspace.v1",
            "workspaces": {"project": {"root": str(self.workspace.root)}, "foreign": {"root": str(foreign)}}}))
        (self.root / m.CONFIG_NAME).write_bytes(m.encoded(self.config))
        self.store = MemoryStore(self.config)
        self.store.initialize(self.workspace, authorized=True, authorization_ref="test-owner")
        for key, tags in (("navigation", ["navigation"]), ("database", ["database"])):
            self.proposal["lessons"].append(dict(id=key, kind="failed_attempt", tags=tags,
                summary=f"Check {key} boundaries", confidence="verified", evidence_refs=["validation"],
                symptom="Observed boundary mismatch", root_cause_status="unknown", root_cause="",
                correction="Adjusted check", validation_result="passed", prevention="Include boundary regression"))
        self.receipt = self.store.persist(self.proposal, self.workspace, authorized=True, privacy_reviewed=True,
            authorization_ref="test-owner", expected_previous_digest=None)

    def metadata(self):
        return {p.name: (p.stat().st_mtime_ns, hashlib.sha256(p.read_bytes()).hexdigest())
                for p in (self.store.path / "projects").iterdir()}

    async def request_process(self, number, cases):
        audit = self.root / f"audit-{number}.json"
        params = StdioServerParameters(command=sys.executable,
            args=["-B", "-c", SERVER, str(ROOT), str(ROOT / "scripts/nexus_mcp.py"), str(self.workspace_config), str(audit)],
            cwd=str(ROOT), env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"})
        payloads = []
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                tools = await session.list_tools()
                self.assertFalse(any(t.name.startswith("nexus.write") or "persist" in t.name for t in tools.tools))
                for args in cases:
                    result = await session.call_tool("nexus.plan_task", args)
                    self.assertFalse(result.is_error)
                    payloads.append(json.loads(result.content[0].text))
        self.assertEqual(json.loads(audit.read_text(encoding="utf-8")), {"network_attempts": [], "write_attempts": []})
        return payloads

    async def test_fresh_process_auto_lookup_isolation_and_independent_planning(self):
        before = self.metadata()
        args = {"task": "Redesign the website navigation", "workspace_id": "project"}
        cases = [args, {**args, "workspace_id": "foreign"}, {**args, "project_context_mode": "none"},
                 {**args, "constraints": ["network", "no_network"]},
                 {**args, "task": "Fix a tiny website typo"},
                 {**args, "task": "Create a website from a complete specification"},
                 {**args, "task": "Create a website; do not search"}]
        results = await self.request_process(1, cases)
        memory = results[0]["project_memory"]
        self.assertEqual(memory["status"], "project_memory_loaded")
        self.assertEqual(memory["current_state"]["name"], "Portfolio")
        self.assertEqual(memory["artifacts"][0]["locator"], "artifact.txt")
        self.assertEqual(memory["current_state"]["completion"]["kind"], "validated_checkpoint")
        self.assertEqual([lesson["id"] for lesson in memory["lessons"]], ["navigation"])
        self.assertEqual(results[1]["project_memory"]["status"], "project_memory_missing")
        self.assertEqual(results[2]["project_memory"]["status"], "project_memory_disabled")
        self.assertEqual(results[0]["reference_research"], results[2]["reference_research"])
        self.assertEqual(results[0]["fallback"]["reason_code"], "CAPABILITY_NOT_COVERED")
        self.assertEqual(results[3]["reference_research"]["reusable_references"]["status"], "HOLD_owner_decision")
        self.assertEqual([r["reference_research"]["status"] for r in results[4:]], ["skipped", "reduced", "skipped"])
        self.assertNotIn(str(self.root), json.dumps(memory))
        fresh = (await self.request_process(2, [args]))[0]
        self.assertEqual(fresh["project_memory"], memory)
        self.assertEqual(self.metadata(), before)

    async def test_missing_config_and_malformed_are_non_blocking(self):
        (self.root / m.CONFIG_NAME).unlink()
        args = {"task": "Redesign the website", "workspace_id": "project"}
        result = (await self.request_process(3, [args]))[0]
        self.assertEqual(result["project_memory"]["status"], "project_memory_unavailable")
        (self.root / m.CONFIG_NAME).write_bytes(m.encoded(self.config))
        path = next((self.store.path / "projects").iterdir())
        path.write_bytes(b"{}")
        result = (await self.request_process(4, [args]))[0]
        self.assertNotEqual(result["project_memory"]["status"], "project_memory_loaded")
        self.assertEqual(result["fallback"]["reason_code"], "CAPABILITY_NOT_COVERED")

    async def test_prior_relevant_lessons_retained_and_latest_state_selected(self):
        update = deepcopy(self.proposal)
        update["lessons"] = []
        update["state"]["stack"] = ["HTML", "CSS"]
        self.store.persist(update, self.workspace, authorized=True, privacy_reviewed=True,
            authorization_ref="test-owner", expected_previous_digest=self.receipt["revision_digest"])
        before = self.metadata()
        memory = ProjectMemoryReader(self.workspace_config)(self.workspace, "navigation")
        self.assertEqual(memory["revision"], 2)
        self.assertEqual(memory["current_state"]["state"]["stack"], ["HTML", "CSS"])
        self.assertEqual(memory["lessons"][0]["source_revision"], 1)
        self.assertEqual(self.metadata(), before)

    async def test_unavailable_d_root_and_ambiguity_are_visible_non_blocking(self):
        config = {**self.config, "root": str(self.root / "missing")}
        (self.root / m.CONFIG_NAME).write_bytes(m.encoded(config))
        reader = ProjectMemoryReader(self.workspace_config)
        self.assertEqual(reader(self.workspace, "navigation")["status"], "project_memory_unavailable")
        (self.root / m.CONFIG_NAME).write_bytes(m.encoded(self.config))
        update = deepcopy(self.proposal)
        update["identity"]["project_id"] = "b" * 32
        update["completion"].update(kind="incomplete", automated_validation="not_run")
        update["state"]["completed_scope"] = []
        self.store.persist(update, self.workspace, authorized=True, privacy_reviewed=True,
            authorization_ref="test-owner", expected_previous_digest=None)
        self.assertEqual(reader(self.workspace, "navigation")["status"], "project_memory_ambiguous")
        self.assertEqual(reader(self.workspace, "navigation", "a" * 32)["status"], "project_memory_loaded")

    async def test_adapter_rejects_unapproved_memory_fields_and_bounds_projection(self):
        payload = {"status": "fallback_needed", "warnings": [], "execution_steps": []}
        memory = ProjectMemoryReader(self.workspace_config)(self.workspace, "navigation")
        memory["raw_transcript"] = "unapproved"
        result = attach_context(payload, memory)
        self.assertEqual(result["project_memory"]["status"], "project_memory_invalid")
        self.assertNotIn("raw_transcript", json.dumps(result))
        memory = ProjectMemoryReader(self.workspace_config)(self.workspace, "navigation")
        from ash.mcp.schemas import MAX_SAFE_ENVELOPE_BYTES
        # Leave room for a visible omission status but not the full memory body.
        crowded = {**payload, "padding": "x" * (MAX_SAFE_ENVELOPE_BYTES - 512)}
        result = attach_context(crowded, memory)
        self.assertEqual(result["project_memory"]["status"], "project_memory_context_overflow")
        self.assertLessEqual(len(m.encoded(result)), MAX_SAFE_ENVELOPE_BYTES)
        self.assertEqual(result["status"], payload["status"])


if __name__ == "__main__":
    unittest.main()
