"""Finite public-only target for the fixed G6 binding qualification.

No GGUF/native candidate access; no private inputs, credentials or external URL.
"""
from pathlib import Path
import ctypes
from ctypes import wintypes
import json
import os
import subprocess
import socket
import sys
import time

case=sys.argv[1]; root=Path(sys.argv[2]); sentinel=int(sys.argv[3]); port=int(sys.argv[4])
if case=='child':
    for _ in range(100):
        os.write(1,b'PUBLIC_LATE\n'); time.sleep(.1)
    raise SystemExit(0)
result={'status':'PUBLIC_FIXTURE_COMPLETE'}
if case in ('success','io'):
    result['exact_read']=(root/'input/public.txt').read_bytes()==b'PUBLIC_ONLY_FINITE_INPUT'
    for name,path in [('unlisted_denied',root/'input/unlisted.txt'),('outside_denied',root/'outside.txt')]:
        try: path.read_bytes(); result[name]=False
        except OSError: result[name]=True
    result['writes_denied']=True
    for path in (root/'input/write.txt',root/'result/write.txt',root/'bin/write.txt'):
        try: path.write_bytes(b'PUBLIC'); result['writes_denied']=False
        except OSError: pass
    result['environment_path_exact']=os.environ.get('PATH')==r'C:\Windows\System32'
    entries=os.environ.get('PATH','').split(';')
    result['path_single']=len(entries)==1
    result['path_casefold_system32']=os.environ.get('PATH','').casefold()==r'C:\Windows\System32'.casefold()
    result['path_only_system32']=bool(entries) and all(entry.casefold()==r'C:\Windows\System32'.casefold() for entry in entries)
    result['environment_ggml_absent']='GGML_BACKEND_PATH' not in os.environ
    result['environment_hf_absent']='HF_HOME' not in os.environ
    result['environment_llama_absent']='LLAMA_ARG_MODEL' not in os.environ
    result['environment_proxy_absent']=all(key not in os.environ for key in ('HTTP_PROXY','HTTPS_PROXY','ALL_PROXY'))
    result['environment_fixed']=all(result[n] for n in ('environment_path_exact','environment_ggml_absent',
        'environment_hf_absent','environment_llama_absent','environment_proxy_absent'))
    backend=ctypes.WinDLL(str(root/'bin/public-backend.dll'))
    result['exact_backend_loaded']=bool(backend._handle) and hasattr(backend,'GetFileVersionInfoSizeW')
    try:
        unexpected=ctypes.WinDLL(str(root/'input/unlisted-backend.dll'))
        result['unlisted_backend_denied']=False
    except OSError: result['unlisted_backend_denied']=True
    k=ctypes.WinDLL('kernel32',use_last_error=True)
    k.GetFinalPathNameByHandleW.argtypes=[wintypes.HANDLE,wintypes.LPWSTR,wintypes.DWORD,wintypes.DWORD]
    k.GetFinalPathNameByHandleW.restype=wintypes.DWORD
    value=ctypes.create_unicode_buffer(2048)
    try: count=k.GetFinalPathNameByHandleW(sentinel,value,len(value),0)
    except OSError as error:
        if error.winerror not in (6,-1073741816): raise
        count=0  # ERROR_INVALID_HANDLE / STATUS_INVALID_HANDLE: expected negative.
    # Compare only the identity of our deliberately excluded public sentinel;
    # do not read/write any object at a reused numeric handle value.
    result['sentinel_unavailable']=not (0<count<len(value) and value.value.removeprefix('\\\\?\\').casefold()==str(root/'result/sentinel').casefold())
    try:
        connection=socket.create_connection(('127.0.0.1',port),timeout=.2); connection.close(); result['network_denied']=False
    except OSError: result['network_denied']=True
elif case in ('overflow','stderr_overflow'):
    for _ in range(256): os.write(1 if case=='overflow' else 2,b'P'*4096)
elif case=='nonzero': raise SystemExit(7)
elif case=='partial': os.write(1,b'{"status":'); raise SystemExit(0)
elif case in ('timeout','cancel','controller_failure'):
    child=subprocess.Popen([sys.executable,'-I','-c','import time;time.sleep(10)'])
    print(json.dumps({'public_pids':[os.getpid(),child.pid]}),flush=True)
    time.sleep(10)
elif case=='cpu':
    deadline=time.monotonic()+10
    while time.monotonic()<deadline: pass
elif case=='memory':
    blocks=[]
    try:
        for _ in range(64): blocks.append(bytearray(16*1024**2))
        result['memory_denied']=False
    except MemoryError: result['memory_denied']=True
elif case=='processes':
    children=[]
    try:
        for _ in range(16): children.append(subprocess.Popen([sys.executable,'-I','-c','import time;time.sleep(5)'],stdin=subprocess.DEVNULL,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL))
        result['processes_denied']=False
    except OSError: result['processes_denied']=True
    finally:
        for child in children:
            child.terminate(); child.wait(timeout=2)
elif case=='late_output':
    os.write(1,b'{"status":"PUBLIC_FIXTURE_COMPLETE"}\n')
    subprocess.Popen([sys.executable,'-I',__file__,'child',str(root),str(sentinel),str(port)])
    time.sleep(.5)  # Allow actual trailing public bytes after the completion record.
    raise SystemExit(0)
else: raise SystemExit(9)
print(json.dumps(result))
