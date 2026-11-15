from emulate_gate import *
import hashlib
cases=[];library=(R/'YTLite-Personal.dylib').read_bytes()
# Read new instructions from the actual final library, then decode their complete MOVZ W8 immediate form.
for a in [0xc23e0,0xc3110]:
 word=struct.unpack_from('<I',library,a)[0];assert word&0xffe0001f==0x52800008
for getter,selector,values,flag_read in [(0xc1ddc,'boolForKey:',[0,1],0xc23e0),(0xc2aa4,'integerForKey:',[0,37],0xc3110)]:
 original=D[flag_read]
 for patched in [False,True]:
  if patched:
   word=struct.unpack_from('<I',library,flag_read)[0];D[flag_read]='mov w8,#'+hex((word>>5)&65535)
  else:D[flag_read]=original
  for flag in [0,1]:
   for saved in values:
    e=Emu();e.r={'sp':0x70000000,'x0':0x2306a30,'x30':0xdeadbeef};e.write(0x2363040,1,flag)
    def handler(target,emulator):
     if target==0xc24bc:
      word=struct.unpack_from('<I',library,target)[0];assert word==0x52800020;return (word>>5)&65535
     if target==0x17a47f4 and emulator.describe(emulator.reg('x1'))==selector:return saved
     return 1
    e.call_handler=handler;actual=e.run(getter,reset=False);expected=saved if patched or not flag else 0
    assert actual=='return '+hex(expected),(hex(getter),patched,flag,saved,actual,expected)
    cases.append({'getter':hex(getter),'build':'test2' if patched else 'test1','remote_access_error':flag,'saved':saved,'actual':expected})
 D[flag_read]=original
report={'library_sha256':hashlib.sha256(library).hexdigest(),'cases':cases,'passed':len(cases),'result':'Reproduced test1 settings blocked by access-error flag; test2 preserves saved settings with error flag clear or set','scope':'Offline instruction interpretation with mocked external calls, not an iOS device test'}
(R/'access-error-regression.json').write_text(json.dumps(report,indent=2));print(report['result']);print('Passed',len(cases),'cases')
