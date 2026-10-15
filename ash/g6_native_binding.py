"""Fixed G6 MXC/Windows-Job binding; public fixtures and one signed native role.

No arbitrary command API, registration or authority restoration. Native use
requires a fresh existing-issuer signature. Core Python hooks remain untouched.
"""
from __future__ import annotations

from contextlib import ExitStack, contextmanager
import hashlib
import json
import os
from pathlib import Path
import subprocess
import socket
import threading
import time
import io
import zipfile

from . import core
from .core_capabilities import safe_path
from .ecosystem_storage import open_stable_input, stable_read_bytes
from . import ecosystem_storage as storage
from .g6_local_model_intake import load_policy

ROOT = Path(__file__).resolve().parents[1]
_LOADED_BINDING_SHA=hashlib.sha256(Path(__file__).read_bytes().replace(b'\r\n',b'\n')).hexdigest()
HOST = Path('C:/Users/De Yong/AppData/Local/OpenAI/Codex/bin/9614f1d9b40d9c4f/codex.exe')
HOST_SHA = 'e98c516f1c8935789aabe9122ee7e05ec4c3efd1ba6acf179242e031c495b99e'
RUNNER=HOST.parent/'codex-command-runner.exe'
RUNNER_SHA='bdf5160289bc4d64bc2fa38c43f9679558b3a4386226adc66a0af741e41424b7'
PYTHON = Path('C:/Users/De Yong/AppData/Local/Programs/Python/Python312/python.exe')
NATIVE = frozenset({'ggml-base.dll', 'ggml-cpu-x64.dll', 'ggml.dll', 'libomp.dll',
                    'llama-common.dll', 'llama-completion-impl.dll',
                    'llama-completion.exe', 'llama.dll'})
PUBLIC_CASES = frozenset({'success', 'io', 'overflow', 'stderr_overflow', 'nonzero',
                          'partial', 'timeout', 'cancel', 'cpu', 'memory', 'processes',
                          'controller_failure', 'late_output'})
FIXTURE = ROOT / 'research/nexus-g6-native-public-fixture-v1.py'
WORK = 'output/g6-native-binding-public-v19'
NATIVE_PROMPT=b'Output only PUBLIC_G6_NATIVE_QUALIFICATION_COMPLETE.\n/no_think\n'
ENV_NAMES = ('SystemRoot', 'WINDIR', 'USERPROFILE', 'SystemDrive', 'COMSPEC', 'PATHEXT',
             'LOCALAPPDATA', 'APPDATA', 'PROGRAMDATA', 'ALLUSERSPROFILE', 'PUBLIC',
             'ProgramFiles', 'ProgramFiles(x86)', 'ProgramW6432', 'CommonProgramFiles',
             'HOMEDRIVE', 'HOMEPATH', 'USERNAME', 'USERDOMAIN')
TELEMETRY = ('analytics.enabled=false', 'feedback.enabled=false', 'otel.exporter="none"',
             'otel.trace_exporter="none"', 'otel.metrics_exporter="none"',
             'otel.log_user_prompt=false', 'features.hooks=false', 'notify=[]')
OUTPUT_LIMIT = 65536


class BindingHold(ValueError):
    """Closed code only; do not disclose raw Host output or local input."""


def require(ok, code):
    if not ok:
        raise BindingHold(code)


def normalized_sha(path):
    raw = stable_read_bytes(Path(path), maximum_bytes=1048576)
    return hashlib.sha256(raw.replace(b'\r\n', b'\n')).hexdigest()


def _source_gate():
    require(normalized_sha(Path(__file__))==_LOADED_BINDING_SHA,'LOADED_BINDING_REVISION_CHANGED')


def native_plan():
    """Pinned inert plan only. Creating this data does not extract or dispatch."""
    policy = load_policy()
    members = [m for m in policy['runtime']['members'] if m['path'] in NATIVE]
    require(len(members) == 8, 'NATIVE_SET')
    directory=ROOT/'output/g6-native-private-once-v1'
    binary=directory/'bin'
    prompt=directory/'input/task.txt'
    model=ROOT/'output/g6-final/intake-successor-v1/model.gguf.blob'
    return {'schema': 'nexus.g6.fixed-native-plan.v1', 'mode': 'FRESH_OWNER_SIGNATURE_REQUIRED',
            'runtime_sha256': policy['runtime']['sha256'], 'model': policy['model'],
            'members': members, 'cwd': str(binary),
            'executable': str(binary/'llama-completion.exe'), 'backend': str(binary/'ggml-cpu-x64.dll'),
            'search': 'bin=CWD; PATH=System32; root-deny; System32 runtime read-only',
            'environment_names': list(ENV_NAMES), 'ggml_backend_path': 'ABSENT',
            'host_material':{str(HOST):HOST_SHA,str(RUNNER):RUNNER_SHA},
            'input':str(prompt),'model_blob':str(model),'result_directory':str(directory/'result'),
            'input_sha256':hashlib.sha256(NATIVE_PROMPT).hexdigest(),
            'filesystem':{':root':'deny','C:/Windows/System32':'read',binary.as_posix():'read',
                          model.as_posix():'read',prompt.as_posix():'read'},
            'candidate_arguments':['-m',str(model),'-f',str(prompt),'-n','128','-c','1024',
                                   '-t','2','-tb','2','-s','42','--temp','0','--offline',
                                   '-no-cnv','--simple-io','--no-display-prompt'],
            'output': 'local-bounded-stdout-stderr-pipes-only; no native filesystem writes',
            'network': False, 'telemetry_overrides': list(TELEMETRY),
            'limits':{'job_memory_bytes':2*1024**3,'active_processes':8,'user_cpu_seconds':120,
                      'wall_seconds':180,'retained_stdout_stderr_bytes':OUTPUT_LIMIT,
                      'prompt_bytes':16384,'cpu_threads':2,'context_tokens':1024,'output_tokens':128},
            'max_attempts': 1, 'automatic_retry': False, 'on_terminal': 'RETIRE',
            'unknown_partial_late': 'QUARANTINE', 'real_admission': 'NO'}


def _environment(result):
    # Never enumerate/copy environment contents or provider/proxy credentials.
    env = {name: os.environ[name] for name in ENV_NAMES if name in os.environ}
    env.update(PATH=r'C:\Windows\System32', COMSPEC=r'C:\Windows\System32\cmd.exe',
               PATHEXT='.COM;.EXE;.BAT;.CMD', TEMP=str(result), TMP=str(result),
               OTEL_SDK_DISABLED='true', PYTHONDONTWRITEBYTECODE='1',
               OMP_NUM_THREADS='2',OMP_THREAD_LIMIT='2',OMP_DYNAMIC='FALSE')
    return env


def _arguments(binary, data, result, case, sentinel, port, *, role='public'):
    # Public Python runtime allowance is explicit and never part of native_plan.
    require(role in ('public','native'),'CLOSED_ROLE')
    fs = {':root': 'deny', 'C:/Windows/System32': 'read', PYTHON.parent.as_posix(): 'read',
          binary.as_posix(): 'read', (data/'public.txt').as_posix(): 'read'}
    if role=='native':
        plan=native_plan(); fs=plan['filesystem']
        require(str(binary)==plan['cwd'],'NATIVE_CWD')
    literal = '{'+', '.join(json.dumps(k)+' = '+json.dumps(v) for k, v in fs.items())+'}'
    argv = [str(HOST), '-c', 'windows.sandbox="mxc"', '-c',
            'permissions.g6fixed.filesystem='+literal, '-c',
            'permissions.g6fixed.network.enabled=false']
    for item in TELEMETRY:
        argv.extend(['-c', item])
    argv.extend(['-c','shell_environment_policy.set.PATH='+json.dumps(r'C:\Windows\System32')])
    target=([str(PYTHON),'-I',str(binary/'fixture.py'),case,str(data.parent),str(sentinel),str(port)]
            if role=='public' else [plan['executable'],*plan['candidate_arguments']])
    argv += ['sandbox', '--include-managed-config', '--permission-profile', 'g6fixed',
             '--cd', str(binary), '--', *target]
    return argv, fs


def owner_intent():
    """Current exact-subject data; no approval and no packet file creation."""
    from . import g3_grant_codec as codec
    names=('ash/g6_native_binding.py','scripts/qualify_g6_native_binding.py',
           'research/nexus-g6-native-public-fixture-v1.py','tests/test_g6_native_binding.py',
           'config/nexus-g6-local-model-intake-successor-v1.json',
           'scripts/verify_g3_owner_signature.py')
    material={name:normalized_sha(ROOT/name) for name in names}
    config=native_plan()
    subject={'schema_version':codec.SUBJECT_SCHEMA,'kind':'local_adapter','provider':'repository',
             'source_ref':'repository-owned-g6-fixed-native-qualification-v1',
             'revision':'g6-fixed-native-binding-v1','capability_id':'nexus/g6-fixed-native-qualification',
             'action':'execute','content_sha256':hashlib.sha256(codec._canonical(material)).hexdigest(),
             'config_sha256':hashlib.sha256(codec._canonical(config)).hexdigest()}
    return {'schema':'nexus.g6.native-owner-qualification-decision.v1','subject':subject,
            'subject_id':codec.subject(subject).subject_id,'material':material,'config':config,
            'issuer':{'provider':'github','login':'TDY0225','user_id':223441940,
                      'principal':'github-user-223441940'},'namespace':'nexus-g3-approval-v1',
            'purpose':'APPROVE_ONE_G6_NATIVE_QUALIFICATION','max_attempts':1,
            'terminal':'RETIRE_ON_COMPLETION_FAILURE_CANCEL_OR_UNKNOWN','automatic_retry':False,
            'capability_registration':False,'real_admission':'NO'}


def _verify_native_owner():
    """Thin application of existing GitHub-bound OpenSSH issuer; no new issuer."""
    from scripts import verify_g3_owner_signature as issuer
    from . import g3_grant_codec as codec
    import tempfile
    path=ROOT/'output/g6-native-owner-signing-v1/decision.json'
    raw=stable_read_bytes(path,maximum_bytes=65536)
    body=codec.parse_input(raw)
    require(isinstance(body,dict),'OWNER_BODY')
    expected=owner_intent()
    require(set(body)==set(expected)|{'effective_at','expires_at','review_sha256'},'OWNER_SHAPE')
    require(all(body[n]==v for n,v in expected.items()),'OWNER_EXACT_SUBJECT')
    now=time.time()
    require(type(body['effective_at']) is int and type(body['expires_at']) is int
            and body['effective_at']<=now<body['expires_at']
            and 0<body['expires_at']-body['effective_at']<=86400,'OWNER_WINDOW')
    review=stable_read_bytes(ROOT/'research/nexus-g6-fixed-native-independent-review-v1.json',maximum_bytes=65536)
    require(hashlib.sha256(review.replace(b'\r\n',b'\n')).hexdigest()==body['review_sha256'],'OWNER_REVIEW')
    reviewed=codec.parse_input(review)
    require(reviewed.get('decision')=='PASS_SIGNING_READINESS'
            and reviewed.get('binding_sha256')==normalized_sha(Path(__file__)),'REVIEW_READINESS')
    public=Path('C:/Users/De Yong/NexusG3OwnerSigning/nexus_g3_ed25519.pub')
    key,fingerprint=issuer.public_key(stable_read_bytes(public,maximum_bytes=4096))
    require(fingerprint=='SHA256:5FV4/OvvMPzivK/4YIolW2kPQBGoik/llHbviTDpf98','OWNER_KEY')
    fresh=time.monotonic(); profile=issuer.github(''); keys=issuer.github('/ssh_signing_keys?per_page=100')
    require(isinstance(profile,dict) and profile.get('id')==223441940 and profile.get('login')=='TDY0225','OWNER_IDENTITY')
    require(isinstance(keys,list) and sum(isinstance(v,dict) and v.get('id')==1242636
            and ' '.join(str(v.get('key','')).split()[:2])==key for v in keys)==1,'OWNER_CURRENT_KEY')
    signature=stable_read_bytes(path.with_suffix('.json.sig'),maximum_bytes=16384)
    require(signature.startswith(b'-----BEGIN SSH SIGNATURE-----'),'OWNER_SIGNATURE_FORMAT')
    with tempfile.TemporaryDirectory(prefix='nexus-g6-public-signature-') as temporary:
        allowed=Path(temporary)/'allowed_signers'; sig=Path(temporary)/'decision.sig'
        allowed.write_text(f'{issuer.PRINCIPAL} namespaces="{issuer.NAMESPACE}" {key}\n',encoding='ascii')
        sig.write_bytes(signature)
        result=subprocess.run([r'C:\Windows\System32\OpenSSH\ssh-keygen.exe','-Y','verify',
                '-f',str(allowed),'-I',issuer.PRINCIPAL,'-n',issuer.NAMESPACE,'-s',str(sig)],
                input=raw,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL,timeout=5)
        require(result.returncode==0,'OWNER_CRYPTOGRAPHIC_SIGNATURE')
    require(time.monotonic()-fresh<=30 and body['effective_at']<=time.time()<body['expires_at'],'OWNER_FRESHNESS')
    return (hashlib.sha256(raw).hexdigest(),body['effective_at'],body['expires_at'],fresh)


def _native_resume_gate(proof,observed):
    now=time.time()
    require(0<=time.monotonic()-observed<=30 and proof[1]<=now<proof[2],
            'OWNER_EXPIRED_OR_STALE_BEFORE_RESUME')


def _prepare_native(binary,data):
    """Only after fresh signature AND exclusive reservation; never called by fixtures."""
    from . import g6_local_model_intake as intake
    plan=native_plan(); policy=intake.load_policy()
    archive=ROOT/'output/g6-final/llama-b11609-bin-win-cpu-x64.zip'
    model=Path(plan['model_blob'])
    intake.inspect_quarantined(archive,model)
    raw=archive.read_bytes()
    require(hashlib.sha256(raw).hexdigest()==policy['runtime']['sha256'],'NATIVE_ARCHIVE')
    with zipfile.ZipFile(io.BytesIO(raw)) as source:
        for member in plan['members']:
            content=source.read(member['path'])
            require(len(content)==member['bytes'] and hashlib.sha256(content).hexdigest()==member['sha256'],'NATIVE_MEMBER')
            with (binary/member['path']).open('xb') as out: out.write(content)
        with (binary/'LICENSE-LLVM-OpenMP').open('xb') as out: out.write(source.read('LICENSE-LLVM-OpenMP'))
    require({p.name for p in binary.iterdir()}==NATIVE|{'LICENSE-LLVM-OpenMP'},'NATIVE_LOADER_INVENTORY')
    with (data/'task.txt').open('xb') as out: out.write(NATIVE_PROMPT)


def public_attempt(case):
    return _fixed_attempt('public',case)


def native_attempt():
    """No plaintext/JSON opt-in: fresh independent signature is checked inside."""
    return _fixed_attempt('native','qualification')


class _Collector:
    """Two local streams, one retained-byte cap; raw bytes never returned."""
    def __init__(self, directory):
        self.directory = directory
        self.count = 0
        self.lock = threading.Lock()
        self.overflow = threading.Event()
        self.error = threading.Event()
        self.threads = []
        # Open output destinations before stable input-parent locks. No sandbox
        # write allowance or weaker input sharing is needed.
        self.outputs = {name:(directory/name).open('xb') for name in ('stdout.bin','stderr.bin')}

    def start(self, descriptor, channel):
        def drain():
            try:
                with os.fdopen(descriptor, 'rb', buffering=0) as source:
                    out=self.outputs[channel]
                    while chunk := source.read(4096):
                        with self.lock:
                            remaining = max(0, OUTPUT_LIMIT-self.count)
                            accepted = chunk[:remaining]
                            out.write(accepted)
                            out.flush()
                            self.count += len(accepted)
                            if len(accepted) != len(chunk):
                                self.overflow.set()
                        # Discard excess while the Job is being terminated. Retained
                        # bytes remain capped; no unbounded communicate()/stderr log.
            except OSError:
                self.error.set()
        thread = threading.Thread(target=drain, daemon=True)
        thread.start()
        self.threads.append(thread)

    def finish(self):
        for thread in self.threads:
            thread.join(timeout=2)
        stopped=not any(t.is_alive() for t in self.threads)
        if stopped:
            for out in self.outputs.values():
                if not out.closed: out.close()
        return not self.error.is_set() and stopped


def _windows():
    import ctypes as c
    from ctypes import wintypes as w

    class Basic(c.Structure):
        _fields_ = [('PerProcessUserTimeLimit', c.c_longlong), ('PerJobUserTimeLimit', c.c_longlong),
                    ('LimitFlags', w.DWORD), ('MinimumWorkingSetSize', c.c_size_t),
                    ('MaximumWorkingSetSize', c.c_size_t), ('ActiveProcessLimit', w.DWORD),
                    ('Affinity', c.c_size_t), ('PriorityClass', w.DWORD), ('SchedulingClass', w.DWORD)]
    class IO(c.Structure):
        _fields_ = [(n, c.c_ulonglong) for n in ('ReadOperationCount', 'WriteOperationCount',
                    'OtherOperationCount', 'ReadTransferCount', 'WriteTransferCount', 'OtherTransferCount')]
    class Extended(c.Structure):
        _fields_ = [('BasicLimitInformation', Basic), ('IoInfo', IO), ('ProcessMemoryLimit', c.c_size_t),
                    ('JobMemoryLimit', c.c_size_t), ('PeakProcessMemoryUsed', c.c_size_t),
                    ('PeakJobMemoryUsed', c.c_size_t)]
    class Accounting(c.Structure):
        _fields_ = [(n, c.c_longlong) for n in ('TotalUserTime', 'TotalKernelTime',
                    'ThisPeriodTotalUserTime', 'ThisPeriodTotalKernelTime')] + [
                    (n, w.DWORD) for n in ('TotalPageFaultCount', 'TotalProcesses', 'ActiveProcesses',
                                          'TotalTerminatedProcesses')]
    k = c.WinDLL(r'C:\Windows\System32\kernel32.dll', use_last_error=True)
    definitions = [
        ('CreateJobObjectW', [w.LPVOID, w.LPCWSTR], w.HANDLE),
        ('SetInformationJobObject', [w.HANDLE, c.c_int, w.LPVOID, w.DWORD], w.BOOL),
        ('QueryInformationJobObject', [w.HANDLE, c.c_int, w.LPVOID, w.DWORD, w.LPVOID], w.BOOL),
        ('AssignProcessToJobObject', [w.HANDLE, w.HANDLE], w.BOOL),
        ('TerminateJobObject', [w.HANDLE, w.UINT], w.BOOL),
        ('ResumeThread', [w.HANDLE], w.DWORD), ('CloseHandle', [w.HANDLE], w.BOOL),
        ('GetHandleInformation', [w.HANDLE, c.POINTER(w.DWORD)], w.BOOL),
        ('WaitForSingleObject', [w.HANDLE, w.DWORD], w.DWORD)]
    for name, args, result in definitions:
        f = getattr(k, name); f.argtypes = args; f.restype = result
    return c, w, k, Extended, Accounting


def _write_state(directory, value):
    raw=(json.dumps(value, sort_keys=True)+'\n').encode()
    path=directory/'disposition.json'
    if not path.exists():
        core._atomic(path,raw)
    else:
        # Audit only: an interrupted/partial record is QUARANTINE, never
        # authority or permission to retry. Avoid directory mutation under the
        # deliberately non-mutation-sharing stable input-parent handles.
        with path.open('r+b') as out:
            out.seek(0); out.write(raw); out.truncate(); out.flush(); os.fsync(out.fileno())


@contextmanager
def _held_installed_host(path=HOST,expected=HOST_SHA):
    """Installed Host may have package-manager hardlinks; deny mutation by handle.

    Candidate/input hardlink policy is unchanged. This exception is confined to
    the exact already-installed trusted Host, not an intake or dispatch fallback.
    """
    import msvcrt
    require((path,expected) in ((HOST,HOST_SHA),(RUNNER,RUNNER_SHA)),'TRUSTED_HOST_COMPONENT')
    storage._verify_path_chain_no_links(path)
    parents=[]
    try:
        for parent in storage._existing_ancestors(path):
            handle=storage._win_handle(parent,directory=True)
            parents.append(handle)
        handle=storage._win_handle(path,directory=False)
        before=storage._win_identity(handle)
        with os.fdopen(msvcrt.open_osfhandle(handle,os.O_RDONLY|os.O_BINARY),'rb') as stream:
            digest=hashlib.sha256()
            while chunk:=stream.read(1048576): digest.update(chunk)
            require(digest.hexdigest()==expected,'HOST_IDENTITY')
            yield
            require(storage._win_identity(msvcrt.get_osfhandle(stream.fileno()))==before,'HOST_CHANGED')
    finally:
        for handle in reversed(parents): storage._win_close(handle)


def _fixed_attempt(role,case):
    """Two closed roles consume one guard; neither accepts caller commands."""
    require(role in ('public','native'),'CLOSED_ROLE')
    require(case in PUBLIC_CASES if role=='public' else case=='qualification','PUBLIC_CASE')
    _source_gate()
    require(os.name == 'nt', 'WINDOWS_REQUIRED')
    if role=='native': _verify_native_owner()  # Before any materialization/reservation.
    import _winapi
    import msvcrt
    c, w, k, Extended, Accounting = _windows()
    name=WORK+'/'+case if role=='public' else 'output/g6-native-private-once-v1'
    parent = safe_path(ROOT, Path(name).parent.as_posix()); parent.mkdir(parents=True, exist_ok=True)
    directory = safe_path(ROOT,name)
    try:
        directory.mkdir()  # Exclusive reservation precedes every Host launch.
    except FileExistsError:
        raise BindingHold('ATTEMPT_RESERVED_NO_REPLAY') from None
    state = {'schema': 'nexus.g6.fixed-public-attempt.v1' if role=='public' else 'nexus.g6.fixed-native-attempt.v1', 'case': case, 'status': 'QUARANTINE',
             'reason': 'RESERVED_NOT_COMPLETED', 'retired': True, 'automatic_retry': False,
             'candidate_executed': False, 'model_loaded': False, 'private_input_processed': False,
             'real_admission': 'NO','binding_sha256':normalized_sha(Path(__file__)),
             'fixture_sha256':normalized_sha(FIXTURE),'host_sha256':HOST_SHA}
    _write_state(directory, state)
    binary=directory/'bin'; data=directory/'input'; result=directory/'result'
    for path in (binary, data, result): path.mkdir()
    if role=='public':
        (binary/'fixture.py').write_bytes(stable_read_bytes(FIXTURE, maximum_bytes=32768))
        (data/'public.txt').write_bytes(b'PUBLIC_ONLY_FINITE_INPUT')
        (data/'unlisted.txt').write_bytes(b'PUBLIC_UNLISTED')
        (directory/'outside.txt').write_bytes(b'PUBLIC_OUT_OF_SCOPE')
        with Path(r'C:\Windows\System32\version.dll').open('rb') as source: public_dll=source.read(65537)
        require(len(public_dll)<=65536,'PUBLIC_SYSTEM_DLL_BOUND')
        (binary/'public-backend.dll').write_bytes(public_dll)
        (data/'unlisted-backend.dll').write_bytes(public_dll)
        state['public_dll_sha256']=hashlib.sha256(public_dll).hexdigest()
    else:
        _prepare_native(binary,data)
    job=hp=ht=None; handles=[]; collector=_Collector(result); started=time.monotonic()
    completed=False; listener=None; stop=threading.Event(); connections=[]; network_thread=None
    wall = 7.0 if case == 'timeout' else 16.0
    cpu = 1 if case == 'cpu' else 8
    memory = 384*1024**2 if case == 'memory' else 2*1024**3
    active = 8
    if role=='native':
        plan=native_plan(); wall=plan['limits']['wall_seconds']; cpu=plan['limits']['user_cpu_seconds']
        memory=plan['limits']['job_memory_bytes']; active=plan['limits']['active_processes']
    try:
        state['stage']='PUBLIC_ENDPOINT'
        # Only a newly owned public loopback endpoint. No external service call.
        port=0
        if role=='public':
            listener=socket.socket(); listener.bind(('127.0.0.1',0)); listener.listen(4); listener.settimeout(.1)
            port=listener.getsockname()[1]
            with socket.create_connection(('127.0.0.1',port),timeout=1): pass
            connection,_=listener.accept(); connection.close()
        def serve():
            while not stop.is_set():
                try:
                    connection,_=listener.accept(); connections.append(True); connection.close()
                except socket.timeout: pass
                except OSError: break
        if role=='public': network_thread=threading.Thread(target=serve,daemon=True); network_thread.start()
        if role=='native':
            verified_owner=_verify_native_owner()
            state['authenticated_payload_sha256']=verified_owner[0]
        eligibility_observed=verified_owner[3] if role=='native' else time.monotonic()
        with ExitStack() as held:
            state['stage']='HELD_HOST'
            held.enter_context(_held_installed_host())
            held.enter_context(_held_installed_host(RUNNER,RUNNER_SHA))
            inputs=([binary/'fixture.py',binary/'public-backend.dll',data/'public.txt'] if role=='public' else
                    [*(binary/m['path'] for m in plan['members']),binary/'LICENSE-LLVM-OpenMP',data/'task.txt'])
            for path in inputs:
                handle=held.enter_context(open_stable_input(path, maximum_bytes=33554432 if role=='native' else 65536))
                if role=='native':
                    from .g6_local_model_intake import _hash_input
                    expected=next((m for m in load_policy()['runtime']['members'] if m['path']==path.name),None)
                    if path.name=='task.txt': expected={'bytes':len(NATIVE_PROMPT),'sha256':hashlib.sha256(NATIVE_PROMPT).hexdigest()}
                    require(expected is not None,'NATIVE_INPUT_IDENTITY')
                    _hash_input(handle,expected,0)
            if role=='native':
                from .g6_local_model_intake import _hash_input
                model=held.enter_context(open_stable_input(Path(plan['model_blob']),maximum_bytes=650000000))
                _hash_input(model,plan['model'],0)
                require({p.name for p in binary.iterdir()}==NATIVE|{'LICENSE-LLVM-OpenMP'},'NATIVE_LOADER_INVENTORY')
            job=k.CreateJobObjectW(None, None); require(job, 'JOB_CREATE')
            state['stage']='JOB_LIMIT_SETUP'
            flags=w.DWORD(); require(k.GetHandleInformation(job,c.byref(flags)) and not flags.value & 1, 'JOB_HANDLE_INHERIT')
            limits=Extended(); limits.BasicLimitInformation.LimitFlags=0x2000|0x200|0x8|0x4
            limits.BasicLimitInformation.ActiveProcessLimit=active
            limits.BasicLimitInformation.PerJobUserTimeLimit=cpu*10000000
            limits.JobMemoryLimit=memory
            require(k.SetInformationJobObject(job,9,c.byref(limits),c.sizeof(limits)), 'JOB_LIMITS')
            observed=Extended(); require(k.QueryInformationJobObject(job,9,c.byref(observed),c.sizeof(observed),None), 'JOB_LIMIT_READBACK')
            state['stage']='JOB_LIMIT_COMPARE'
            require(observed.BasicLimitInformation.LimitFlags==limits.BasicLimitInformation.LimitFlags
                    and observed.BasicLimitInformation.ActiveProcessLimit==active
                    and observed.BasicLimitInformation.PerJobUserTimeLimit==cpu*10000000
                    and observed.JobMemoryLimit==memory, 'JOB_LIMIT_BINDING')
            # Sentinel is intentionally inheritable, but excluded from the explicit
            # list. The fixture proves it cannot use this Host-only file handle.
            sentinel=os.open(result/'sentinel',os.O_CREAT|os.O_EXCL|os.O_RDWR,0o600)
            state['stage']='HANDLE_SETUP'
            handles.append(sentinel); os.set_inheritable(sentinel,True)
            stdin=os.open(os.devnull,os.O_RDONLY); handles.append(stdin)
            reads=[]; writes=[]
            for _ in range(2):
                read,write=os.pipe(); reads.append(read); writes.append(write); handles.extend((read,write))
                os.set_inheritable(read,False); os.set_inheritable(write,True)
            os.set_inheritable(stdin,True)
            allowed=[msvcrt.get_osfhandle(fd) for fd in (stdin,*writes)]
            argv,fs=_arguments(binary,data,result,case,msvcrt.get_osfhandle(sentinel),port,role=role)
            si=subprocess.STARTUPINFO(); si.dwFlags|=subprocess.STARTF_USESTDHANDLES
            si.hStdInput,si.hStdOutput,si.hStdError=allowed
            si.lpAttributeList={'handle_list':allowed}
            state['stage']='CREATE_SUSPENDED'
            hp,ht,pid,_=_winapi.CreateProcess(str(HOST),subprocess.list2cmdline(argv),None,None,True,
                    0x4|0x08000000,_environment(result),str(binary),si)
            require(k.AssignProcessToJobObject(job,hp), 'JOB_ASSIGN_SUSPENDED')
            for fd in writes: os.close(fd); handles.remove(fd)
            for fd,channel in zip(reads,('stdout.bin','stderr.bin')):
                collector.start(fd,channel); handles.remove(fd)
            state.update(stage='JOB_BOUND_BEFORE_RESUME',launcher_pid=pid,limits={
                'memory_bytes':memory,'active_processes':active,'user_cpu_seconds':cpu,
                'wall_seconds':wall,'retained_stdout_stderr_bytes':OUTPUT_LIMIT},
                handle_allowlist_count=3,job_handle_inherited=False,filesystem=fs,
                telemetry_overrides=list(TELEMETRY),environment_names=sorted(_environment(result)))
            state['stage']='PERSIST_BOUND_STATE'
            if role=='native':
                state.update(candidate_execution_attempted=True,candidate_executed='UNKNOWN_NOT_SELF_CERTIFIED',
                             model_loaded='UNKNOWN_NOT_SELF_CERTIFIED')
            _write_state(directory,state)
            state['stage']='RESUME_BOUND_LAUNCHER'
            _source_gate()
            if role=='native': _native_resume_gate(verified_owner,eligibility_observed)
            require(k.ResumeThread(ht)!=0xffffffff,'RESUME')
            _winapi.CloseHandle(ht); ht=None
            reason=None
            state['stage']='OBSERVE_BOUND_JOB'
            ready_at=None
            while k.WaitForSingleObject(hp,0)==258:
                elapsed=time.monotonic()-started
                if role=='public' and case in ('cancel','timeout') and ready_at is None:
                    try:
                        with (result/'stdout.bin').open('rb') as stream: ready=json.loads(stream.read(256))
                        if isinstance(ready,dict) and len(ready.get('public_pids',[]))==2:
                            ready_at=time.monotonic(); state['public_tree_ready']=True
                    except (OSError,ValueError): pass
                if collector.overflow.is_set(): reason='OUTPUT_LIMIT'
                elif collector.error.is_set(): reason='COLLECTOR_ERROR'
                elif (directory/'cancel.request').exists() or (case=='cancel' and ready_at is not None and time.monotonic()-ready_at>=.2): reason='CANCELLED'
                elif elapsed>=wall: reason='TIMEOUT'
                if reason: break
                time.sleep(.01)
            code=_winapi.GetExitCodeProcess(hp)
            state['stage']='ACCOUNT_BOUND_JOB'
            account=Accounting(); require(k.QueryInformationJobObject(job,1,c.byref(account),c.sizeof(account),None),'JOB_ACCOUNTING')
            if reason is None and account.ActiveProcesses: reason='LATE_DESCENDANT'
            require(k.TerminateJobObject(job,1),'JOB_TERMINATE')
            until=time.monotonic()+2
            while True:
                require(k.QueryInformationJobObject(job,1,c.byref(account),c.sizeof(account),None),'JOB_QUIESCENCE')
                if account.ActiveProcesses==0: break
                require(time.monotonic()<until,'JOB_NOT_QUIESCENT'); time.sleep(.01)
            require(collector.finish(),'COLLECTOR_NOT_CLOSED')
            state['stage']='COLLECTED_LOCAL_BYTES'
            reason=reason or ('OUTPUT_LIMIT' if collector.overflow.is_set() else None)
            stdout=(result/'stdout.bin').read_bytes()
            parsed=None
            if role=='native' and reason is None and code==0:
                if stdout.strip()!=b'PUBLIC_G6_NATIVE_QUALIFICATION_COMPLETE': reason='UNVERIFIED_NATIVE_RESULT'
                else: parsed={'status':'PUBLIC_FIXTURE_COMPLETE'}
            elif reason is None and code==0:
                try: parsed=json.loads(stdout)
                except (ValueError,UnicodeError): reason='PARTIAL_RESULT'
            if reason is None and (code!=0 or not isinstance(parsed,dict) or parsed.get('status')!='PUBLIC_FIXTURE_COMPLETE'):
                reason='UNVERIFIED_RESULT'
            if reason is None and case in ('success','io') and not all(parsed.get(n) is True for n in (
                    'exact_read','unlisted_denied','outside_denied','writes_denied',
                    'environment_fixed','sentinel_unavailable','network_denied','exact_backend_loaded',
                    'unlisted_backend_denied')):
                reason='PUBLIC_CONTROL_FAILED'
            if reason is None and ((case=='memory' and parsed.get('memory_denied') is not True)
                                   or (case=='processes' and parsed.get('processes_denied') is not True)):
                reason='PUBLIC_RESOURCE_CONTROL_FAILED'
            state.update(status=('PUBLIC_FIXTURE_VERIFIED' if role=='public' else 'NATIVE_BOUNDED_RESULT_OBSERVED') if reason is None else 'QUARANTINE',
                         reason=reason or ('PUBLIC_ONLY' if role=='public' else 'NATIVE_RESULT_NOT_FINAL_G6_ACCEPTANCE'),returncode=code,job_active_after_termination=0,
                         user_cpu_100ns=account.TotalUserTime,total_processes=account.TotalProcesses,
                         retained_bytes=collector.count,elapsed_seconds=round(time.monotonic()-started,3),
                         stdout_sha256=hashlib.sha256(stdout).hexdigest(),
                         stderr_sha256=hashlib.sha256((result/'stderr.bin').read_bytes()).hexdigest(),
                         sandbox_network_connections=len(connections),sentinel_file_unchanged=os.fstat(sentinel).st_size==0)
            if role=='public' and isinstance(parsed,dict):
                # These are closed public-fixture booleans only, never a generic
                # result passthrough or arbitrary native output admission.
                state['public_checks']={n:parsed.get(n) is True for n in (
                    'exact_read','unlisted_denied','outside_denied','writes_denied',
                    'environment_fixed','sentinel_unavailable','network_denied','memory_denied','processes_denied',
                    'environment_path_exact','environment_ggml_absent','environment_hf_absent',
                    'environment_llama_absent','environment_proxy_absent','path_single',
                    'path_casefold_system32','path_only_system32','exact_backend_loaded',
                    'unlisted_backend_denied')}
            completed=True
    except Exception as error:
        state.update(status='QUARANTINE',reason='BINDING_OR_HOST_FAILURE',exception_class=type(error).__name__,winerror=c.get_last_error())
    finally:
        if not completed: state.update(status='QUARANTINE',reason='BINDING_OR_HOST_FAILURE')
        if job: k.CloseHandle(job)
        if ht: _winapi.CloseHandle(ht)
        if hp:
            if k.WaitForSingleObject(hp,2000)==258: _winapi.TerminateProcess(hp,1)
            _winapi.CloseHandle(hp)
        for fd in handles:
            try: os.close(fd)
            except OSError: pass
        collector.finish()
        stop.set()
        if listener: listener.close()
        if network_thread: network_thread.join(timeout=1)
        _write_state(directory,state)
    return state


def reconcile_public(case):
    """Interrupted reserved attempts remain retired; no execution/retry path."""
    require(case in PUBLIC_CASES,'PUBLIC_CASE')
    directory=safe_path(ROOT,WORK+'/'+case)
    require(directory.is_dir(),'NO_RESERVED_ATTEMPT')
    try:
        value=json.loads(stable_read_bytes(directory/'disposition.json',maximum_bytes=32768))
        require(isinstance(value,dict) and value.get('schema')=='nexus.g6.fixed-public-attempt.v1'
                and value.get('case')==case,'AUDIT_SHAPE')
    except (OSError,ValueError):
        value={'schema':'nexus.g6.fixed-public-attempt.v1','case':case,'status':'QUARANTINE'}
    if value.get('status')!='PUBLIC_FIXTURE_VERIFIED':
        value.update(status='QUARANTINE',reason='UNKNOWN_OR_INTERRUPTED',retired=True,automatic_retry=False)
        # Preserve the original partial/unknown bytes; this is additive evidence.
        destination=directory/'reconciliation.json'
        if not destination.exists(): core._atomic(destination,(json.dumps(value,sort_keys=True)+'\n').encode())
    return value
