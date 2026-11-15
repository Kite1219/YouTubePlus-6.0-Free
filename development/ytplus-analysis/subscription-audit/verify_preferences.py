from emulate_gate import *
checks=[]
for fn,selector,values in [(0xc1ddc,'boolForKey:',[0,1]),(0xc2aa4,'integerForKey:',[0,37])]:
 for enabled in [0,1]:
  for value in values:
   e=Emu()
   def handler(t,emu):
    if t==0xc24bc:return enabled
    if t==0x17a47f4 and emu.describe(emu.reg('x1'))==selector:return value
    return 1
   e.call_handler=handler;result=e.run(fn);expected=value if enabled else 0
   assert result=='return '+hex(expected),(hex(fn),enabled,value,result)
   checks.append({'getter':hex(fn),'access_granted':enabled,'saved_value':value,'result':expected})
# Verify the actual rebuilt gate instructions using independently decoded Ghidra output.
verification=(R/'patched-verification.txt').read_text()
assert '000c24bc mov w0,#0x1' in verification and '000c24c0 ret' in verification
report={'checks':checks,'result':'8 preference-preservation cases passed','scope':'Bounded offline instruction interpretation with mocked external calls; not iOS runtime testing'}
(R/'preference-verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report,indent=2))
