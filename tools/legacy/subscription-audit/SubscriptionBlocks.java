import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
public class SubscriptionBlocks extends GhidraScript {
 public void run() throws Exception {
  long[] addresses={0x34b31cL,0x34b1d8L,0x34bff4L,0x34bd78L,0x34c898L,0x34c260L,0xc3590L};
  DecompInterface d=new DecompInterface();d.openProgram(currentProgram);
  for(long value:addresses){Address a=toAddr(value);disassemble(a);Function f=getFunctionAt(a);if(f==null)f=createFunction(a,null);println("BLOCK "+a);if(f!=null){DecompileResults result=d.decompileFunction(f,12,monitor);if(result.decompileCompleted())println(result.getDecompiledFunction().getC());else println("LIMIT "+result.getErrorMessage());}}
  d.dispose();
 }
}
