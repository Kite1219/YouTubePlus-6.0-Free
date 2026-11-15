from pathlib import Path
import tarfile, io, re
p=Path('ytplus-analysis/ytplus-6.0.deb').read_bytes()
i=8
out=Path('ytplus-analysis/extracted'); out.mkdir(exist_ok=True)
while i+60<=len(p):
 h=p[i:i+60]; n=h[:16].decode().strip(); s=int(h[48:58]); d=p[i+60:i+60+s]
 print(n,s)
 if n.startswith('data.tar'):
  t=tarfile.open(fileobj=io.BytesIO(d)); t.extractall(out,filter='data')
 i+=60+s+(s%2)
for f in out.rglob('*'):
 if f.is_file() and (f.suffix in ('.dylib','.plist') or not f.suffix): print(f)
strings=[]
for f in out.rglob('*.dylib'):
 ss=[x.decode('utf-8','replace') for x in re.findall(rb'[\x20-\x7e]{5,}',f.read_bytes())]
 strings.extend(ss)
 Path('ytplus-analysis/strings.txt').write_text('\n'.join(ss),encoding='utf-8')
 print('BINARY',f,'STRINGS',len(ss))
 for x in ss:
  if re.search(r'duo|fold|floating|watermark|safeArea|traitCollection|horizontalSizeClass|screenSize',x,re.I): print(x[:500])
