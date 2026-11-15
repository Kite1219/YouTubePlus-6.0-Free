from emulate_gate import *
for key in [0,0x2306a30]:
 for flag in [0,1]:
  e=Emu();e.r={'sp':0x70000000,'x0':key,'x30':0xdeadbeef};e.write(0x2363040,1,flag);e.visited=[]
  def handler(t,emu):
   if t==0xc24bc:return 1
   if t==0x17a47f4 and emu.describe(emu.reg('x1'))=='boolForKey:':return 1
   return 1
  e.call_handler=handler;result=e.run(0xc1ddc,reset=False)
  print('KEY',hex(key),'ACTIVE',flag,result,'READ_ACTIVE',0xc23e0 in e.visited,'CALLS',e.calls)
