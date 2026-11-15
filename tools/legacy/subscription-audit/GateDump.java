import ghidra.app.script.GhidraScript;
import ghidra.program.model.listing.*;
public class GateDump extends GhidraScript {
 public void run() throws Exception {
  String[] args=getScriptArgs(); long start=Long.decode(args[0]),end=Long.decode(args[1]);
  for(long p=start;p<end;p+=4){Instruction i=getInstructionAt(toAddr(p)); if(i==null){disassemble(toAddr(p));i=getInstructionAt(toAddr(p));} if(i!=null)println(i.getAddress()+" "+i.toString());}
 }
}
