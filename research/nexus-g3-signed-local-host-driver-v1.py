"""One-off E2E Host tool driver, outside the product/package. Fixed profile only."""
import hashlib,json,re,subprocess,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from ash import core_host_loop as h
from ash.core_capabilities import write

directory=Path(sys.argv[1]).resolve(strict=True)
action=json.loads(Path(sys.argv[2]).read_bytes())
state=h._load(directory)
assert all(action[k]==state['inflight'][k] for k in ('task_id','action_id','stage'))
stage=action['stage'];trace=[];data={};outcome='ok'
try:
    if stage=='report':
        assert action['directory']==str(directory) and action['files']==h._report(state)
        for name,body in action['files'].items():write(directory,name,body.encode('utf-8'))
        data={'files':['report.json','report.md']}
    else:
        assert action['commands']==h._commands(state,stage)
        outputs={}
        for item in action['commands']:
            remaining=state['inflight']['deadline']-time.time()
            assert remaining>0
            result=subprocess.run(item['argv'],capture_output=True,timeout=remaining,shell=False)
            assert len(result.stdout)+len(result.stderr)<=65536
            trace.append({'key':item['key'],'argv':item['argv'],'exit_code':result.returncode,
                          'stdout_bytes':len(result.stdout),'stderr_present':bool(result.stderr)})
            outputs[item['key']]=(result.returncode,result.stdout)
        repository=None;checks=None
        if stage in ('inspect','verify'):
            assert all(outputs[k][0]==0 for k in ('root','head','status','tracked'))
            raw=outputs['status'][1];entries=raw.split(b'\0');i=0;count=0
            while i<len(entries) and entries[i]:
                assert len(entries[i])>=4 and entries[i][2:3]==b' '
                renamed=b'R' in entries[i][:2] or b'C' in entries[i][:2]
                count+=1;i+=2 if renamed else 1
            repository={'root':str(Path(outputs['root'][1].decode('utf-8').strip()).resolve()),
                        'head':outputs['head'][1].decode('ascii').strip(),
                        'status_sha256':hashlib.sha256(raw).hexdigest(),'changed_tracked':count,
                        'tracked_files':sorted(x for x in outputs['tracked'][1].decode('utf-8').split('\0') if x)}
        if stage in ('check','verify'):
            checks={};kinds={'trailing whitespace':'trailing_whitespace','space before tab in indent':'space_before_tab',
                             'new blank line at EOF':'blank_line_at_eof'}
            for key in ('unstaged','staged'):
                code,raw=outputs[key];assert code in (0,2)
                findings=[]
                for line in raw.decode('utf-8').splitlines():
                    match=re.fullmatch(r'(.+?):(\d+): (trailing whitespace|space before tab in indent|new blank line at EOF)\.',line)
                    if match:
                        assert match[1] in state['files']
                        findings.append({'path':match[1],'line':int(match[2]),'kind':kinds[match[3]]})
                assert bool(findings)==(code==2)
                if code==0:assert not raw.strip()
                checks[key]={'exit_code':code,'findings':findings}
        data=repository if stage=='inspect' else checks if stage=='check' else {'repository':repository,'checks':checks}
except subprocess.TimeoutExpired:outcome='unknown';data={}
except (AssertionError,OSError,UnicodeError,ValueError):outcome='failed';data={}
observation={k:action[k] for k in ('task_id','action_id','stage')}
observation.update(host_status=outcome,data=data)
path=directory/(stage+'-observation.json');write(directory,path.name,h.core._bytes(observation)+b'\n')
closed={'stage':stage,'host_status':outcome,'actual_git_processes':len(trace),'commands':trace,
        'raw_source_or_stderr_retained':False,'observation_sha256':hashlib.sha256(path.read_bytes()).hexdigest()}
if stage=='verify':
    closed['report_readback']=[{'path':name,'sha256':hashlib.sha256((directory/name).read_bytes()).hexdigest()}
                               for name in ('report.json','report.md')]
write(directory,stage+'-native-trace.json',h.core._bytes(closed)+b'\n')
print(json.dumps({'stage':stage,'host_status':outcome,'actual_git_processes':len(trace),
                  'observation_path':str(path),'native_trace_path':str(directory/(stage+'-native-trace.json'))}))
sys.exit(outcome!='ok')
