"""Local Host-observation fixtures; these are not the real repository E2E."""
from __future__ import annotations
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch

from ash import core, core_host_loop as host
from ash.core_capabilities import ScopeError, write

ROOT = Path(__file__).resolve().parents[1]
TASK = 'Inspect this local Git repository changes and whitespace checks, then return a maintenance report.'


class HostLoopTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='nexus-host-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.repo = self.root / 'repo'; self.repo.mkdir()
        (self.repo / 'README.md').write_text('Declared non-secret fixture\n', encoding='utf-8')
        self.directory = self.root / 'task'

    def prepare(self):
        state = host.prepare(TASK, self.repo, ['README.md'], self.directory)
        self.assertEqual(state['status'], 'prepared', state['blocker'])
        return state

    def inspection(self):
        return dict(root=str(self.repo.resolve()), head='1' * 40,
                    status_sha256=hashlib.sha256(b' M README.md\0').hexdigest(),
                    changed_tracked=1, tracked_files=['README.md'])

    def checks(self, finding=False):
        return {'unstaged': {'exit_code': 2 if finding else 0,
                'findings': [{'path': 'README.md', 'line': 1, 'kind': 'trailing_whitespace'}] if finding else []},
                'staged': {'exit_code': 0, 'findings': []}}

    def action(self):
        result = host.next_action(self.directory)
        self.assertIsNotNone(result['action'], result)
        return result['action']

    def observe(self, action, data, outcome='ok'):
        return host.observe(self.directory, dict(
            **{k: action[k] for k in ('task_id', 'action_id', 'stage')}, host_status=outcome, data=data))

    def through_report(self, finding=False):
        self.prepare()
        self.observe(self.action(), self.inspection())
        self.observe(self.action(), self.checks(finding))
        report = self.action(); self.assertEqual(report['stage'], 'report')
        for name, body in report['files'].items():
            write(self.directory, name, body.encode('utf-8'))
        self.observe(report, {'files': ['report.json', 'report.md']})

    def test_planner_selects_real_loaded_profile_and_clean_report_is_reopened(self):
        with patch('subprocess.run', side_effect=AssertionError('adapter must not execute tools')):
            self.through_report()
            result = self.observe(self.action(), {'repository': self.inspection(), 'checks': self.checks()})
        self.assertEqual(result['status'], 'completed')
        self.assertEqual(result['commands_used'], 4)
        self.assertEqual(result['receipt']['verification'], 'passed')
        self.assertEqual(result['receipt']['repository'], self.inspection())
        self.assertEqual(result['receipt']['checks'], self.checks())
        self.assertEqual(result['receipt']['artifact_root'], str(self.directory.resolve()))
        self.assertIn('verified_completion', result['receipt']['states'])
        selected = result['selected_skill']
        self.assertEqual(selected['name'], 'nexus-git-maintenance-readonly')
        self.assertEqual(core._digest(Path(selected['path'])), selected['sha256'])
        self.assertEqual(json.loads((self.directory / 'report.json').read_bytes())['repository'], self.inspection())
        self.assertEqual(json.loads((self.directory / 'receipt.json').read_bytes()), result['receipt'])

    def test_actual_whitespace_finding_fixture_remains_completed_with_findings(self):
        (self.repo / 'README.md').write_text('Trailing space \n')
        self.through_report(finding=True)
        result = self.observe(self.action(), {'repository': self.inspection(), 'checks': self.checks(True)})
        self.assertEqual(result['status'], 'completed_with_findings')
        report = json.loads((self.directory / 'report.json').read_bytes())
        self.assertEqual(report['checks']['unstaged']['exit_code'], 2)
        self.assertEqual(report['findings_count'], 1)
        self.assertIn('Whitespace findings: 1', (self.directory / 'report.md').read_text())

    def test_resume_preserves_verified_report_and_does_not_redispatch_inflight(self):
        self.prepare(); first = self.action()
        self.assertIsNone(host.next_action(self.directory)['action'])
        self.assertEqual(host.status(self.directory)['commands_used'], 1)
        self.observe(first, self.inspection())
        self.observe(self.action(), self.checks())
        action = self.action()
        for name, body in action['files'].items(): write(self.directory, name, body.encode())
        # Interrupted writer: reconcile already existing exact files; no overwrite.
        stamp = (self.directory / 'report.json').stat().st_mtime_ns
        self.assertIsNone(host.next_action(self.directory)['action'])
        self.observe(action, {'files': ['report.json', 'report.md']})
        state = self.observe(self.action(), {'repository': self.inspection(), 'checks': self.checks()})
        self.assertEqual((self.directory / 'report.json').stat().st_mtime_ns, stamp)
        self.assertEqual(state['commands_used'], 4)
        self.assertIsNone(host.next_action(self.directory)['action'])
        self.assertEqual(host.status(self.directory)['commands_used'], 4)
        (self.directory / 'report.json').write_text('{}')
        self.assertEqual(host.next_action(self.directory)['status'], 'failed')
        self.assertEqual(host.status(self.directory)['commands_used'], 4)

    def test_missing_or_changed_skill_blocks_without_forcing_selection(self):
        unrelated = self.root / 'SKILL.md'; unrelated.write_text('Unrelated Skill')
        with patch.object(host, 'SKILL', unrelated):
            state = host.prepare(TASK, self.repo, ['README.md'], self.directory)
        self.assertEqual(state['status'], 'blocked')
        self.assertIsNone(host.next_action(self.directory)['action'])
        self.assertEqual(state['commands_used'], 0)
        second = self.root / 'second'
        state = host.prepare(TASK, self.repo, ['README.md'], second)
        with patch.object(host, 'SKILL', unrelated):
            self.assertEqual(host.next_action(second)['status'], 'blocked')

    def test_scope_paths_and_dangerous_requests_are_refused_before_writes(self):
        with self.assertRaises((core.CoreError, ScopeError)):
            host.prepare(TASK, self.repo, ['../README.md'], self.directory)
        self.assertFalse(self.directory.exists())
        with self.assertRaises(core.CoreError):
            host.prepare(TASK, self.repo, ['README.md'], self.repo / 'task')
        for command in ('reset', 'push', 'commit', 'stage', 'deploy', 'fetch', 'clone', 'run project tests'):
            with self.assertRaises(core.CoreError):
                host.prepare('Inspect this Git repo then ' + command, self.repo, ['README.md'], self.directory)
        with self.assertRaises((OSError, ValueError, KeyError)):
            host.next_action(self.repo)
        self.assertFalse((self.repo / 'run.lock').exists())

    def test_fixed_git_arrays_disable_optional_locks_hooks_and_nonliteral_paths(self):
        self.prepare(); action = self.action()
        self.assertEqual({x['key'] for x in action['commands']}, {'root', 'head', 'status', 'tracked'})
        for item in action['commands']:
            self.assertEqual(item['argv'][0], 'git')
            for flag in ('--no-optional-locks', '--no-pager', '--literal-pathspecs', 'core.fsmonitor=false'):
                self.assertIn(flag, item['argv'])
        self.observe(action, self.inspection())
        for item in self.action()['commands']:
            self.assertIn('--no-ext-diff', item['argv']); self.assertIn('--no-textconv', item['argv'])

    def test_tool_failure_unknown_and_host_approval_are_truthful_terminal_outcomes(self):
        for outcome, expected in [('failed', 'failed'), ('unknown', 'ambiguous'),
                                  ('approval_required', 'approval_required'), ('denied', 'failed')]:
            directory = self.root / outcome
            host.prepare(TASK, self.repo, ['README.md'], directory)
            action = host.next_action(directory)['action']
            state = host.observe(directory, dict(**{k: action[k] for k in ('task_id', 'action_id', 'stage')},
                                host_status=outcome, data={}))
            self.assertEqual(state['status'], expected)
            self.assertEqual(state['receipt']['verification'], 'not_verified')
            self.assertIsNone(host.next_action(directory)['action'])
            self.assertEqual(state['commands_used'], 1)

    def test_malformed_stale_oversized_and_raw_observations_never_complete(self):
        for case in ('wrong_id', 'extra_command', 'oversized', 'raw_findings'):
            directory = self.root / case
            host.prepare(TASK, self.repo, ['README.md'], directory)
            action = host.next_action(directory)['action']
            obs = dict(**{k: action[k] for k in ('task_id', 'action_id', 'stage')}, host_status='ok', data=self.inspection())
            if case == 'wrong_id': obs['action_id'] = 'stale'
            elif case == 'extra_command': obs['argv'] = ['git', 'reset']
            elif case == 'oversized': obs['data']['raw'] = 'x' * 65536
            else: obs['data']['source_line'] = 'forbidden raw source'
            result = host.observe(directory, obs)
            self.assertEqual(result['status'], 'failed')
            self.assertNotIn('forbidden raw source', (directory / 'task.json').read_text())

    def test_corrupt_checkpoint_budget_deadline_and_cancellation_are_not_resets(self):
        self.prepare(); state = host._load(self.directory)
        state['commands_used'] = 8; core._save(self.directory, state)
        self.assertIsNone(host.next_action(self.directory)['action'])
        self.assertEqual(host.status(self.directory)['commands_used'], 8)
        for name, mode in [('deadline', 'expired'), ('cancel', 'cancelled')]:
            directory = self.root / name
            host.prepare(TASK, self.repo, ['README.md'], directory)
            if mode == 'cancelled': (directory / 'cancel.request').write_bytes(b'cancel\n')
            with patch.object(host.time, 'time', return_value=time.time() + (601 if mode == 'expired' else 0)):
                self.assertIsNone(host.next_action(directory)['action'])
            self.assertEqual(host.status(directory)['commands_used'], 0)
        (self.directory / 'task.json').write_text('{"payload":{}}')
        with self.assertRaises((KeyError, ValueError)): host.status(self.directory)
        directory = self.root / 'step-timeout'
        host.prepare(TASK, self.repo, ['README.md'], directory)
        action = host.next_action(directory)['action']
        with patch.object(host.time, 'time', return_value=time.time() + 21):
            state = host.observe(directory, dict(**{k: action[k] for k in ('task_id', 'action_id', 'stage')},
                                                 host_status='ok', data=self.inspection()))
        self.assertEqual(state['status'], 'failed')
        self.assertEqual(state['commands_used'], 1)

    def test_reopened_report_tampering_and_fresh_repository_drift_refuse_completion(self):
        self.through_report(); action = self.action()
        (self.directory / 'report.md').write_text('False clean report')
        state = self.observe(action, {'repository': self.inspection(), 'checks': self.checks()})
        self.assertEqual(state['status'], 'failed')
        self.directory = self.root / 'second'; self.through_report()
        fresh = self.inspection(); fresh['head'] = '2' * 40
        state = self.observe(self.action(), {'repository': fresh, 'checks': self.checks()})
        self.assertEqual(state['status'], 'failed')
        self.directory = self.root / 'third'; self.prepare()
        (self.repo / 'README.md').write_text('Changed declared input')
        self.assertEqual(host.next_action(self.directory)['status'], 'blocked')

    def test_check_exit_errors_and_untracked_declared_files_are_not_false_passes(self):
        self.prepare(); bad = self.inspection(); bad['tracked_files'] = []
        self.assertEqual(self.observe(self.action(), bad)['status'], 'failed')
        self.directory = self.root / 'second'; self.prepare()
        self.observe(self.action(), self.inspection())
        data = self.checks(); data['unstaged']['exit_code'] = 128
        self.assertEqual(self.observe(self.action(), data)['status'], 'failed')

    def test_cli_bookkeeping_is_compatible_and_requires_no_local_approval_hash(self):
        task = TASK + ' Do not edit source, stage, commit, push, clean or reset anything.'
        command = [sys.executable, '-B', str(ROOT / 'scripts/nexus.py'), 'core-host-plan', task,
                   '--project', str(self.repo), '--file', 'README.md', '--task-dir', str(self.directory)]
        completed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['status'], 'prepared')
        state = host._load(self.directory)
        self.assertEqual(state['task'], task)
        self.assertNotIn('commit', state['planner_task'])
        command = [sys.executable, '-B', str(ROOT / 'scripts/nexus.py'), 'core-host-next', str(self.directory)]
        completed = subprocess.run(command, capture_output=True, text=True, encoding='utf-8')
        action = json.loads(completed.stdout)['action']
        obs = dict(**{k: action[k] for k in ('task_id', 'action_id', 'stage')}, host_status='ok', data=self.inspection())
        completed = subprocess.run([*command[:3], 'core-host-observe', str(self.directory)],
                                   input=json.dumps(obs), capture_output=True, text=True, encoding='utf-8')
        self.assertEqual(completed.returncode, 0, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['commands_used'], 1)


if __name__ == '__main__':
    unittest.main()
