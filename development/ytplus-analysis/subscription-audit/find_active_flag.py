import json,struct,bisect
from pathlib import Path
r=Path('ytplus-analysis/subscription-audit');m=json.loads((r/'macho.json').read_text());b=(r/'YTLite.dylib').read_bytes();starts=json.loads((r/'function-starts.json').read_text())
for s in m['sections']:
 if s['sectname']=='__mod_init_func':print('INIT',[(hex(s['addr']+k),hex(struct.unpack_from('<Q',b,s['offset']+k)[0]&0xfffffffff)) for k in range(0,s['size'],8)])
regs={};found=[]
for p in range(0x4000,0x17a4000,4):
 v=struct.unpack_from('<I',b,p)[0]
 if v&0x9f000000==0x90000000:
  imm=((v>>5)&0x7ffff)*4+((v>>29)&3);imm-=1<<21 if imm&(1<<20) else 0;regs[v&31]=((p&~4095)+(imm<<12),p)
 elif v&0xffc00000 in [0x39400000,0x39000000]:
  rn=(v>>5)&31;delta=(v>>10)&4095
  if rn in regs and p-regs[rn][1]<48:
   addr=regs[rn][0]+delta
   if addr in [0x2363040,0x2363041]:found.append({'site':hex(p),'address':hex(addr),'op':'load' if v&0x400000 else 'store','function':hex(starts[bisect.bisect_right(starts,p)-1])})
print(json.dumps(found,indent=2));(r/'active-flag-references.json').write_text(json.dumps(found,indent=2))
