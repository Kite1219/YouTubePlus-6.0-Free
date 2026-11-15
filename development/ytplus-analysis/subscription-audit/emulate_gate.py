import re,json,struct
from pathlib import Path
R=Path('ytplus-analysis/subscription-audit')
B=(R/'YTLite.dylib').read_bytes();S=json.loads((R/'macho.json').read_text())['sections'];D={}
for f in ['core-dump.txt','wrappers-dump.txt','gate-dump.txt','middle-dump.txt','wrappers2-dump.txt']:
 for a,i in re.findall(r'GateDump.java> ([0-9a-f]{8}) (.*?) \(GhidraScript\)',(R/f).read_text()):D[int(a,16)]=i.strip()
class Emu:
 def __init__(self):self.r={};self.mem={};self.flags=(0,0,32);self.calls=[];self.writes=[];self.pc=0
 def reg(self,x):
  if x in ['xzr','wzr']:return 0
  if x.startswith('#'):return int(x[1:],0)
  if x.startswith('0x'):return int(x,16)
  return self.r.get(x.replace('w','x',1) if x.startswith('w') else x,0)&((1<<(32 if x.startswith('w') else 64))-1)
 def put(self,x,v):
  if x in ['xzr','wzr']:return
  self.r[x.replace('w','x',1) if x.startswith('w') else x]=v&((1<<(32 if x.startswith('w') else 64))-1)
 def read(self,a,n):
  q=[]
  for k in range(n):
   if a+k in self.mem:q.append(self.mem[a+k]);continue
   s=next((s for s in S if s['addr']<=a+k<s['addr']+s['size']),None)
   q.append(B[s['offset']+a+k-s['addr']] if s and s.get('offset') else 0)
  v=int.from_bytes(bytes(q),'little')
  if n==8 and v>>48 in [0x10,0x20,0x30,0x40,0x50,0x60,0x70,0x80,0x90,0xa0,0xb0,0xc0,0xd0,0xe0,0xf0,0x100,0x200,0x300,0x400]:v&=0xfffffffff
  return v
 def write(self,a,n,v):
  for k in range(n):self.mem[a+k]=(v>>(k*8))&255
  if a<0x4000000:self.writes.append((self.pc,a,n,v))
 def addr(self,op):
  q=op.strip('[]').split(',');a=self.reg(q[0]);
  if len(q)>1:
   v=self.reg(q[1].strip())
   if len(q)>2:
    ext=q[2].strip();shift=int(ext.split('#')[1],0) if '#' in ext else 0
    if ext.startswith('SXTW'):v=struct.unpack('<i',struct.pack('<I',v&0xffffffff))[0]
    v<<=shift
   a+=v
  return a
 def cond(self,c):
  a,b,w=self.flags;mask=(1<<w)-1;sg=lambda v:v-(1<<w) if v>>(w-1)&1 else v
  return {'eq':a==b,'ne':a!=b,'lt':sg(a)<sg(b),'le':sg(a)<=sg(b),'gt':sg(a)>sg(b),'ge':sg(a)>=sg(b),'lo':a<b,'hs':a>=b,'hi':a>b,'ls':a<=b}.get(c,False)
 def describe(self,a):
  try:
   if 0x224c218<=a<0x2250000:a=self.read(a,8)
   if 0x2200000<=a<0x2360000:
    q=self.read(a+16,8)
    if 0x1000000<q<0x2360000:a=q
   b=bytes(self.read(a+i,1) for i in range(120));return b.split(b'\0')[0].decode('utf8') if b[0] else hex(a)
  except:return hex(a)
 def run(self,start,stub=0,limit=15000,reset=True):
  
  if reset:self.r={'sp':0x70000000,'x30':0xdeadbeef}
  self.pc=start
  for step in range(limit):
   pc=self.pc;i=D.get(pc)
   if i is None:return 'missing '+hex(pc)
   
   if hasattr(self,'visited'):self.visited.append(pc)
   self.pc+=4;op,_,rest=i.partition(' ');p=[x.strip() for x in re.split(r',(?=[^\]]*(?:\[|$))',rest)]
   try:
    if op in ['adrp','adr']:self.put(p[0],int(p[1],0))
    elif op in ['mov','movz']:self.put(p[0],self.reg(p[1]))
    elif op=='movk':
     sh=int(p[2].split('#')[1],0) if len(p)>2 else 0;self.put(p[0],(self.reg(p[0])&~(65535<<sh))|(self.reg(p[1])<<sh))
    elif op in ['add','sub','and','orr','eor']:
     a=self.reg(p[1]);b=self.reg(p[2]);
     if len(p)>3:
      if p[3].startswith('SXTW'):b=struct.unpack('<i',struct.pack('<I',b&0xffffffff))[0]
      if '#' in p[3]:b<<=int(p[3].split('#')[1],0)
     self.put(p[0],{'add':lambda:a+b,'sub':lambda:a-b,'and':lambda:a&b,'orr':lambda:a|b,'eor':lambda:a^b}[op]())
    elif op in ['neg','mvn']:self.put(p[0],-self.reg(p[1]) if op=='neg' else ~self.reg(p[1]))
    elif op=='cmp':self.flags=(self.reg(p[0]),self.reg(p[1]),32 if p[0].startswith('w') else 64)
    elif op=='cset':self.put(p[0],int(self.cond(p[1])))
    elif op=='csel':self.put(p[0],self.reg(p[1] if self.cond(p[3]) else p[2]))
    elif op.startswith(('ldr','ldur','ldar','str','stur','stlr')):
     isload=op.startswith(('ld','lda'));n=1 if op.endswith('b') else 2 if op.endswith('h') else 4 if p[0].startswith('w') else 8;a=self.addr(p[1]);
     if isload:self.put(p[0],self.read(a,n))
     else:self.write(a,n,self.reg(p[0]))
    elif op in ['stp','ldp']:
     mem=p[2];pre=mem.endswith('!');mem=mem.rstrip('!');a=self.addr(mem);base=mem.strip('[]').split(',')[0];n=4 if p[0].startswith('w') else 8
     if pre:self.put(base,a)
     for k in range(2):
      if op=='stp':self.write(a+n*k,n,self.reg(p[k]))
      else:self.put(p[k],self.read(a+n*k,n))
     if len(p)>3:self.put(base,self.reg(base)+self.reg(p[3]))
    elif op in ['b','br']:self.pc=self.reg(p[0])
    elif op in ['cbz','cbnz']:
     if (self.reg(p[0])==0)==(op=='cbz'):self.pc=int(p[1],0)
    elif op.startswith('b.'):
     if self.cond(op[2:]):self.pc=int(p[0],0)
    elif op=='bl':
     target=int(p[0],0)
     # Resolve straightforward wrapper chains; preserve call-site argument state.
     seen=set()
     while target in D and target not in seen:
      seen.add(target);ins=[D.get(target+k*4,'') for k in range(5)]
      if ins[0].startswith('stp x29,x30') and ins[1].startswith('bl '):target=int(ins[1].split()[1],0)
      else:break
     self.calls.append((hex(pc),hex(target),[self.describe(self.reg('x'+str(k))) for k in range(4)]))
     if target==0x17a4848:pass
     elif target in [0x17a4818,0x17a4824]:pass
     else:self.put('x0',self.call_handler(target,self) if hasattr(self,'call_handler') else stub)
    elif op=='ret':return 'return '+hex(self.reg('x0'))
    elif op in ['nop']:pass
    else:return 'unsupported '+hex(pc)+' '+i
   except Exception as e:return f'ERROR {pc:x} {i} {p} {e}'
  return 'limit'
if __name__=='__main__':
 import sys
 for stub in [0,1]:
  e=Emu();result=e.run(int(sys.argv[1],0),stub);print(result);print(json.dumps(e.calls,indent=2));print('WRITES',len(e.writes));
  for p,a,n,v in e.writes:
   if n==1 and a<0x4000000:print(hex(p),hex(a),hex(v))


