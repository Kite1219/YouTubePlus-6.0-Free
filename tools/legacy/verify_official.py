import zipfile,plistlib,hashlib,json
from pathlib import Path
p=Path('ytplus-analysis/YouTubePlus_6.0_YouTube_21.43.5_official.ipa')
with zipfile.ZipFile(p) as z:
 assert z.testzip() is None
 n=next(n for n in z.namelist() if n.startswith('Payload/') and n.count('/')==2 and n.endswith('/Info.plist'))
 info=plistlib.loads(z.read(n)); app=n[:-len('Info.plist')]
 bundles=[n for n in z.namelist() if n.endswith('YTLite.bundle/Info.plist')]
 print(json.dumps({'size':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'version':info.get('CFBundleShortVersionString'),'minimum_ios':info.get('MinimumOSVersion'),'bundle_id':info.get('CFBundleIdentifier'),'tweak_libraries':[n for n in z.namelist() if n.endswith('YTLite.dylib')],'bundle_metadata':[plistlib.loads(z.read(n)) for n in bundles],'zip_integrity':'passed'},indent=2))
 assert info.get('CFBundleShortVersionString')=='21.43.5'
 assert p.stat().st_size==149520411
