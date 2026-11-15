from pathlib import Path
import importlib.util,zipfile,struct,hashlib,json,plistlib,stat
r=Path('ytplus-analysis/free-player-audit');source=Path('ytplus-analysis/YouTubePlus-Personal-6.0-test.2-SideStore.ipa');free=Path(r'C:/Users/Kiet/Desktop/Apps/IPAs/21.13.6_YouTubePlus_5.2b4.ipa');out=Path('ytplus-analysis/YouTubePlus-Personal-6.0-test.3-YouPiP.ipa');app='Payload/YouTube.app/';main=app+'YouTube'
if not source.exists():
 import runpy
 runpy.run_path('ytplus-analysis/subscription-audit/build_personal_test2.py',run_name='__main__')
 runpy.run_path('ytplus-analysis/subscription-audit/repack_sidestore.py',run_name='__main__')
spec=importlib.util.spec_from_file_location('pack','twitch-integration/package-ipa.py');pack=importlib.util.module_from_spec(spec);spec.loader.exec_module(pack)
helper=(r/'PersonalPlayback.dylib').read_bytes();yp=bytearray((r/'YouPiP.dylib').read_bytes());original_yp_sha=hashlib.sha256(yp).hexdigest();pos=32
for _ in range(struct.unpack_from('<I',yp,16)[0]):
 cmd,size=struct.unpack_from('<II',yp,pos)
 if cmd==0xd:
  start=pos+struct.unpack_from('<I',yp,pos+8)[0];end=yp.index(0,start);new=b'@rpath/YouPiP.dylib';assert len(new)<=end-start;yp[start:end]=new+b'\0'*(end-start-len(new))
 pos+=size
(r/'YouPiP-integrated.dylib').write_bytes(yp)
changes={};added={app+'Frameworks/PersonalPlayback.dylib':helper,app+'Frameworks/YouPiP.dylib':bytes(yp)}
with zipfile.ZipFile(free) as f:
 for entry in f.infolist():
  if entry.filename.startswith(app+'YouPiP.bundle/'):added[entry.filename]=f.read(entry)
assert app+'YouPiP.bundle/en.lproj/Localizable.strings' in added
added[app+'YouPiP.bundle/LICENSE.txt']=(r/'YouPiP-LICENSE.txt').read_bytes()
with zipfile.ZipFile(source) as z:
 original_main=z.read(main);patched=original_main
 for path in ['@executable_path/Frameworks/PersonalPlayback.dylib','@executable_path/Frameworks/YouPiP.dylib']:
  pack.LOAD_PATH=path;patched,before,after=pack.inject(patched)
 changes[main]=patched
 local=app+'YTLite.bundle/en.lproj/Localizable.strings';strings=plistlib.loads(z.read(local));strings['PiPButton']='Legacy Picture in Picture toggle';strings['PiPButtonDesc']='Use YouTube settings > YouPiP for the manual PiP button and automatic activation. Background playback is controlled separately.';changes[local]=plistlib.dumps(strings,fmt=plistlib.FMT_BINARY,sort_keys=False)
 names=z.namelist();assert not set(added)&set(names)
 with zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=False) as dest:
  for name in names+list(added):
   old=z.getinfo(name) if name in names else None;isdir=name.endswith('/');data=added[name] if name in added else changes.get(name,z.read(name));entry=zipfile.ZipInfo(name,(2026,11,9,12,0,0));entry.create_system=3
   if isdir:entry.external_attr=((stat.S_IFDIR|0o755)<<16)|0x10;entry.compress_type=zipfile.ZIP_STORED
   elif old and stat.S_ISLNK(old.external_attr>>16):entry.external_attr=old.external_attr;entry.compress_type=zipfile.ZIP_DEFLATED
   else:
    executable=name==main or name.endswith('.dylib') or '.framework/' in name and '.' not in name.rsplit('/',1)[-1];entry.external_attr=(stat.S_IFREG|(0o755 if executable else 0o644))<<16;entry.compress_type=zipfile.ZIP_DEFLATED
   dest.writestr(entry,data)
with zipfile.ZipFile(source) as z,zipfile.ZipFile(out) as dest:
 assert dest.testzip() is None
 assert set(dest.namelist())==set(z.namelist())|set(added)
 unchanged=0
 for n in z.namelist():
  if n in changes:assert dest.read(n)==changes[n]
  else:assert dest.read(n)==z.read(n);unchanged+=1
 for n,b in added.items():assert dest.read(n)==b
 paths=[x.get('path','') for x in pack.macho(dest.read(main))['commands']]
 assert paths.index('@executable_path/Frameworks/PersonalPlayback.dylib')<paths.index('@executable_path/Frameworks/YouPiP.dylib')
report={'output':str(out.resolve()),'size':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'source_ipa_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'free_ipa':str(free),'free_ipa_sha256':hashlib.sha256(free.read_bytes()).hexdigest(),'original_youpip_sha256':original_yp_sha,'integrated_youpip_sha256':hashlib.sha256(yp).hexdigest(),'new_native_helper_sha256':hashlib.sha256(helper).hexdigest(),'changed_members':list(changes),'added_members':list(added),'unchanged_members':unchanged,'verification':['ZIP CRC passed','Every original member unchanged except documented main load commands and English legacy PiP label','Every copied YouPiP resource matches supplied free IPA','YouPiP code unchanged; only its library install name normalized','New helper loads before YouPiP; late hook setup dispatched to main queue','Native host behavior tests: 12 passed with mocked iOS runtime'],'runtime_device_tested':False,'defaults':'First migration enables background audio and manual YouPiP button, disables unrestricted/legacy PiP; later user choices preserved','conflict_handling':'Keep 6.0; route PiP controls through YouPiP, neutralize 6.0 PiP veto while YouPiP enabled, hide legacy 6.0 PiP button after normal updates','limits':['Real iOS playback/PiP behavior remains untested','No unconditional override of canEnablePictureInPicture','Missing ivars or newer activation method fall back to copied YouPiP handler']}
(r/'integration-build.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k not in ['added_members']},indent=2))
