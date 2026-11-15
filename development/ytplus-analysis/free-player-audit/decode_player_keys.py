import sys;sys.path.insert(0,'ytplus-analysis/subscription-audit');from emulate_gate import *
for a,i in re.findall(r'GateDump.java> ([0-9a-f]{8}) (.*?) \(GhidraScript\)',(R/'player-integration-dump.txt').read_text()):D[int(a,16)]=i.strip()
e=Emu();e.r={'sp':0x70000000}
for pc in sorted(x for x in D if 0x1a80f0<=x<0x1ba720):
 if D[pc].split()[0] in ['b','br','blr','ret','cbz','cbnz','tbz','tbnz'] or D[pc].startswith('b.'):continue
 e.run(pc,limit=1,reset=False)
touched={a for _,a,n,_ in e.writes if n==1 and 0x2200000<=a<0x2360000}
for a in sorted(touched):
 if a-1 in touched:continue
 raw=bytes(e.read(a+i,1) for i in range(90)).split(b'\0')[0]
 try:s=raw.decode('utf8')
 except:continue
 if 'pip' in s.lower():
  refs=[hex(p-16) for p in range(0x22b0000,0x22b7000,8) if e.read(p,8)==a];print(hex(a),s,refs)
