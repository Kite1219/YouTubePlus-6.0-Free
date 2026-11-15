import sys
from pathlib import Path
import json,zipfile,struct,plistlib,hashlib,posixpath,collections
r=Path('ytplus-analysis/subscription-audit');p=Path(sys.argv[1]) if len(sys.argv)>1 else Path('ytplus-analysis/YouTubePlus-Personal-6.0-test.2-SideStore.ipa');report={'ipa':str(p.resolve()),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'binaries':[],'missing_dependencies':[]}
def cs(b,p):return b[p:b.index(0,p)].decode('utf8','replace')
def header(b):
 if b[:4]==b'\xca\xfe\xba\xbe':
  n=struct.unpack_from('>I',b,4)[0];entries=[struct.unpack_from('>IIIII',b,8+k*20) for k in range(n)];entry=next((e for e in entries if e[0]==0x100000c),None)
  if not entry:return {'unsupported':'no arm64 slice'}
  b=b[entry[2]:entry[2]+entry[3]]
 if b[:4]!=b'\xcf\xfa\xed\xfe':return None
 o=32;out={'cpu':hex(struct.unpack_from('<I',b,4)[0]),'dependencies':[],'rpaths':[],'encryption':[],'initializers':[]}
 for _ in range(struct.unpack_from('<I',b,16)[0]):
  cmd,size=struct.unpack_from('<II',b,o)
  assert size>=8 and o+size<=len(b)
  if cmd in [0xc,0x80000018,0x8000001f,0x80000023,0x20]:out['dependencies'].append({'name':cs(b,o+struct.unpack_from('<I',b,o+8)[0]),'weak':cmd==0x80000018})
  if cmd==0x8000001c:out['rpaths'].append(cs(b,o+struct.unpack_from('<I',b,o+8)[0]))
  if cmd==0x2c:out['encryption'].append(struct.unpack_from('<III',b,o+8)[2])
  if cmd==0x32:out['minimum_os_raw'],out['sdk_raw']=struct.unpack_from('<II',b,o+12)
  if cmd==0x19:
   n=struct.unpack_from('<I',b,o+64)[0]
   for k in range(n):
    q=o+72+k*80;name=b[q:q+16].split(b'\0')[0].decode();addr,sz=struct.unpack_from('<QQ',b,q+32);off=struct.unpack_from('<I',b,q+48)[0];typ=struct.unpack_from('<I',b,q+64)[0]&255
    if typ==9:out['initializers'].append({'section':name,'address':hex(addr),'size':sz})
  o+=size
 return out
with zipfile.ZipFile(p) as z:
 report['zip_integrity']=z.testzip();names=set(z.namelist());base='Payload/YouTube.app';info=plistlib.loads(z.read(base+'/Info.plist'));exe=base+'/'+info['CFBundleExecutable']
 report['info']={k:info.get(k) for k in ['CFBundleIdentifier','CFBundleShortVersionString','MinimumOSVersion','UIBackgroundModes','UIDeviceFamily']}
 for entry in z.infolist():
  n=entry.filename
  if entry.is_dir() or not (n==exe or n.endswith('.dylib') or '.framework/' in n and '.' not in n.rsplit('/',1)[-1]):continue
  b=z.read(n);h=header(b)
  if not h:continue
  h['path']=n;h['sha256']=hashlib.sha256(b).hexdigest();report['binaries'].append(h)
 for h in report['binaries']:
  loader=posixpath.dirname(h['path']);rp=[base+'/Frameworks',base,loader]
  for dep in h.get('dependencies',[]):
   name=dep['name']
   if name.startswith(('/System/Library/','/usr/lib/')):continue
   candidates=[]
   if name.startswith('@rpath/'):candidates=[x+'/'+name[7:] for x in rp]
   elif name.startswith('@executable_path/'):candidates=[base+'/'+name[len('@executable_path/'):]]
   elif name.startswith('@loader_path/'):candidates=[loader+'/'+name[len('@loader_path/'):]]
   else:candidates=[name]
   if not any(posixpath.normpath(c) in names for c in candidates):
    target_list='system_swift_runtime_references' if name.startswith('@rpath/libswift') and '/usr/lib/swift' in h.get('rpaths',[]) else 'missing_dependencies'
    report.setdefault(target_list,[]).append({'loader':h['path'],'dependency':name,'weak':dep['weak']})
 report['pip_named_artifacts']=[x for x in names if 'youpip' in x.lower()]
 report['main_directly_loads_yltite']=any(x['name'].endswith('/YTLite.dylib') for h in report['binaries'] if h['path']==exe for x in h['dependencies'])
(r/(sys.argv[2] if len(sys.argv)>2 else 'package-dependency-audit-test3.json' if len(sys.argv)>1 else 'package-dependency-audit.json')).write_text(json.dumps(report,indent=2))
print(json.dumps({k:v for k,v in report.items() if k!='binaries'},indent=2));print('ARM64 binaries inspected',len(report['binaries']));print('Encrypted binaries',[(x['path'],x['encryption']) for x in report['binaries'] if any(x.get('encryption',[]))])
