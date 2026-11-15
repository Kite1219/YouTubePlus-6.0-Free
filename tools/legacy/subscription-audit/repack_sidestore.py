from pathlib import Path
import zipfile,stat,json,hashlib,plistlib
r=Path('ytplus-analysis/subscription-audit');src=Path('ytplus-analysis/YouTubePlus-Personal-6.0-test.2-unsigned.ipa');out=src.with_name('YouTubePlus-Personal-6.0-test.2-SideStore.ipa');changed=[]
with zipfile.ZipFile(src) as old:
 info=plistlib.loads(old.read('Payload/YouTube.app/Info.plist'));main='Payload/YouTube.app/'+info['CFBundleExecutable']
 with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=False) as new:
  for entry in old.infolist():
   name=entry.filename;assert name.startswith('Payload/') and '..' not in Path(name).parts
   fresh=zipfile.ZipInfo(name,date_time=(2026,11,9,12,0,0));fresh.create_system=3;fresh.extra=b'';fresh.comment=b''
   if entry.is_dir():fresh.external_attr=((stat.S_IFDIR|0o755)<<16)|0x10;fresh.compress_type=zipfile.ZIP_STORED
   elif stat.S_ISLNK(entry.external_attr>>16):fresh.external_attr=entry.external_attr;fresh.compress_type=zipfile.ZIP_DEFLATED
   else:
    executable=name==main or name.endswith('.dylib') or '.framework/' in name and '.' not in name.rsplit('/',1)[-1]
    mode=(stat.S_IFREG|(0o755 if executable else 0o644));fresh.external_attr=mode<<16;fresh.compress_type=zipfile.ZIP_DEFLATED
   if fresh.external_attr!=entry.external_attr:changed.append({'file':name,'old_mode':oct(entry.external_attr>>16),'new_mode':oct(fresh.external_attr>>16)})
   new.writestr(fresh,old.read(entry))
with zipfile.ZipFile(src) as old,zipfile.ZipFile(out) as new:
 assert new.testzip() is None
 assert old.namelist()==new.namelist()
 for n in old.namelist():assert old.read(n)==new.read(n),n
 assert all(e.compress_type in [0,8] and e.extract_version==20 and not e.extra for e in new.infolist())
report={'output':str(out.resolve()),'bytes':out.stat().st_size,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'previous_archive_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'same_app_file_contents':True,'zip_crc_passed':True,'zip64':False,'compression':'standard DEFLATE for files; stored directories','metadata':'fresh ZIP headers without extra fields; executable permissions normalized','permission_changes':changed,'sidestore_tested':False,'diagnosis':'Original local ZIP was valid; repackaging is a compatibility trial, not a confirmed fix for an unobserved phone/download failure'}
(r/'sidestore-repack.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:v for k,v in report.items() if k!='permission_changes'},indent=2));print('Permission changes',len(changed))
