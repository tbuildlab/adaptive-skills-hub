"""One read-only Git/Host workflow. No tool invocation or production authority."""
from __future__ import annotations

from dataclasses import asdict
from pathlib import Path
import json
import re
import time
from uuid import uuid4

from . import core, core_capabilities as files
from .common import utc_now
from .core_host import exclusive_run
from .discovery import discover_skills
from .semantic_domains import make_trusted_applicability
from .v2 import ProjectContext, plan_task, load_plan_skills, validate_plan

SKILL = Path(__file__).resolve().parents[1] / 'plugins/nexus-desktop/skills/nexus/SKILL.md'
MARKER = '## Core Host Git Maintenance v1\n'
SCHEMA = 'nexus.core.host-git-task.v1'
STAGES = ('inspect', 'check', 'report', 'verify')
FINAL = {'completed', 'completed_with_findings', 'blocked', 'failed', 'ambiguous',
         'approval_required', 'cancelled', 'budget_exhausted'}
KINDS = {'trailing_whitespace', 'space_before_tab', 'blank_line_at_eof'}
HASH = re.compile(r'[0-9a-f]{64}')


def require(ok, reason):
    if not ok:
        raise core.CoreError(reason)


def _inputs(state):
    return {name: files.sha(files.read_bytes(Path(state['repo']), name)) for name in state['files']}


def _load(directory):
    directory = Path(directory).resolve(strict=True)
    envelope = files.load_json(core._bound(directory, 'task.json'))
    state = envelope['payload']
    require(state['schema'] == SCHEMA and state['directory'] == str(directory)
            and files.sha(core._bytes(state)) == envelope['sha256'], 'Host checkpoint integrity mismatch')
    budget = core.CoreBudget(**state['budget']); budget.validate()
    require(budget.max_commands <= 8 and budget.max_replans == 0
            and type(state['commands_used']) is int and 0 <= state['commands_used'] <= budget.max_commands
            and type(state['observations']) is list and len(state['observations']) <= 4
            and 1 <= len(state['files']) <= 32 and len(set(state['files'])) == len(state['files']),
            'Invalid Host checkpoint bounds')
    return state


def _report(state):
    inspected, checked = state['observations'][:2]
    data = {'schema': 'nexus.core.host-git-report.v1', 'task_id': state['task_id'],
            'repo': state['repo'], 'files': state['files'], 'repository': inspected,
            'checks': checked, 'selected_skill': state['selected_skill'],
            'scope': 'Read-only tracked Git metadata and explicit non-secret file checks',
            'findings_count': sum(len(v['findings']) for v in checked.values())}
    markdown = ('# Git maintenance inspection\n\n'
                f"HEAD: {inspected['head']}\n\n"
                f"Changed tracked entries: {inspected['changed_tracked']}\n\n"
                f"Allowed files checked: {len(state['files'])}\n\n"
                f"Whitespace findings: {data['findings_count']}\n\n"
                'Inspection only; no source edits or Git mutations. Detailed evidence: report.json.\n')
    return {'report.json': core._bytes(data).decode('utf-8') + '\n', 'report.md': markdown}


def _artifacts(state):
    expected = _report(state)
    result = core._artifacts({'project': state['directory'], 'budget': state['budget']},
                             {'data': {}, 'artifacts': list(expected)})
    for name, body in expected.items():
        require(files.read_bytes(Path(state['directory']), name) == body.encode('utf-8'),
                'Report content does not match observed facts')
    return result


def _end(state, status, reason=None):
    state.update(status=status, blocker=reason, inflight=None)
    verified = status in {'completed', 'completed_with_findings'}
    receipt = {'schema': 'nexus.core.host-git-receipt.v1', 'task_id': state['task_id'],
               'task': state['task'], 'artifact_root': state['directory'], 'files': state['files'],
               'repository': state['observations'][0] if state['observations'] else None,
               'checks': state['observations'][1] if len(state['observations']) >= 2 else None,
               'status': status, 'blocker': reason, 'selected_skill': state['selected_skill'],
               'states': ['selected', 'loaded_verified'] if state['selected_skill'] else [],
               'completed_steps': list(STAGES[:len(state['observations'])]),
               'commands_used': state['commands_used'], 'budget': state['budget'],
               'budget_unit': 'Host action batches, not provider spend or Git process count',
               'artifacts': state['artifacts'], 'verification': 'passed' if verified else 'not_verified',
               'scope': 'trusted local Host read-only Git inspection', 'real_admission': 'NO'}
    if state['commands_used']: receipt['states'].append('host_action_requested')
    if state['observations']: receipt['states'].append('host_result_observed')
    if verified: receipt['states'] += ['report_reopened', 'fresh_repository_checked', 'verified_completion']
    state['receipt'] = receipt
    core._atomic(core._bound(Path(state['directory']), 'receipt.json'), core._bytes(receipt) + b'\n')
    core._save(Path(state['directory']), state)


def prepare(task, repo, names, directory):
    repo, directory = Path(repo).absolute(), Path(directory).absolute()
    for part in (repo, *repo.parents):
        require(not part.is_symlink() and not (part.exists() and getattr(part.lstat(), 'st_file_attributes', 0) & 0x400),
                'Linked repository root refused')
    repo = repo.resolve(strict=True)
    require(repo.is_dir() and not directory.exists() and not directory.resolve().is_relative_to(repo),
            'Fresh task directory must be outside the inspected repository')
    core._bound(directory.parent.resolve(strict=True), directory.name)
    require(type(task) is str and 0 < len(task) <= 4096 and type(names) is list
            and 1 <= len(names) <= 32 and len(set(names)) == len(names), 'Invalid bounded task scope')
    negative = r"\b(?:do not|don't|never|no)\b[^.;\n]*"
    require(not any(re.search(r'\b(?:read|inspect|check|include)\b', clause)
                    for clause in re.findall(negative, task.lower())),
            'Conflicting read restriction; narrow the explicit file scope first')
    positive = re.sub(negative, '', task.lower()).strip()
    require(re.search(r'\b(?:inspect|check|review|audit|research|analyze)\b', positive)
            and re.search(r'\b(?:git|repository|repo)\b', positive)
            and not re.search(r'\b(?:push|reset|deploy|delete|stage|commit|rebase|checkout|clean|fix|edit|fetch|pull|clone|merge|switch|revert|stash|install|history)\b|\bgit\s+add\b|\brun\b.*\btests?\b', positive),
            'Only read-only Git inspection is supported; Host approval cannot expand this profile')
    budget = core.CoreBudget(max_commands=8, total_seconds=600, max_attempts=1, max_replans=0)
    state = {'schema': SCHEMA, 'task_id': uuid4().hex, 'task': task, 'repo': str(repo),
             'directory': str(directory.resolve()), 'files': sorted(names), 'budget': asdict(budget),
             'created_at_utc': utc_now(), 'updated_at_utc': utc_now(), 'commands_used': 0,
             'observations': [], 'inflight': None, 'status': 'prepared', 'artifacts': [],
             'selected_skill': None, 'receipt': None, 'blocker': None}
    state['input_hashes'] = _inputs(state)
    state['planner_task'] = positive  # Original task retained; fixed read-only prohibitions remain enforced.
    directory.mkdir()
    try:
        source = SKILL.read_text(encoding='utf-8')
        require(MARKER in source, 'No eligible repository-owned Git Skill mapping')
        section = source.split(MARKER, 1)[1].split('\n## ', 1)[0]
        (directory / 'skill').mkdir()
        narrow = ('---\nname: nexus-git-maintenance-readonly\n'
                  'description: Read-only Git repository software research inspection and whitespace checks\n'
                  'capabilities: ["research", "testing", "general"]\n---\n\n' + MARKER + section)
        (directory / 'skill/SKILL.md').write_text(narrow, encoding='utf-8', newline='\n')
        records = discover_skills([directory / 'skill'], directory)
        for record in records:
            record['_nexus_trusted_applicability'] = make_trusted_applicability(
                supported_domains=['software_research', 'general_research', 'code_review', 'software_testing'],
                supported_task_kinds=['research', 'analysis', 'review', 'software_test'],
                provenance='repository_owned_readonly_git_profile_v1')
        plan = plan_task(positive, {'skills': records, 'agents': []}, repo,
                         context_reader=lambda root, text, **kw: ProjectContext(str(root)))
        loaded = load_plan_skills(plan); validation = validate_plan(plan, loaded)
        require(validation['status'] == 'passed' and len(plan.selected) == len(loaded) == 1,
                'No compatible Git Skill selection; do not force a candidate')
        state['plan'] = plan.to_dict()
        state['selected_skill'] = {k: loaded[0][k] for k in ('name', 'path', 'sha256')}
        state['source_sha256'] = core._digest(SKILL)
        state['selected_skill']['origin_sha256'] = state['source_sha256']
    except (OSError, ValueError, KeyError):
        _end(state, 'blocked', 'No eligible verified repository-owned Git Skill')
        return state
    core._save(directory, state)
    return state


def _current(state):
    require(time.time() >= core._epoch(state['updated_at_utc']), 'Local clock reversal')
    require(_inputs(state) == state['input_hashes'] and core._digest(SKILL) == state['source_sha256']
            and core._digest(Path(state['selected_skill']['path'])) == state['selected_skill']['sha256'],
            'Declared input or selected Skill changed')


def _commands(state, stage):
    prefix = ['git', '--no-optional-locks', '--no-pager', '--literal-pathspecs',
              '-c', 'color.ui=false', '-c', 'core.quotePath=false',
              '-c', 'core.fsmonitor=false', '-c', 'core.untrackedCache=false',
              '-C', state['repo']]
    inspect = [('root', ['rev-parse', '--show-toplevel']), ('head', ['rev-parse', '--verify', 'HEAD']),
               ('status', ['status', '--porcelain=v1', '-z', '--untracked-files=no']),
               ('tracked', ['ls-files', '-z', '--', *state['files']])]
    checks = [('unstaged', ['diff', '--no-ext-diff', '--no-textconv', '--check', '--', *state['files']]),
              ('staged', ['diff', '--no-ext-diff', '--no-textconv', '--cached', '--check', '--', *state['files']])]
    return [{'key': key, 'argv': prefix + argv} for key, argv in
            (inspect if stage == 'inspect' else checks if stage == 'check' else inspect + checks)]


def next_action(directory):
    _load(directory)  # Refuse arbitrary directories before creating a run lock.
    with exclusive_run(Path(directory)):
        state = _load(directory)
        if state['status'] in {'completed', 'completed_with_findings'}:
            try:
                require(_artifacts(state) == state['artifacts'], 'Completed report artifact changed')
            except (OSError, ValueError, KeyError):
                _end(state, 'failed', 'Completed report artifact changed; no replay')
        if state['status'] in FINAL or state['inflight']:
            return {'status': state['status'], 'action': None, 'inflight': state['inflight'],
                    'receipt': state['receipt'], 'commands_used': state['commands_used']}
        try:
            _current(state)
            if Path(directory, 'cancel.request').exists():
                _end(state, 'cancelled', 'Host task cancelled'); return {'status': state['status'], 'action': None}
            if state['commands_used'] >= state['budget']['max_commands'] or time.time() >= \
                    core._epoch(state['created_at_utc']) + state['budget']['total_seconds']:
                _end(state, 'budget_exhausted', 'Remaining Host budget exhausted')
                return {'status': state['status'], 'action': None, 'receipt': state['receipt']}
            stage = STAGES[len(state['observations'])]
            action = {'task_id': state['task_id'], 'action_id': uuid4().hex, 'stage': stage,
                      'timeout_seconds': min(state['budget']['step_seconds'],
                        core._epoch(state['created_at_utc']) + state['budget']['total_seconds'] - time.time()),
                      'max_observation_bytes': state['budget']['max_output_bytes']}
            if stage == 'report': action.update(directory=state['directory'], files=_report(state))
            else: action['commands'] = _commands(state, stage)
            state['commands_used'] += 1
            pending = {k: action[k] for k in ('task_id', 'action_id', 'stage')}
            pending['deadline'] = time.time() + action['timeout_seconds']
            state.update(inflight=pending, status='waiting_host')
            core._save(Path(directory), state)
            return {'status': state['status'], 'action': action}
        except (OSError, ValueError, KeyError):
            _end(state, 'blocked', 'Scope, Skill, cancellation or remaining budget gate failed')
            return {'status': state['status'], 'action': None, 'receipt': state['receipt']}


def _inspection(state, data):
    require(type(data) is dict and set(data) == {'root', 'head', 'status_sha256', 'changed_tracked', 'tracked_files'},
            'Malformed repository observation')
    require(data['root'] == state['repo'] and type(data['head']) is str
            and re.fullmatch(r'[0-9a-f]{40}|[0-9a-f]{64}', data['head'])
            and type(data['status_sha256']) is str and HASH.fullmatch(data['status_sha256'])
            and type(data['changed_tracked']) is int and 0 <= data['changed_tracked'] <= 4096
            and data['tracked_files'] == state['files'], 'Wrong repository or untracked declared file')


def _checks(state, data):
    require(type(data) is dict and set(data) == {'unstaged', 'staged'}, 'Malformed check observation')
    for check in data.values():
        require(type(check) is dict and set(check) == {'exit_code', 'findings'}
                and type(check['exit_code']) is int and check['exit_code'] in (0, 2)
                and type(check['findings']) is list and len(check['findings']) <= 512
                and bool(check['findings']) == (check['exit_code'] == 2), 'Check failure is not a clean finding')
        for item in check['findings']:
            require(type(item) is dict and set(item) == {'path', 'line', 'kind'}
                    and item['path'] in state['files'] and type(item['line']) is int and item['line'] > 0
                    and item['kind'] in KINDS, 'Out-of-scope or raw check evidence')


def observe(directory, observation):
    _load(directory)
    with exclusive_run(Path(directory)):
        state = _load(directory)
        try:
            require(type(observation) is dict and set(observation) ==
                    {'task_id', 'action_id', 'stage', 'host_status', 'data'}
                    and len(core._bytes(observation)) <= state['budget']['max_output_bytes'], 'Malformed Host observation')
            pending = state['inflight']
            require(state['status'] == 'waiting_host' and pending and all(observation[k] == pending[k]
                    for k in ('task_id', 'action_id', 'stage')), 'Wrong, duplicate or stale Host observation')
            require(observation['host_status'] in {'ok', 'failed', 'unknown', 'approval_required', 'denied', 'cancelled'},
                    'Unknown Host outcome')
            if observation['host_status'] != 'ok':
                status = {'unknown': 'ambiguous', 'approval_required': 'approval_required',
                          'cancelled': 'cancelled'}.get(observation['host_status'], 'failed')
                _end(state, status, 'Host action did not succeed'); return state
            _current(state)
            require(time.time() < core._epoch(state['created_at_utc']) + state['budget']['total_seconds'],
                    'Expired Host observation')
            require(time.time() < pending['deadline'], 'Host action deadline expired; no replay')
            if Path(directory, 'cancel.request').exists():
                _end(state, 'cancelled', 'Host task cancelled'); return state
            stage, data = pending['stage'], observation['data']
            if stage == 'inspect': _inspection(state, data)
            elif stage == 'check': _checks(state, data)
            elif stage == 'report':
                require(data == {'files': ['report.json', 'report.md']}, 'Wrong report observation')
                state['artifacts'] = _artifacts(state)
            else:
                require(type(data) is dict and set(data) == {'repository', 'checks'}, 'Malformed fresh verification')
                _inspection(state, data['repository']); _checks(state, data['checks'])
                require(data['repository'] == state['observations'][0] and data['checks'] == state['observations'][1],
                        'Fresh repository state differs from report')
                require(_artifacts(state) == state['artifacts'], 'Report changed after checkpoint')
            state['observations'].append(data); state.update(inflight=None, status='prepared')
            if stage == 'verify':
                count = _report(state)['report.json']
                _end(state, 'completed_with_findings' if json.loads(count)['findings_count'] else 'completed')
            else: core._save(Path(directory), state)
        except (OSError, ValueError, KeyError, TypeError):
            if state['status'] not in FINAL: _end(state, 'failed', 'Host observation or independent verification rejected')
        return state


def status(directory):
    _load(directory)
    with exclusive_run(Path(directory)):
        state = _load(directory)
        return {k: state[k] for k in ('task_id', 'status', 'blocker', 'selected_skill', 'commands_used',
                                      'budget', 'inflight', 'artifacts', 'receipt')}
