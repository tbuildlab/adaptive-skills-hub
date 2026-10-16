"""One fixed PUBLIC Git pilot recipe; no product runner or execution authority.

Native uses stdlib/Git directly. Nexus uses the existing read-only Core adapter.
Shared tools/observer facts receive no incremental evidence credit in either arm.
"""
from pathlib import Path
import hashlib,json,os,re,subprocess,sys,time

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
GIT=Path(r'C:/Program Files/Git/cmd/git.exe')
FILES=['README.md','docs/nexus-roadmap-v2.md']
TASK='Inspect this local Git repository changes and whitespace checks, then return a maintenance report.'
CASES=('clean','findings','resume','pending_unknown')
ORDER=(('clean','native'),('clean','nexus'),('findings','nexus'),('findings','native'),
       ('resume','native'),('resume','nexus'),('pending_unknown','nexus'),('pending_unknown','native'))
BASE=ROOT.parent/'nexus-g6-core-host-value-pilot-v1'
PREP=ROOT/'output/g6-core-host-value-pilot-v1'

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(p):return json.loads(Path(p).read_bytes())
def save(p,v,new=False):
    p=Path(p);raw=(json.dumps(v,sort_keys=True,indent=2)+'\n').encode()
    if new:
        with p.open('xb') as out:out.write(raw)
    else:
        temp=p.with_suffix('.next');temp.write_bytes(raw);os.replace(temp,p)

def commands(repo,stage):
    prefix=[str(GIT),'--no-optional-locks','--no-pager','--literal-pathspecs',
        '-c','color.ui=false','-c','core.quotePath=false','-c','core.fsmonitor=false',
        '-c','core.untrackedCache=false','-C',str(repo.resolve())]
    inspect=[('root',['rev-parse','--show-toplevel']),('head',['rev-parse','--verify','HEAD']),
        ('status',['status','--porcelain=v1','-z','--untracked-files=no']),('tracked',['ls-files','-z','--',*FILES])]
    checks=[('unstaged',['diff','--no-ext-diff','--no-textconv','--check','--',*FILES]),
        ('staged',['diff','--no-ext-diff','--no-textconv','--cached','--check','--',*FILES])]
    return [{'key':k,'argv':prefix+a} for k,a in (inspect if stage=='inspect' else checks if stage=='check' else inspect+checks)]

def observe_git(repo,stage,deadline=None):
    deadline=time.time()+20 if deadline is None else deadline
    outputs={};trace=[]
    for item in commands(repo,stage):
        remaining=deadline-time.time();assert remaining>0
        proc=subprocess.run(item['argv'],capture_output=True,timeout=remaining,shell=False)
        assert time.time()<deadline
        assert len(proc.stdout)+len(proc.stderr)<=65536
        outputs[item['key']]=(proc.returncode,proc.stdout)
        trace.append({'key':item['key'],'exit_code':proc.returncode,
            'stdout_sha256':hashlib.sha256(proc.stdout).hexdigest(),'stderr_present':bool(proc.stderr)})
    repository=checks=None
    if stage in ('inspect','verify'):
        assert all(outputs[k][0]==0 for k in ('root','head','status','tracked'))
        raw=outputs['status'][1];entries=raw.split(b'\0');i=count=0
        while i<len(entries) and entries[i]:
            assert len(entries[i])>=4 and entries[i][2:3]==b' '
            count+=1;i+=2 if b'R' in entries[i][:2] or b'C' in entries[i][:2] else 1
        repository={'root':str(Path(outputs['root'][1].decode().strip()).resolve()),
            'head':outputs['head'][1].decode().strip(),'status_sha256':hashlib.sha256(raw).hexdigest(),
            'changed_tracked':count,'tracked_files':sorted(x for x in outputs['tracked'][1].decode().split('\0') if x)}
        assert repository['tracked_files']==FILES and repository['root']==str(repo.resolve())
    if stage in ('check','verify'):
        checks={};kinds={'trailing whitespace':'trailing_whitespace','space before tab in indent':'space_before_tab','new blank line at EOF':'blank_line_at_eof'}
        for key in ('unstaged','staged'):
            code,raw=outputs[key];assert code in (0,2);findings=[]
            for line in raw.decode().splitlines():
                m=re.fullmatch(r'(.+?):(\d+): (trailing whitespace|space before tab in indent|new blank line at EOF)\.',line)
                if m:
                    assert m[1] in FILES
                    findings.append({'path':m[1],'line':int(m[2]),'kind':kinds[m[3]]})
            assert bool(findings)==(code==2)
            if code==0:assert not raw.strip()
            checks[key]={'exit_code':code,'findings':findings}
    return (repository if stage=='inspect' else checks if stage=='check' else {'repository':repository,'checks':checks}),trace

def input_hashes(repo):
    for name in FILES:
        path=repo/name
        assert path.is_file() and path.stat().st_size<=262144
        for part in (path,*path.parents):
            assert not part.is_symlink() and not getattr(part.lstat(),'st_file_attributes',0)&0x400
    return {name:digest(repo/name) for name in FILES}

def native_save(path,state):
    raw=json.dumps(state,sort_keys=True,separators=(',',':')).encode()
    save(path,{'state':state,'sha256':hashlib.sha256(raw).hexdigest()})

def native_load(path):
    envelope=load(path);state=envelope['state']
    assert set(envelope)=={'state','sha256'}
    assert hashlib.sha256(json.dumps(state,sort_keys=True,separators=(',',':')).encode()).hexdigest()==envelope['sha256']
    return state

def native(directory,repo,case,resume=False):
    """Finite direct Host recipe. Equivalent checkpoint/readback, no Nexus calls."""
    statefile=directory/'native-checkpoint.json'
    state=native_load(statefile) if resume else {'repo':str(repo),'input_hashes':input_hashes(repo),
        'created_at':time.time(),'budget':{'max_commands':8,'total_seconds':600},'commands_used':0,'observations':[],'trace':[],'pending':None}
    assert state['repo']==str(repo) and state['input_hashes']==input_hashes(repo)
    assert state['commands_used']==len(state['observations']) and not state['pending']
    for stage in ('inspect','check','report','verify')[len(state['observations']):]:
        assert time.time()<state['created_at']+600 and state['commands_used']<8
        deadline=min(time.time()+20,state['created_at']+600)
        state['commands_used']+=1;state['pending']={'stage':stage,'deadline':deadline};native_save(statefile,state)
        if stage=='report':
            report={'repository':state['observations'][0],'checks':state['observations'][1],'input_hashes':state['input_hashes']}
            save(directory/'report.json',report,new=True)
            count=sum(len(c['findings']) for c in report['checks'].values())
            text=('# Git maintenance inspection\n\nHEAD: '+report['repository']['head']+
                '\n\nChanged tracked entries: '+str(report['repository']['changed_tracked'])+
                '\n\nAllowed files checked: 2\n\nWhitespace findings: '+str(count)+
                '\n\nRead-only inspection; detailed evidence: report.json.\n')
            with (directory/'report.md').open('x',encoding='utf8',newline='\n') as out:out.write(text)
            state['markdown_sha256']=digest(directory/'report.md')
            data={'files':['report.json','report.md']}
        else:
            data,trace=observe_git(repo,stage,deadline);state['trace']+=trace
        if case=='pending_unknown' and stage=='inspect':
            # Actual reads happened; their acknowledgement is deliberately unavailable.
            # Preserve charged pending state, never resend these reads automatically.
            state['status']='ambiguous';native_save(statefile,state);return state
        assert state['input_hashes']==input_hashes(repo)
        if stage=='verify':
            report=load(directory/'report.json')
            assert data['repository']==state['observations'][0] and data['checks']==state['observations'][1]
            assert report=={'repository':data['repository'],'checks':data['checks'],'input_hashes':state['input_hashes']}
            assert digest(directory/'report.md')==state['markdown_sha256']
            state['status']='completed_with_findings' if any(c['findings'] for c in data['checks'].values()) else 'completed'
            state['artifact_sha256']=digest(directory/'report.json')
        assert time.time()<deadline
        state['observations'].append(data);state['pending']=None;native_save(statefile,state)
        if case=='resume' and stage=='check' and not resume:return state
    return state

def nexus(directory,repo,case,resume=False):
    from ash import core_host_loop as host
    from ash.core_capabilities import write
    taskdir=directory/'task'
    state=host._load(taskdir) if resume else host.prepare(TASK,repo,FILES,taskdir)
    assert state['status']=='prepared';trace=[]
    for stage in ('inspect','check','report','verify')[len(state['observations']):]:
        action=host.next_action(taskdir)['action'];assert action and action['stage']==stage
        assert host.next_action(taskdir)['action'] is None  # No duplicated intent/charge.
        if stage=='report':
            for name,body in action['files'].items():write(taskdir,name,body.encode())
            data={'files':['report.json','report.md']}
        else:
            expected=commands(repo,stage)
            assert [{**x,'argv':[str(GIT),*x['argv'][1:]]} for x in action['commands']]==expected
            data,called=observe_git(repo,stage,host._load(taskdir)['inflight']['deadline']);trace+=called
        observation={k:action[k] for k in ('task_id','action_id','stage')}
        if case=='pending_unknown' and stage=='inspect':
            observation.update(host_status='unknown',data={})
        else:observation.update(host_status='ok',data=data)
        state=host.observe(taskdir,observation)
        if state['status']=='ambiguous':break
        assert state['status'] in ('prepared','completed','completed_with_findings'),state['blocker']
        if case=='resume' and stage=='check' and not resume:break
    save(directory/('nexus-trace-resume.json' if resume else 'nexus-trace.json'),trace,new=True)
    return state

def actor(case,arm,resume=False):
    assert case in CASES and arm in ('native','nexus')
    binding=load(BASE/'binding.json');repo=Path(binding['repositories'][case]);directory=BASE/(case+'-'+arm)
    assert load(BASE/'batch-reservation.json')=={'binding_sha256':digest(BASE/'binding.json'),'order':[list(x) for x in ORDER]}
    assert not (BASE/'pilot-result.json').exists()
    prior=ORDER[:ORDER.index((case,arm))];names={c+'-'+a for c,a in ORDER}
    assert {p.name for p in BASE.iterdir() if p.is_dir() and p.name in names}=={c+'-'+a for c,a in prior}|({directory.name} if resume else set())
    for c,a in prior:
        previous=load(BASE/(c+'-'+a)/'disposition.json')
        assert previous['retired'] is True and previous['automatic_retry'] is False and previous['correct_outcome'] is True
    assert not resume or (case=='resume' and not (directory/'actor-resumed.json').exists())
    assert digest(__file__)==binding['source_sha256'] and digest(GIT)==binding['git_sha256']
    assert sys.executable==binding['python_executable'] and digest(sys.executable)==binding['python_sha256']
    assert subprocess.check_output([str(GIT),'-C',str(ROOT),'rev-parse','HEAD'],text=True).strip()==binding['source_head']
    assert all(hashlib.sha256((ROOT/n).read_bytes().replace(b'\r\n',b'\n')).hexdigest()==h for n,h in binding['source_material'].items())
    assert digest(ROOT/'docs/nexus-g6-core-host-value-pilot-design-v1.md')==binding['design_sha256']
    assert input_hashes(repo)==binding['inputs'][case]
    if not resume:directory.mkdir(exist_ok=False)
    elif case!='resume':raise ValueError('NOT_A_RESUME_CASE')
    started=time.monotonic_ns()
    state=(native if arm=='native' else nexus)(directory,repo,case,resume)
    save(directory/('actor-resumed.json' if resume else 'actor-initial.json'),
        {'elapsed_ns':time.monotonic_ns()-started,'status':state['status'] if 'status' in state else 'prepared',
         'commands_used':state['commands_used'],'actor_pid':os.getpid()},new=True)

def audit_case(case,arm):
    """Common independent factual observer, no incremental arm credit."""
    binding=load(BASE/'binding.json');repo=Path(binding['repositories'][case]);directory=BASE/(case+'-'+arm)
    if arm=='native':
        state=native_load(directory/'native-checkpoint.json');report_path=directory/'report.json'
        trace=state['trace'];created=state['created_at'];budget=state['budget']
    else:
        from ash import core_host_loop as host
        state=host._load(directory/'task');report_path=directory/'task/report.json'
        trace=load(directory/'nexus-trace.json')
        if case=='resume':trace+=load(directory/'nexus-trace-resume.json')
        created=state['created_at_utc'];budget=state['budget']
    expected='ambiguous' if case=='pending_unknown' else 'completed_with_findings' if case=='findings' else 'completed'
    assert state['status']==expected and state['commands_used']==(1 if case=='pending_unknown' else 4)
    assert input_hashes(repo)==binding['inputs'][case]
    assert len(trace)==(4 if case=='pending_unknown' else 12)
    if case=='pending_unknown':
        assert not report_path.exists() and not (report_path.parent/'report.md').exists()
    else:
        report=load(report_path);fresh,_=observe_git(repo,'verify')
        assert report['repository']==fresh['repository'] and report['checks']==fresh['checks']
        assert bool(fresh['checks']['unstaged']['findings'])==(case=='findings')
        if arm=='native':
            assert state['artifact_sha256']==digest(report_path)
            assert state['markdown_sha256']==digest(directory/'report.md')
        else:
            assert state['receipt']['verification']=='passed'
            assert next(a['sha256'] for a in state['artifacts'] if a['path']=='report.json')==digest(report_path)
    return {'case':case,'arm':arm,'correct_outcome':True,'status':expected,
        'artifact_completed':case!='pending_unknown','artifact_sha256':digest(report_path) if report_path.exists() else None,
        'commands_used':state['commands_used'],'actual_git_reads':len(trace),
        'created':created,'budget':budget,'input_hashes':binding['inputs'][case],
        'policy_violations_observed':0,'retries':0,'runtime_human_interventions':0,
        'money_basis':'ESTIMATED_INCREMENTAL_ATTEMPT_BILLING','cost_microunits':0,
        'total_economic_cost':'UNMEASURED_EXCLUDED_NOT_ZERO','common_observer_incremental_credit':0,
        'real_admission':'NO'}

def run_pilot():
    """One fixed eight-slot pilot under existing safe task authority, no retry."""
    binding=load(BASE/'binding.json');marker=BASE/'batch-reservation.json'
    assert binding['source_sha256']==digest(__file__)
    save(marker,{'binding_sha256':digest(BASE/'binding.json'),'order':[list(x) for x in ORDER]},new=True)
    outcomes=[];failure=None;current=None
    try:
        for case,arm in ORDER:
            current=case+'-'+arm;started=time.monotonic_ns()
            subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--actor',case,arm],
                check=True,timeout=180,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            if case=='resume':
                directory=BASE/current
                initial=native_load(directory/'native-checkpoint.json') if arm=='native' else None
                if arm=='nexus':
                    from ash import core_host_loop as host
                    initial=host._load(directory/'task')
                initial_created=initial.get('created_at',initial.get('created_at_utc'))
                initial_budget=initial['budget'];assert initial['commands_used']==2
                save(directory/'resume-boundary.json',{'created':initial_created,'budget':initial_budget,'commands_used':2},new=True)
                subprocess.run([sys.executable,'-X','utf8',str(Path(__file__).resolve()),'--resume',case,arm],
                    check=True,timeout=180,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
            observed=audit_case(case,arm)
            if case=='resume':assert observed['created']==initial_created and observed['budget']==initial_budget
            observed['end_to_end_ns']=time.monotonic_ns()-started
            observed.update(retired=True,automatic_retry=False)
            save(BASE/current/'disposition.json',observed,new=True);outcomes.append(observed)
    except Exception as error:
        failure={'slot':current,'exception_class':type(error).__name__}
        raise
    finally:
        for case,arm in ORDER:
            directory=BASE/(case+'-'+arm);directory.mkdir(exist_ok=True)
            if not (directory/'disposition.json').exists():
                save(directory/'disposition.json',{'status':'QUARANTINE','retired':True,'automatic_retry':False,
                    'dispatch_requested':directory.name==current,
                    'execution_result':'UNKNOWN' if directory.name==current else 'NOT_DISPATCHED',
                    'reason':'PILOT_STOPPED_NOT_REPLAYABLE','real_admission':'NO'},new=True)
        save(BASE/'pilot-result.json',{'status':'PILOT_OBSERVATIONS_ONLY' if failure is None else 'PILOT_STOPPED',
            'outcomes':outcomes,'failure':failure,'retired':True,'automatic_retry':False,
            'value':'NOT_FINAL_COMPARISON','real_admission':'NO'},new=True)
    print(json.dumps({'status':'PILOT_OBSERVATIONS_ONLY','slots':len(outcomes),'retired':True,'real_admission':'NO'}))

def prepare():
    """Public data materialization only, no value observation or task execution."""
    BASE.mkdir(exist_ok=False);(BASE/'fixtures').mkdir()
    repo=BASE/'fixtures/findings';repo.mkdir()
    for name in FILES:
        p=repo/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes((ROOT/name).read_bytes())
    for argv in ([str(GIT),'init','-q',str(repo)],
        [str(GIT),'-C',str(repo),'-c','core.autocrlf=false','add','--',*FILES],
        [str(GIT),'-C',str(repo),'-c','user.name=Nexus public fixture','-c','user.email=fixture@example.invalid',
            '-c','commit.gpgSign=false','-c','core.hooksPath='+str(BASE/'absent-hooks'),'commit','-qm','PUBLIC input snapshot']):
        subprocess.run(argv,check=True,capture_output=True,timeout=20)
    with (repo/'README.md').open('ab') as out:out.write(b'\nPublic controlled whitespace finding.  \n')
    repositories={c:str((repo if c=='findings' else ROOT).resolve()) for c in CASES}
    binding={'repositories':repositories,'inputs':{c:input_hashes(Path(p)) for c,p in repositories.items()},
        'git_executable':str(GIT),'git_sha256':digest(GIT),'python_executable':sys.executable,
        'python_sha256':digest(sys.executable),'source_sha256':digest(__file__),
        'source_head':subprocess.check_output([str(GIT),'-C',str(ROOT),'rev-parse','HEAD'],text=True).strip(),
        'task':TASK,'cases':list(CASES),'order':[list(pair) for pair in ORDER],
        'source_material':{p.relative_to(ROOT).as_posix():hashlib.sha256(p.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
            for p in sorted((ROOT/'ash').rglob('*.py'))},
        'design_sha256':digest(ROOT/'docs/nexus-g6-core-host-value-pilot-design-v1.md'),
        'real_admission':'NO','automatic_retry':False,'new_model_invocations':0}
    skill=ROOT/'plugins/nexus-desktop/skills/nexus/SKILL.md'
    binding['source_material'][skill.relative_to(ROOT).as_posix()]=hashlib.sha256(skill.read_bytes().replace(b'\r\n',b'\n')).hexdigest()
    save(BASE/'binding.json',binding,new=True)
    print(json.dumps({'status':'PUBLIC_INPUTS_PREPARED_NO_VALUE_OBSERVATIONS','binding_sha256':digest(BASE/'binding.json')}))

if __name__=='__main__':
    if sys.argv[1:]==['--prepare']:prepare()
    elif sys.argv[1:]==['--pilot']:run_pilot()
    elif len(sys.argv)==4 and sys.argv[1]=='--actor':
        case,arm=sys.argv[2:];actor(case,arm)
    elif len(sys.argv)==4 and sys.argv[1]=='--resume':
        case,arm=sys.argv[2:];actor(case,arm,True)
    else:raise SystemExit('CLOSED_PUBLIC_PILOT_COMMAND')
