"""Finite PUBLIC snapshot/environment/I/O/lifecycle probe; never a real task."""
import json
import os
import sys
import time

case = sys.argv[1]
if case == 'child':
    # On Windows spawnv(P_NOWAIT) returns a HANDLE, not a PID. The child
    # reports its own PID through the existing bounded stdout pipe instead.
    if len(sys.argv) != 3:
        raise SystemExit(2)
    print(json.dumps({'public_pids': [int(sys.argv[2]), os.getpid()]}), flush=True)
    time.sleep(60)
    raise SystemExit(0)
if case in ('deterministic_cancel', 'deterministic_timeout', 'deterministic_controller_failure'):
    process_handle = os.spawnv(os.P_NOWAIT, sys.executable,
                              [sys.executable, '-I', '-S', '-B', __file__, 'child', str(os.getpid())])
    os.waitpid(process_handle, 0)
    raise SystemExit(0)
if case != 'deterministic_io':
    raise SystemExit(2)
runtime = os.path.dirname(sys.executable)
checks = {'search_snapshot_only': all(os.path.commonpath((runtime, p)) == runtime for p in sys.path),
          'isolated': bool(sys.flags.isolated), 'no_site': bool(sys.flags.no_site),
          'dont_write_bytecode': bool(sys.flags.dont_write_bytecode),
          'path_fixed': os.environ.get('PATH', '').lower() == r'c:\windows\system32',
          'ggml_absent': 'GGML_BACKEND_PATH' not in os.environ,
          'provider_proxy_env_absent': not any(k in os.environ for k in ('OPENAI_API_KEY', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY'))}
with open('../input/task.txt', 'rb') as source:
    checks['exact_input_read'] = len(source.read(16385)) <= 16384
for name, path in (('unlisted_denied', '../input/unlisted.txt'), ('outside_denied', '../outside.txt')):
    try:
        with open(path, 'rb') as source:
            source.read(1)
        checks[name] = False
    except OSError:
        checks[name] = True
try:
    with open('../input/task.txt', 'ab') as target:
        target.write(b'PUBLIC_WRITE')
    checks['write_denied'] = False
except OSError:
    checks['write_denied'] = True
for name in ('socket', 'subprocess', 'sitecustomize', 'usercustomize'):
    try:
        __import__(name)
        checks['unlisted_module_' + name + '_denied'] = False
    except ImportError:
        checks['unlisted_module_' + name + '_denied'] = True
print(json.dumps({'status': 'PUBLIC_FIXTURE_COMPLETE', 'checks': checks}), flush=True)
