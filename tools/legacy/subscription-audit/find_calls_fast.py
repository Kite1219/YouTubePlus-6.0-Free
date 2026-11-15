import struct,json
from pathlib import Path
r=Path('ytplus-analysis/subscription-audit');b=(r/'YTLite.dylib').read_bytes(); targets={0xc24bc,0xc1a28,0xc1bd8,0xcb364};calls={t:[] for t in targets}
for idx,(v,) in enumerate(struct.iter_unpack('<I',b[0x4000:0x17a4000])):
 if v&0xfc000000==0x94000000:
  p=0x4000+idx*4;d=v&0x3ffffff;d=d-(1<<26) if d&(1<<25) else d;t=p+d*4
  if t in calls:calls[t].append(hex(p))
print(json.dumps({hex(k):v for k,v in calls.items()},indent=2))
for c in json.loads((r/'objc.json').read_text()):
 if c['name'] in ['YTLUserDefaults','YTPSettingsBuilder']:
  print(c['name'])
  for m in c['methods']:
   if c['name']=='YTLUserDefaults' or any(x in m['name'].lower() for x in ['patreon','build','account','view','section']):print(m['name'],m['imp_hex'])
