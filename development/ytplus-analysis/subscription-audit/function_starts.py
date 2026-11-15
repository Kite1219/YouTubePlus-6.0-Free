from emulate_gate import *
cmd=next(x for x in json.loads((R/'macho.json').read_text())['commands'] if x['type']=='0x26');raw=B[cmd['dataoff']:cmd['dataoff']+cmd['datasize']];starts=[];a=0;v=0;shift=0
for byte in raw:
 v|=(byte&127)<<shift
 if byte&128:shift+=7
 else:
  if not v:break
  a+=v;starts.append(a);v=0;shift=0
(R/'function-starts.json').write_text(json.dumps(starts))
for a in starts:
 if 0xc1800<a<0xc3500 or 0xcf800<a<0xcfa00 or 0xd9800<a<0xd9c00 or 0xdb000<a<0xdb300:print(hex(a))
