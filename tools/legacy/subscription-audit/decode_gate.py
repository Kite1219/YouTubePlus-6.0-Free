import json,re,struct
from pathlib import Path
root=Path('ytplus-analysis/subscription-audit'); b=bytearray((root/'YTLite.dylib').read_bytes()); secs=json.loads((root/'macho.json').read_text())['sections']
def off(a):
 for s in secs:
  if s['addr']<=a<s['addr']+s['size']:return s['offset']+a-s['addr']
 raise ValueError(hex(a))
s=(root/'blocks-output.txt').read_text()
for line in s.splitlines():
 m=re.search(r'(?:DAT_|bRam[0-9]*?)([0-9a-f]{8}) = (?:DAT_|bRam[0-9]*?)([0-9a-f]{8}) \^ (0x[0-9a-f]+|[0-9]+);',line)
 if m:
  dst,src=int(m[1],16),int(m[2],16);b[off(dst)]=b[off(src)]^int(m[3],0)
 m=re.search(r'(?:DAT_|bRam[0-9]*?)([0-9a-f]{8}) = ~(?:DAT_|bRam[0-9]*?)([0-9a-f]{8});',line)
 if m:b[off(int(m[1],16))]=255^b[off(int(m[2],16))]
for a in [0x2314880,0x23148c0,0x2314dc0,0x2314e00,0x2314e40,0x2314e80,0x2314f00,0x2314f40,0x2314fc0]:
 q=struct.unpack_from('<Q',b,off(a)+16)[0]&0xfffffffff
 try:
  p=off(q);end=b.index(0,p);print(hex(a),hex(q),bytes(b[p:end]).decode('utf8','replace'))
 except Exception as e:print(e)
(root/'strings-decoded.bin').write_bytes(b)
