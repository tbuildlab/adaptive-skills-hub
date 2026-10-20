"""Focused regressions for the approved D001/D002/D003/D004/D007 repairs.

Fixtures confer no production trust. Original qualification receipts and gold
labels remain external immutable evidence, not rewritten by these tests.
"""
from pathlib import Path
import asyncio
import json
import tempfile
import unittest
from unittest.mock import Mock
import mcp_types as types

from ash.mcp.schemas import NexusMcpError, parse_health_request
from ash.mcp.server import create_server
from ash.mcp.redaction import safe_health
from ash.reference_research import reference_research_plan
from ash.semantic_domains import semantic_task_model, task_intent_text
from ash.v2 import load_plan_skills, plan_task
from tests.test_semantic_routing import skill


class CapabilityLabRepairTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.skills = [skill(self.root, name, name=name, description=description,
            domains=('frontend_implementation',), task_kinds=('animation',))
            for name, description in (
                ('gsap-core', 'GSAP core opacity tween animation'),
                ('gsap-scrolltrigger', 'GSAP ScrollTrigger scroll pin scrub animation'),
                ('gsap-react', 'GSAP React scoped animation'),
                ('gsap-timeline', 'GSAP timeline sequencing animation'),
            )]

    def tearDown(self):
        self.temp.cleanup()

    def plan(self, task, records=None, **kwargs):
        return plan_task(task, {'skills': self.skills if records is None else records, 'agents': []}, self.root, **kwargs)

    def test_plan_only_dom_and_plain_js_establish_frontend_domain(self):
        for task in (
            'Plan a GSAP DOM tween for a badge.',
            'Draft a plain JavaScript opacity animation plan.',
            'Recommend an animation workflow for a vanilla JavaScript DOM tooltip.',
        ):
            with self.subTest(task=task):
                plan = self.plan(task, [self.skills[0]])
                self.assertEqual([x.name for x in plan.selected], ['gsap-core'])
                loaded = load_plan_skills(plan)
                self.assertNotIn('load_error', loaded[0])
                self.assertEqual(loaded[0]['sha256'], plan.selected[0].record['content_sha256'])

    def test_negation_quotes_and_non_dom_work_do_not_select_gsap(self):
        for task in (
            'Fix frontend CSS spacing. There is no movement or animation.',
            'Implement GLSL mesh animation. Do not use DOM animation or frontend GSAP.',
            'Review Python data named "React GSAP animation" for parsing errors.',
            "Review a Python parser using the literal 'frontend GSAP tween'.",
            'Create an HTML form; never animate its controls.',
            'Fix frontend HTML spacing, not animation or motion.',
            'Fix CSS padding; avoid animation and GSAP tweens.',
        ):
            with self.subTest(task=task):
                self.assertEqual(self.plan(task).selected, [])

    def test_positive_clause_survives_separate_exclusion(self):
        task = 'Do not scroll or pin; instead implement an HTML opacity tween using GSAP.'
        plan = self.plan(task)
        self.assertEqual([x.name for x in plan.selected], ['gsap-core'])
        self.assertNotIn('scroll', task_intent_text(task))
        self.assertEqual([x.name for x in self.plan('Implement not only HTML but also a GSAP animation.', [self.skills[0]]).selected], ['gsap-core'])

    def test_visual_comparison_needs_source_and_implementation_roles(self):
        for task in (
            'Audit UX onboarding layout and accessibility.',
            'Read a PDF and review its rendered page layout.',
            "Review code with the comment 'compare implementation with design'.",
            'Plan a visual QA comparison. No source mockup or rendered implementation is available.',
        ):
            with self.subTest(task=task):
                self.assertNotIn('visual_design_qa', semantic_task_model(task).required_domains)
        for task in (
            'Compare the rendered interface with the approved visual design.',
            'Review a rendered prototype against its supplied design image.',
        ):
            with self.subTest(task=task):
                self.assertIn('visual_design_qa', semantic_task_model(task).required_domains)

    def test_scrolltrigger_requires_one_specialist_not_all_gsap(self):
        plan = self.plan('Implement a frontend GSAP ScrollTrigger animation with scrub and pinning.')
        self.assertEqual([x.name for x in plan.selected], ['gsap-scrolltrigger'])
        self.assertEqual(plan.fallback['status'], 'not_needed')

    def test_missing_specialist_remains_honest_gap(self):
        plan = self.plan('Plan a DOM ScrollTrigger animation with pin and scrub.', [self.skills[0]])
        self.assertEqual(plan.selected, [])
        self.assertEqual(plan.fallback['reason_code'], 'CAPABILITY_NOT_COVERED')

    def test_health_closed_object_and_omitted_arguments(self):
        self.assertIsNone(parse_health_request({}))
        self.assertIsNone(parse_health_request(None, arguments_provided=False))
        for value in (None, {'unexpected': 'read_only_schema_probe'}, {'x': None}, [], '', 0, False):
            with self.subTest(value=value), self.assertRaises(NexusMcpError) as caught:
                parse_health_request(value)
            self.assertEqual(caught.exception.code, 'INVALID_REQUEST')

    def test_health_sdk_callback_distinguishes_omission_and_explicit_null(self):
        runtime = Mock()
        runtime.health.side_effect = safe_health
        callback = create_server(runtime)._request_handlers['tools/call'].handler
        for raw, expected_error in (
            ({'name': 'nexus.health'}, False),
            ({'name': 'nexus.health', 'arguments': {}}, False),
            ({'name': 'nexus.health', 'arguments': None}, True),
            ({'name': 'nexus.health', 'arguments': {'unexpected': 1}}, True),
        ):
            with self.subTest(raw=raw):
                runtime.health.reset_mock()
                result = asyncio.run(callback(None, types.CallToolRequestParams.model_validate(raw)))
                self.assertEqual(result.is_error, expected_error)
                if expected_error:
                    self.assertEqual(json.loads(result.content[0].text)['error']['code'], 'INVALID_REQUEST')
                    runtime.health.assert_not_called()
                else:
                    runtime.health.assert_called_once_with()

    def test_research_optout_task_and_constraints_before_library_reads(self):
        for optout in (
            'Do not perform external reference research for this bounded task.',
            'Skip reference research.', 'Do not conduct public reference research.',
            'Omit external reference research.', 'Never carry out external research.',
            'Without public reference research.', '不要搜索 GitHub',
        ):
            with self.subTest(optout=optout):
                self.assertEqual(reference_research_plan('Build a new website. '+optout).status, 'skipped')
                reader = Mock(side_effect=AssertionError('opt-out must not read Library'))
                plan = self.plan('Build a new frontend website.', [],
                    user_requirements=iter([optout]), reference_library_reader=reader)
                self.assertEqual(plan.reference_research.status, 'skipped')
                self.assertEqual(plan.reference_research.reusable_references['library_status'], 'not_read')
                reader.assert_not_called()

    def test_positive_research_constraints_do_not_create_or_suppress_trigger(self):
        self.assertEqual(reference_research_plan('Build a new website.', constraints=['Compare official documentation and mature alternatives.']).status, 'required')
        self.assertEqual(reference_research_plan('Build a new website from a complete specification.').status, 'reduced')
        self.assertEqual(reference_research_plan('Fix a tiny typo.', constraints=['Research is available.']).status, 'skipped')
        self.assertEqual(reference_research_plan('Build a new website. Do not skip reference research.').status, 'required')
        self.assertEqual(reference_research_plan('Build a new website.', constraints=['Do not omit external research.']).status, 'required')

    def test_postposed_negative_operator_preserves_requested_core_workflow(self):
        prefix = 'Implement a frontend HTML opacity animation with GSAP core using one tween and cleanup. '
        for exclusion in (
            'ScrollTrigger is not needed.', 'ScrollTrigger is not required.',
            'GSAP ScrollTrigger is not requested.', 'ScrollTrigger is unnecessary.',
            "ScrollTrigger isn't needed.", 'ScrollTrigger is unneeded.',
        ):
            with self.subTest(exclusion=exclusion):
                self.assertEqual([x.name for x in self.plan(prefix + exclusion).selected], ['gsap-core'])

    def test_negative_operator_clause_does_not_veto_a_separate_affirmative_task(self):
        for task in (
            'ScrollTrigger is not needed for the badge. Implement another HTML GSAP ScrollTrigger animation with pin and scrub.',
            'Implement an HTML GSAP animation. ScrollTrigger is not only supported but required with pin and scrub.',
        ):
            with self.subTest(task=task):
                self.assertEqual([x.name for x in self.plan(task).selected], ['gsap-scrolltrigger'])

    def test_quoted_operator_reference_is_not_a_specialist_request(self):
        task = 'Implement an HTML opacity animation with a GSAP core tween. The note "Use ScrollTrigger pinning" is quoted background.'
        self.assertEqual([x.name for x in self.plan(task).selected], ['gsap-core'])

    def test_non_animation_with_postposed_operator_exclusion_does_not_select_gsap(self):
        for task in (
            'Fix frontend CSS margin only. ScrollTrigger is not needed.',
            "Review a Python parser containing 'ScrollTrigger GSAP animation'.",
        ):
            with self.subTest(task=task):
                self.assertEqual(self.plan(task).selected, [])


if __name__ == '__main__':
    unittest.main()
