import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import ghidra.program.model.symbol.*;
import java.util.*;
public class SubscriptionInspect extends GhidraScript {
 public void run() throws Exception {
  println("TARGET_SHA_EXPECTED aec278e47289639a7dc8b22cc4257df9b9f75336d6e187dd82da0d981c1ae59c");
  println("IMAGE_BASE "+currentProgram.getImageBase());
  long base=currentProgram.getImageBase().getOffset();
  long[] seeds={0x34b160L,0x34bcdcL,0x34c1c4L};
  String[] names={"PatreonSection","PatreonStatusCell","PatreonButtonCell"};
  DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
  LinkedHashSet<Address> todo=new LinkedHashSet<>();
  for(int i=0;i<seeds.length;i++){Address a=toAddr(base+seeds[i]);disassemble(a);Function f=getFunctionAt(a);if(f==null)f=createFunction(a,names[i]);todo.add(a);}
  int count=0;
  while(!todo.isEmpty()&&count<18){Address a=todo.iterator().next();todo.remove(a);Function f=getFunctionAt(a);if(f==null){disassemble(a);f=createFunction(a,null);}if(f==null)continue;
   count++;println("FUNCTION "+a+" "+f.getName());
   DecompileResults result=d.decompileFunction(f,18,monitor);if(result.decompileCompleted())println(result.getDecompiledFunction().getC());else println("DECOMPILER_LIMIT "+result.getErrorMessage());
   if(count<=3){InstructionIterator it=currentProgram.getListing().getInstructions(f.getBody(),true);int limit=0;
    while(it.hasNext()&&limit++<1200){Instruction ins=it.next();if(ins.getFlowType().isCall())for(Address target:ins.getFlows()){
     println("DIRECT_CALL "+ins.getAddress()+" -> "+target);
     if(target.getOffset()>=base+0x4000&&target.getOffset()<base+0x550000)todo.add(target);
    }}
   }
  }
  d.dispose();
 }
}
