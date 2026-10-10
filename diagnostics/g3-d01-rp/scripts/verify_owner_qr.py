"""Versioned local Owner QR artifacts. Quarantine is the default deployment profile."""
from __future__ import annotations
import argparse,hashlib,importlib.util,json,re
from pathlib import Path,PurePosixPath
HERE=Path(__file__).resolve().parents[1]
SPEC=importlib.util.spec_from_file_location('owner_qr_base',HERE/'scripts/verify_owner_form_parser.py')
BASE=importlib.util.module_from_spec(SPEC);SPEC.loader.exec_module(BASE)
G3=BASE.G3
PROFILES=('DISABLED_OWNER_QR_QUARANTINE','LIVE_DIAGNOSTIC_OWNER_QR')
REVISION='g3-d01-owner-local-qr-v3'
VENDOR=HERE/'vendor/qrcodegen-v1.8.0-es6.js'
VENDOR_SHA256='5d65f10cbda9bc5f61df20e4dfb716ef3203b19f7daedb6cc7c0ae51193f033f'
OWNER='lib/server/owner-channel.js'
CLIENT='public/owner-transient.js'

def need(ok,why):
    if not ok:raise RuntimeError('OWNER_QR_BLOCKED: '+why)

def compose(data,profile=PROFILES[0]):
    need(profile in PROFILES,'profile')
    blobs=BASE.compose(data)
    blobs[G3.INPUT]=blobs[G3.INPUT].replace(BASE.REVISION.encode(),REVISION.encode())
    if profile==PROFILES[0]:
        need(blobs[G3.INPUT].count(b'"mode": "D01_DIAGNOSTIC_LIVE_STYTCH"')==1,'mode membership')
        blobs[G3.INPUT]=blobs[G3.INPUT].replace(b'"mode": "D01_DIAGNOSTIC_LIVE_STYTCH"',b'"mode": "FAKE_DISABLED"')
        for gate in ('CODE_REVIEWED_LIVE_ENABLED','DEPLOYMENT_REGISTRATION_ENABLED'):
            old=(gate+' = true').encode();need(blobs[G3.POLICY].count(old)==1,'gate membership')
            blobs[G3.POLICY]=blobs[G3.POLICY].replace(old,(gate+' = false').encode())
    replace=BASE.BASE.BASE.BASE.replace
    replace(blobs,OWNER,
        '<p>Transient manual authenticator enrollment. No automatic clipboard or third-party QR service.</p>\n<code id="seed">${escape(value.seed)}</code><code id="recovery">${escape(value.recovery.join(\'\\n\'))}</code>',
        '<p>Scan this private, locally generated QR with Google Authenticator. Do not screenshot or share it. Closing, hiding, cancelling or expiry retires this view.</p>\n<canvas id="totp-qr" role="img" aria-label="Private disposable TOTP enrollment QR"></canvas>\n<code id="seed" hidden>${escape(value.seed)}</code>')
    blobs[CLIENT]=(HERE/'future-deployment/owner-transient-qr.js').read_bytes().replace(b'\r\n',b'\n')
    vendor=VENDOR.read_bytes().replace(b'\r\n',b'\n');need(hashlib.sha256(vendor).hexdigest()==VENDOR_SHA256,'vendor pin')
    blobs['public/qrcodegen.js']=vendor+b'\nexport { qrcodegen };\n'
    return blobs

def validate(blobs,data,profile=PROFILES[0]):
    need(blobs==compose(data,profile) and len(blobs)==20,'closed exact inventory')
    report=BASE.validate(BASE.compose(data),data)
    G3.HISTORICAL.scan(blobs);G3.HISTORICAL.config_review(blobs)
    previous=BASE.compose(data)
    delta={n for n,b in blobs.items() if n not in previous or b!=previous[n]}
    expected_delta={G3.INPUT,OWNER,CLIENT,'public/qrcodegen.js'}
    if profile==PROFILES[0]:expected_delta.add(G3.POLICY)
    need(delta==expected_delta,'bounded delta')
    for n in (G3.SERVICE,G3.CUSTODY,'vercel.json','public/index.html','public/app.js'):
        need(blobs[n]==previous[n],'historical gates/transport bytes')
    for n,b in blobs.items():
        if not n.endswith('.js'):continue
        t=b.decode()
        need(not re.search(r'\bimport\s*\(|\brequire\s*\(|\beval\s*\(|\bconsole\s*\.',t),'dynamic code/logging')
        for declaration in re.findall(r'(?m)^\s*import\b[^;]+;',t):
            literals=re.findall(r"['\"]([^'\"]+)['\"]",declaration);need(len(literals)==1,'import ambiguity')
            target=literals[0]
            if target.startswith('node:'):continue
            need(target.startswith('.'),'external import')
            parts=[]
            for part in (PurePosixPath(n).parent/target).parts:
                if part=='..':need(bool(parts),'import escape');parts.pop()
                elif part!='.':parts.append(part)
            need('/'.join(parts) in blobs,'import closure')
        if n.startswith('public/'):
            need(not re.search(r'lib/server|process\.env|STYTCH_SECRET|session_token|session_jwt|localStorage|sessionStorage|innerHTML',t),'client boundary')
            for v in (data['provider']['project_id'],data['provider']['owner_user_id'],data['provider']['delivery_email'],data['keyset']['source']):
                need(v.encode() not in b,'public identity disclosure')
    need(b'id="recovery"' not in blobs[OWNER],'no recovery display')
    need(b'id="seed" hidden' in blobs[OWNER],'private seed only')
    report.update(profile=profile,files=20,mode='FAKE_DISABLED' if profile==PROFILES[0] else 'D01_DIAGNOSTIC_LIVE_STYTCH',
        deployment_revision=REVISION,vendor_sha256=VENDOR_SHA256,
        changed_runtime_files=sorted(delta),public_assets=sorted(n for n in blobs if n.startswith('public/')),
        zip_sha256=hashlib.sha256(G3.HISTORICAL.frozen_zip(blobs)).hexdigest(),
        files_sha256={n:{'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest(),'source_uid':hashlib.sha1(b).hexdigest()} for n,b in sorted(blobs.items())})
    return report

def build(output,profile=PROFILES[0]):
    output=G3.HISTORICAL.safe_output(output);need(not output.exists(),'fresh output')
    data=G3.generation3_input();blobs=compose(data,profile);report=validate(blobs,data,profile)
    for n,b in blobs.items():
        p=output/'source'/n;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
    (output/'diagnostic-source.zip').write_bytes(G3.HISTORICAL.frozen_zip(blobs))
    (output/'artifact-metadata.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:report[k] for k in ('profile','files','zip_sha256','authority','real_admission_enabled')}));return report

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--profile',choices=PROFILES,default=PROFILES[0]);a=p.parse_args();build(a.output,a.profile)
