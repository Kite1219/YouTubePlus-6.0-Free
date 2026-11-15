import os, subprocess, shutil, urllib.request, json, hashlib, base64, zipfile
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ARCHIVE=ROOT.parent/'YouTubePlus-development-backup.zip'
external=Path('C:/Users/Kiet/Desktop/Apps/IPAs/21.13.6_YouTubePlus_5.2b4.ipa')
files=sorted(p for p in ROOT.rglob('*') if p.is_file())
manifest=[]
print('Archiving local development data',flush=True)
with zipfile.ZipFile(ARCHIVE,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as z:
    for p in files:
        name='ytplus-analysis/'+p.relative_to(ROOT).as_posix()
        b=p.read_bytes();manifest.append({'path':name,'size':len(b),'sha256':hashlib.sha256(b).hexdigest()});z.writestr(name,b)
    if external.exists():
        b=external.read_bytes();name='inputs/'+external.name
        manifest.append({'path':name,'size':len(b),'sha256':hashlib.sha256(b).hexdigest()});z.writestr(name,b)
    z.writestr('MANIFEST.json',json.dumps(manifest,indent=2))
with zipfile.ZipFile(ARCHIVE) as z:
    assert z.testzip() is None
    for item in manifest:assert hashlib.sha256(z.read(item['path'])).hexdigest()==item['sha256']
env=os.environ.copy();env.update(GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never')
p=subprocess.run([shutil.which('git'),'-c','credential.interactive=never','credential','fill'],input='protocol=https\nhost=github.com\n\n',capture_output=True,text=True,env=env,check=True)
creds=dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line)
headers={'Authorization':'Bearer '+creds['password'],'Accept':'application/vnd.github+json','User-Agent':'YouTubePlus-private-backup'}
def api(path,data=None,method=None,raw=None):
    url=path if path.startswith('https://') else 'https://api.github.com'+path
    h=headers.copy();body=None
    if data is not None:body=json.dumps(data).encode();h['Content-Type']='application/json'
    if raw is not None:body=raw;h['Content-Type']='application/octet-stream'
    with urllib.request.urlopen(urllib.request.Request(url,data=body,headers=h,method=method),timeout=300) as f:return json.load(f)
repo='Kite1219/YouTubePlus-6.0-Free';prefix='/repos/'+repo
assert api(prefix)['private'] is True
release=api(prefix+'/releases/tags/v6.0-test.4')
digest=hashlib.sha256(ARCHIVE.read_bytes()).hexdigest()
asset=next((a for a in release['assets'] if a['name']==ARCHIVE.name),None)
if asset is None:
    print('Uploading full backup archive',flush=True)
    asset=api(release['upload_url'].split('{')[0]+'?name='+ARCHIVE.name,raw=ARCHIVE.read_bytes())
assert asset['size']==ARCHIVE.stat().st_size
if asset.get('digest'):assert asset['digest']=='sha256:'+digest
print('Verifying remote backup bytes',flush=True)
h=headers.copy();h['Accept']='application/octet-stream'
with urllib.request.urlopen(urllib.request.Request(asset['url'],headers=h),timeout=300) as f:
    check=hashlib.sha256();size=0
    while True:
        b=f.read(1024*1024)
        if not b:break
        check.update(b);size+=len(b)
assert check.hexdigest()==digest and size==ARCHIVE.stat().st_size
print('Publishing browsable sources and records',flush=True)
branch=api(prefix)['default_branch'];head=api(prefix+'/git/ref/heads/'+branch)['object']['sha'];commit=api(prefix+'/git/commits/'+head)
tree=[];source_count=0
for p in files:
    if p.suffix.lower() not in {'.py','.rs','.ps1','.java','.md','.json','.txt','.toml'} or p.stat().st_size>200000:continue
    if any(x in p.parts for x in ('extracted','temp','__pycache__')):continue
    if p.name.endswith('-dump.txt') or p.name in ('strings.txt','ghidra-output.txt'):continue
    try:content=p.read_text(encoding='utf-8')
    except UnicodeError:continue
    tree.append({'path':'development/ytplus-analysis/'+p.relative_to(ROOT).as_posix(),'mode':'100644','type':'blob','content':content});source_count+=1
readme='# Development archive\n\nOur local helper sources, tests, package scripts and investigation records are browsable under `ytplus-analysis/`. This is not the original complete YouTube or YouTubePlus source project.\n\nThe release asset `YouTubePlus-development-backup.zip` preserves every local file from the work folder, including original input, extracted libraries, intermediate analysis, and final IPA. It also includes the supplied 5.2b4 reference IPA when available. `MANIFEST.json` records every file hash. Restore the archive into a workspace before running historical scripts. Some scripts contain original absolute Windows paths and require path adjustment, installed Rust/LLVM tools, Python dependencies or Ghidra. Host tests use mocked iOS APIs; on-device PiP remains unverified.\n\nLatest helper: `ytplus-analysis/free-player-audit/PersonalPlayback.rs`. See `manual-pip-test4-notes.md` and `manual-pip-test4-build.json` in the same directory.\n\nBackup SHA-256: `'+digest+'`\n'
tree.extend([{'path':'development/README.md','mode':'100644','type':'blob','content':readme},{'path':'development/MANIFEST.json','mode':'100644','type':'blob','content':json.dumps(manifest,indent=2)+'\n'}])
existing=api(prefix+'/contents/README.md');top=base64.b64decode(existing['content']).decode()
top+='\n## Development and backups\n\nSee [development](development/README.md) for helper sources, tests and records. The release includes a complete, checksummed development backup ZIP.\n'
tree.append({'path':'README.md','mode':'100644','type':'blob','content':top})
newtree=api(prefix+'/git/trees',{'base_tree':commit['tree']['sha'],'tree':tree})
newcommit=api(prefix+'/git/commits',{'message':'Preserve local development sources, tests and complete backup inventory','tree':newtree['sha'],'parents':[head]})
assert api(prefix+'/git/ref/heads/'+branch)['object']['sha']==head
api(prefix+'/git/refs/heads/'+branch,{'sha':newcommit['sha'],'force':False},'PATCH')
remote=api(prefix+'/git/trees/'+newtree['sha']+'?recursive=1');entries={x['path']:x for x in remote['tree']}
for item in tree:
    b=item['content'].encode();blobsha=hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()
    assert entries[item['path']]['sha']==blobsha
assert api(prefix)['private'] is True
# Remove only individually verified snapshot files inside the explicitly named work folder.
deleted=0;count=0
for p in files:
    assert p.resolve().is_relative_to(ROOT.resolve())
    if p.suffix.lower() in {'.ipa','.dylib','.deb','.bin','.dll','.lib','.o','.log','.pyc'} or p.stat().st_size>1000000:
        item=next(i for i in manifest if i['path']=='ytplus-analysis/'+p.relative_to(ROOT).as_posix())
        assert hashlib.sha256(p.read_bytes()).hexdigest()==item['sha256']
        deleted+=p.stat().st_size;p.unlink();count+=1
deleted+=ARCHIVE.stat().st_size;ARCHIVE.unlink()
record={'repository':'https://github.com/'+repo,'release':release['html_url'],'backupAsset':asset['name'],'backupSHA256':digest,'backupBytes':size,'archivedFiles':len(manifest),'browsableSourceFiles':source_count,'verifiedRemoteDownload':True,'deletedLocalFiles':count,'originalLocalBytesFreed':sum(i['size'] for i in manifest if i['path'].startswith('ytplus-analysis/') and not (ROOT/i['path'].removeprefix('ytplus-analysis/')).exists()),'commit':newcommit['sha'],'externalReferenceKept':str(external)}
(ROOT/'storage-cleanup.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
