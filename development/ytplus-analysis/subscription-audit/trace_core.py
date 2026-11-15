from emulate_gate import *
starts=json.loads((R/'function-starts.json').read_text());out=[]
for a in starts:
 if not 0xb0000<=a<0xe7000:continue
 for stub in [0,1]:
  e=Emu();result=e.run(a,stub,5000)
  out.append({'start':hex(a),'stub':stub,'result':result,'calls':e.calls,'writes':len(e.writes)})
(R/'core-traces.json').write_text(json.dumps(out,indent=2))
for row in out:
 print(row['start'],row['stub'],row['result'])
 for call in row['calls']:
  if any(any(k.lower() in arg.lower() for k in ['jwt','login','access','device','http','request','notactivated','subscription','refresh']) for arg in call[2]):print(' ',call)
