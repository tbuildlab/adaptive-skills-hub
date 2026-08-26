from __future__ import annotations

import copy
import unittest

from ash.agent_contract import AgentContractError, validate_agent_task_contract


def contract() -> dict:
    return {
        "schema_version": "nexus.agent-task-contract.v1",
        "contract_id": "contract:architecture-review-001",
        "agent_id": "agent:software-architect",
        "mode": "advisory_only",
        "provenance": {
            "source_id": "agency-agents-canonical",
            "repository": "msitarzewski/agency-agents",
            "commit": "a" * 40,
            "content_sha256": None,
        },
        "task": {
            "objective_id": "objective:review-capability-model",
            "input_reference_ids": ["context:bounded-001"],
            "output_schema_id": "schema:advisory-review-v1",
        },
        "allowed_capability_ids": [],
        "limits": {"max_turns": 4, "timeout_seconds": 300, "token_budget": 8000},
        "permissions": {
            "read_only": True,
            "network": False,
            "shell": False,
            "subprocess": False,
            "write": False,
            "delegation": False,
        },
        "cancellation": {"supported": True, "signal_id": "cancel:architecture-review-001"},
        "validation": {"required": True, "validator_capability_ids": ["validator:primary-agent"]},
        "receipt": {
            "required_fields": [
                "contract_id",
                "agent_id",
                "started",
                "completed",
                "cancelled",
                "output_reference_id",
                "validation_status",
                "result_code",
            ]
        },
    }


class AgentContractTests(unittest.TestCase):
    def test_advisory_contract_is_pinned_bounded_cancellable_and_validated(self) -> None:
        result = validate_agent_task_contract(contract())
        self.assertEqual(result["mode"], "advisory_only")
        self.assertFalse(result["permissions"]["delegation"])

    def test_execution_or_delegation_authority_is_rejected(self) -> None:
        bad = contract()
        bad["mode"] = "autonomous_execution"
        with self.assertRaises(AgentContractError):
            validate_agent_task_contract(bad)
        bad = contract()
        bad["permissions"]["delegation"] = True
        with self.assertRaises(AgentContractError):
            validate_agent_task_contract(bad)

    def test_raw_context_absolute_paths_and_missing_cancellation_are_rejected(self) -> None:
        bad = contract()
        bad["task"]["raw_context"] = "secret project contents"
        with self.assertRaises(AgentContractError):
            validate_agent_task_contract(bad)
        bad = contract()
        bad["task"]["input_reference_ids"] = ["C:/Users/private/context.txt"]
        with self.assertRaises(AgentContractError):
            validate_agent_task_contract(bad)
        bad = contract()
        bad["cancellation"]["supported"] = False
        with self.assertRaises(AgentContractError):
            validate_agent_task_contract(bad)

    def test_budget_and_receipt_fields_are_fail_closed(self) -> None:
        bad = contract()
        bad["limits"]["max_turns"] = 100
        with self.assertRaises(AgentContractError):
            validate_agent_task_contract(bad)
        bad = contract()
        bad["receipt"]["required_fields"].remove("validation_status")
        with self.assertRaises(AgentContractError):
            validate_agent_task_contract(bad)


if __name__ == "__main__":
    unittest.main()
