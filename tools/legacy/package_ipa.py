from pathlib import Path
import zipfile,struct,hashlib,json,plistlib
root=Path('ytplus-analysis')
base=Path(r'C:/Users/Kiet/Desktop/Apps/IPAs/21.13.6_YouTubePlus_5.2b4.ipa')
lib=root/'extracted/Library/MobileSubstrate/DynamicLibraries/YTLite.dylib'
bundle=root/'extracted/Library/Application Support/YTLite.bundle'
out=root/'YouTubePlus_6.0_YouTube_21.13.6_unsigned.ipa'
b=bytearray(lib.read_bytes()); assert b[:4]==b'\xcf\xfa\xed\xfe'
ncmds=struct.unpack_from('<I',b,16)[0]; off=32; changes=[]
for _ in range(ncmds):
 cmd,size=struct.unpack_from('<II',b,off)
 if cmd in (0xc,0xd,0x18,0x80000018,0x8000001f,0x80000023):
  pos=off+struct.unpack_from('<I',b,off+8)[0]
  end=b.index(0,pos); name=bytes(b[pos:end]).decode()
  replacement=None
  if name=='/Library/Frameworks/CydiaSubstrate.framework/CydiaSubstrate': replacement='@rpath/CydiaSubstrate.framework/CydiaSubstrate'
  if cmd==0xd: replacement='@rpath/YTLite.dylib'
  if replacement and replacement!=name:
   new=replacement.encode(); assert len(new)<=end-pos
   b[pos:end]=new+b'\x00'*(end-pos-len(new)); changes.append([name,replacement])
 off+=size
assert any('CydiaSubstrate' in x[0] for x in changes)
app='Payload/YouTube.app/'
with zipfile.ZipFile(base) as src,zipfile.ZipFile(out,'w',zipfile.ZIP_DEFLATED,compresslevel=6) as dst:
 for entry in src.infolist():
  n=entry.filename
  if n.startswith(app+'YTLite.bundle/') or n==app+'Frameworks/YTLite.dylib' or n.startswith(app+'_CodeSignature/'): continue
  dst.writestr(entry,src.read(n))
 dst.writestr(app+'Frameworks/YTLite.dylib',bytes(b))
 for p in bundle.rglob('*'):
  if p.is_file(): dst.write(p,app+'YTLite.bundle/'+p.relative_to(bundle).as_posix())
with zipfile.ZipFile(out) as z:
 assert z.testzip() is None
 assert z.read(app+'Frameworks/YTLite.dylib')==bytes(b)
 info=plistlib.loads(z.read(app+'Info.plist'))
 for p in bundle.rglob('*'):
  if p.is_file(): assert z.read(app+'YTLite.bundle/'+p.relative_to(bundle).as_posix())==p.read_bytes()
report={'output':str(out.resolve()),'base':str(base),'youtube_version':info.get('CFBundleShortVersionString'),'tweak_version':'6.0','dependency_path_changes':changes,'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'size':out.stat().st_size,'verification':'ZIP integrity and byte-for-byte replacement checks passed','limits':['Unsigned; sign before installing','YouTube 21.13.6 compatibility with tweak 6.0 is not runtime tested','Existing optional tweaks retained','Subscription checks intact']}
(root/'build-result.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
