from pathlib import Path
import json,struct,bisect,collections
r=Path('ytplus-analysis/subscription-audit');b=(r/'YTLite.dylib').read_bytes();starts=json.loads((r/'function-starts.json').read_text());metadata=json.loads((r/'objc.json').read_text());owners={}
for c in metadata:
 for kind in ['methods','class_methods']:
  for m in c.get(kind,[]):owners[m['imp']]=c['name']+'.'+m['name']
reverse=collections.defaultdict(set);sites=collections.defaultdict(list)
for i,(w,) in enumerate(struct.iter_unpack('<I',b[0x4000:0x17a4000])):
 if w&0xfc000000!=0x94000000:continue
 p=0x4000+i*4;d=w&0x3ffffff;d-=1<<26 if d&(1<<25) else 0;dest=p+d*4;idx=bisect.bisect_right(starts,p)-1
 if idx>=0:reverse[dest].add(starts[idx]);sites[dest].append(p)
out={}
for getter in [0xc1ddc,0xc2aa4]:
 seen={getter};front={getter}
 for depth in range(5):
  front={caller for target in front for caller in reverse[target]}-seen;seen|=front
 out[hex(getter)]={'direct_call_sites':len(sites[getter]),'functions_reaching_getter_within_5_calls':len(seen)-1,'objc_entry_points':sorted(owners[x] for x in seen if x in owners)}
(r/'feature-getter-coverage.json').write_text(json.dumps(out,indent=2));print(json.dumps({k:{'direct_call_sites':v['direct_call_sites'],'reachable_objc_methods':len(v['objc_entry_points']),'examples':v['objc_entry_points'][:15]} for k,v in out.items()},indent=2))
