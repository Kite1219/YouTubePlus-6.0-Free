from pathlib import Path
import json,struct,zipfile,hashlib,plistlib
r=Path('ytplus-analysis/subscription-audit');src=Path('ytplus-analysis/YouTubePlus_6.0_YouTube_21.43.5_official.ipa');out=Path('ytplus-analysis/YouTubePlus-Personal-6.0-test.2-unsigned.ipa')
expected='aec278e47289639a7dc8b22cc4257df9b9f75336d6e187dd82da0d981c1ae59c'
member='Payload/YouTube.app/Frameworks/YTLite.dylib'
original=(r/'YTLite.dylib').read_bytes();assert hashlib.sha256(original).hexdigest()==expected
b=bytearray(original);patches=[]
def patch(a,words,purpose):
 new=b''.join(struct.pack('<I',w) for w in words);old=bytes(b[a:a+len(new)]);assert old==original[a:a+len(new)];b[a:a+len(new)]=new
 patches.append({'address':hex(a),'file_offset':a,'original':old.hex(),'replacement':new.hex(),'purpose':purpose})
patch(0xc24bc,[0x52800020,0xd65f03c0],'Local feature eligibility always true; feature preference values are still read normally')
patch(0xc23e0,[0x52800008],'Boolean preferences ignore the remote-access error flag and keep the saved value')
patch(0xc3110,[0x52800008],'Numeric preferences ignore the remote-access error flag and keep the saved value')
patch(0xc1bd8,[0xd2800000,0xd65f03c0],'Do not load a third-party membership JWT or linked-device credential')
patch(0xc4b48,[0xd2800000,0xd65f03c0],'Disable the membership fetch-token client; return no membership response without networking')
patch(0xcac80,[0xd65f03c0],'Disable the access/subscription reminder presenter')
patch(0x34b38c,[0xaa1f03e2],'Clear the now-empty membership section header')
patch(0x34b3e8,[0xd503201f],'Do not populate the membership section with status/login/device controls')
libout=r/'YTLite-Personal.dylib';libout.write_bytes(b)
source_hash=hashlib.sha256(src.read_bytes()).hexdigest();removed=[]
with zipfile.ZipFile(src) as z,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as dest:
 assert z.read(member)==original
 for entry in z.infolist():
  if '/_CodeSignature/' in entry.filename or entry.filename.endswith('/embedded.mobileprovision'):
   removed.append(entry.filename);continue
  dest.writestr(entry,bytes(b) if entry.filename==member else z.read(entry))
with zipfile.ZipFile(src) as z,zipfile.ZipFile(out) as dest:
 assert dest.testzip() is None
 assert set(dest.namelist())==set(z.namelist())-set(removed)
 for entry in dest.infolist():assert dest.read(entry)==(bytes(b) if entry.filename==member else z.read(entry.filename))
 info=plistlib.loads(dest.read('Payload/YouTube.app/Info.plist'))
report={'build':'YouTubePlus Personal 6.0-test.2','output':str(out.resolve()),'size':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_sha256':source_hash,'original_library_sha256':expected,'patched_library_sha256':hashlib.sha256(b).hexdigest(),'youtube_version':info.get('CFBundleShortVersionString'),'bundle_id':info.get('CFBundleIdentifier'),'patches':patches,'removed_stale_signing_files':removed,'checks':['Exact original embedded library SHA-256 matched','ZIP integrity passed','All retained members byte-identical except YTLite.dylib','Original input IPA unchanged'],'runtime_tested':False,'limits':['Requires signing before installation','iPhone/iPad launch and feature behavior require device testing','Obfuscated binary may have additional integrity or subscription paths not covered by static tracing']}
assert hashlib.sha256(src.read_bytes()).hexdigest()==source_hash
(r/'personal-build-test2.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['patches','removed_stale_signing_files']},indent=2))
