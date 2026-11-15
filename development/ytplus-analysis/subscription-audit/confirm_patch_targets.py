from emulate_gate import *
for a in [0xcac80,0xc4b48]:
 e=Emu();res=e.run(a,0);print(hex(a),res)
 touched={x[1] for x in e.writes if x[2]==1}
 data=[]
 for p in sorted(touched):
  if p-1 not in touched:
   raw=bytes(e.read(p+i,1) for i in range(180)).split(b'\0')[0]
   print(hex(p),raw.decode('utf8','backslashreplace'))
