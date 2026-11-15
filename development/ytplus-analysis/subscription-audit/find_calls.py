import struct,json
from pathlib import Path
r=Path('ytplus-analysis/subscription-audit'); b=(r/'YTLite.dylib').read_bytes(); targets={0xc1a28,0xc1bd8,0xc1ddc,0xbf534,0xcb364}
for t in targets:
 sites=[]
 for p in range(0x4000,0x17a4000,4):
  v=struct.unpack_from('<I',b,p)[0]
  if v&0xfc000000==0x94000000:
   d=v&0x3ffffff;d=d-(1<<26) if d&(1<<25) else d
   if p+d*4==t:sites.append(hex(p))
 print(hex(t),sites)
