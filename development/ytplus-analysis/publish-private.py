import os, subprocess, shutil, urllib.request, urllib.error, json, hashlib, base64
from pathlib import Path
ROOT=Path(__file__).resolve().parent
ipa=ROOT/'YouTubePlus-Personal-6.0-test.4-ManualPiP.ipa'
expected='4ad31f12f9008ad233cbfadc59e4a0796133d88fec7957a545d6daf627b19044'
assert hashlib.sha256(ipa.read_bytes()).hexdigest()==expected
env=os.environ.copy();env.update(GIT_TERMINAL_PROMPT='0',GCM_INTERACTIVE='never')
p=subprocess.run([shutil.which('git'),'-c','credential.interactive=never','credential','fill'],input='protocol=https\nhost=github.com\n\n',capture_output=True,text=True,env=env,check=True)
creds=dict(line.split('=',1) for line in p.stdout.splitlines() if '=' in line)
headers={'Authorization':'Bearer '+creds['password'],'Accept':'application/vnd.github+json','User-Agent':'YouTubePlus-private-release'}
def api(path,data=None,method=None,raw=None):
    url=path if path.startswith('https://') else 'https://api.github.com'+path
    h=headers.copy();body=None
    if data is not None:body=json.dumps(data).encode();h['Content-Type']='application/json'
    if raw is not None:body=raw;h['Content-Type']='application/octet-stream'
    with urllib.request.urlopen(urllib.request.Request(url,data=body,headers=h,method=method),timeout=300) as f:return json.load(f)
owner=api('/user')['login'];name='YouTubePlus-6.0-Free';repo=owner+'/'+name
try:r=api('/repos/'+repo)
except urllib.error.HTTPError as e:
    if e.code!=404:raise
    r=api('/user/repos',{'name':name,'private':True,'auto_init':True,'description':'Private personal YouTubePlus 6.0 build based on YouTube 21.43.5.'})
assert r['private'] is True,'Repository must be private before upload'
readme='# Youtube Plus 6.0 Free\n\nPrivate personal build based on YouTubePlus 6.0 / YouTube 21.43.5.\n\nDownload the IPA from Releases and sign it using your own sideloading setup.\n\nLatest package: test.4 (Manual PiP). Preserves working background audio and corrects manual PiP activation and automatic-entry guards. Package integrity and 28 mocked host tests passed; actual device PiP behavior remains unverified.\n'
current=api('/repos/'+repo+'/contents/README.md')
if base64.b64decode(current['content']).decode()!=readme:
    api('/repos/'+repo+'/contents/README.md',{'message':'Describe private YouTubePlus personal build','content':base64.b64encode(readme.encode()).decode(),'sha':current['sha']},'PUT')
tag='v6.0-test.4'
try:release=api('/repos/'+repo+'/releases/tags/'+tag)
except urllib.error.HTTPError as e:
    if e.code!=404:raise
    release=api('/repos/'+repo+'/releases',{'tag_name':tag,'name':'Youtube Plus 6.0 Free','body':'Private personal build: YouTubePlus 6.0 on YouTube 21.43.5.\n\n- Preserves background audio.\n- Corrects manual PiP button activation and suppresses automatic PiP in button-only mode.\n- ZIP integrity, member comparison and 28 mocked production-code host tests passed.\n\nOn-device PiP remains unverified. Unsigned IPA: sign with your own sideloading setup.\n\nSHA-256: `'+expected+'`','draft':False,'prerelease':False,'make_latest':'true'})
assetname='YouTubePlus-6.0-Free-test.4.ipa'
asset=next((a for a in release['assets'] if a['name']==assetname),None)
if asset is None:
    print('Uploading IPA to verified private repository',flush=True)
    asset=api(release['upload_url'].split('{')[0]+'?name='+assetname,raw=ipa.read_bytes())
assert asset['size']==ipa.stat().st_size
if asset.get('digest'):assert asset['digest']=='sha256:'+expected
# Independently download authenticated release asset and verify its bytes.
print('Verifying uploaded IPA checksum',flush=True)
h=headers.copy();h['Accept']='application/octet-stream'
with urllib.request.urlopen(urllib.request.Request(asset['url'],headers=h),timeout=300) as f:
    digest=hashlib.sha256();size=0
    while True:
        chunk=f.read(1024*1024)
        if not chunk:break
        digest.update(chunk);size+=len(chunk)
assert digest.hexdigest()==expected and size==ipa.stat().st_size
assert api('/repos/'+repo)['private'] is True
record={'repository':r['html_url'],'private':True,'release':release['html_url'],'title':release['name'],'asset':assetname,'sha256':expected,'verifiedDownload':True}
(ROOT/'private-release.json').write_text(json.dumps(record,indent=2)+'\n')
print(json.dumps(record),flush=True)
