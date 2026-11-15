from pathlib import Path
import zipfile,hashlib,json,copy,re
r=Path('ytplus-analysis/free-player-audit');src=Path('ytplus-analysis/YouTubePlus-Personal-6.0-test.3-YouPiP.ipa');out=src.with_name('YouTubePlus-Personal-6.0-test.4-ManualPiP.ipa')
if not src.exists():
 import runpy;runpy.run_path(str(r/'package_integrated.py'),run_name='__main__')
helper=(r/'PersonalPlayback.dylib').read_bytes();lib='Payload/YouTube.app/Frameworks/PersonalPlayback.dylib'
old_source=(r/'PersonalPlayback-test3.rs').read_text();new_source=(r/'PersonalPlayback.rs').read_text()
pattern=r'#\[unsafe\(no_mangle\)\]pub unsafe extern "C" fn personal_background.*?(?=unsafe extern "C" fn pip_disabled)'
assert re.search(pattern,old_source,re.S)[0]==re.search(pattern,new_source,re.S)[0]
with zipfile.ZipFile(src) as z,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=False) as dest:
 for entry in z.infolist():dest.writestr(copy.copy(entry),helper if entry.filename==lib else z.read(entry))
with zipfile.ZipFile(src) as z,zipfile.ZipFile(out) as dest:
 assert dest.testzip() is None;assert z.namelist()==dest.namelist();unchanged=0
 for name in z.namelist():
  expected=helper if name==lib else z.read(name);assert dest.read(name)==expected
  if name!=lib:unchanged+=1
report={'output':str(out.resolve()),'size':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'base_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'helper_sha256':hashlib.sha256(helper).hexdigest(),'changed_members':[lib],'unchanged_members':unchanged,'background_hook_source_unchanged':True,'checks':['ZIP CRC passed','Member-by-member comparison passed','28 production-code host tests passed with mocked UIKit/Foundation','Exact no-argument appWillResignActive selector and type confirmed in current YouTube metadata'],'runtime_device_tested':False,'behavior':'Manual-button mode suppresses automatic PiP; button requests AVKit start/stop when possible, otherwise guarded fallback','limits':['Actual phone PiP activation remains unverified','No unconditional override of canEnablePictureInPicture or platform pictureInPicturePossible','A requested start is not proof of successful PiP activation'],'diagnostics':'PersonalPlaybackLastPiPResult in standard preferences records the most recent manual action path without URLs or account data'}
(r/'manual-pip-test4-build.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
