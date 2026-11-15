from pathlib import Path
import zipfile,plistlib,hashlib,importlib.util,json,re
r=Path('ytplus-analysis/free-player-audit');r.mkdir(exist_ok=True)
spec=importlib.util.spec_from_file_location('ma','twitch-integration/native-audit/audit.py');ma=importlib.util.module_from_spec(spec);spec.loader.exec_module(ma)
p=Path(r'C:/Users/Kiet/Desktop/Apps/IPAs/21.13.6_YouTubePlus_5.2b4.ipa')
with zipfile.ZipFile(p) as z:
 print('YouPiP RESOURCES',[n for n in z.namelist() if 'youpip' in n.lower()][:35])
 for name in ['Payload/YouTube.app/Frameworks/YouPiP.dylib','Payload/YouTube.app/Frameworks/YTLite.dylib']:
  b=z.read(name);q=r/(Path(name).name if 'YouPiP' in name else 'YTLite-free.dylib');q.write_bytes(b);m=ma.macho(b);q.with_suffix('.json').write_text(json.dumps(m,indent=2));print(name,len(b),m['sha256']);print([c for c in m['commands'] if c['type'] in ['0xc','0xd','0x8000001c']])
  if 'YouPiP' in name:
   for x in re.findall(rb'[\x20-\x7e]{5,}',b):
    s=x.decode()
    if re.search(r'1\.12|pip|background|button',s,re.I) and not s.startswith(('v','T@')):print(s[:180])
 for n in z.namelist():
  if 'youpip' in n.lower() and n.endswith(('Info.plist','en.lproj/Localizable.strings')):
   try:print(n,plistlib.loads(z.read(n)))
   except:pass
