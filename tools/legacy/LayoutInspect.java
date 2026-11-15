import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.listing.*;
public class LayoutInspect extends GhidraScript {
 public void run() throws Exception {
  DecompInterface d=new DecompInterface(); d.openProgram(currentProgram);
  FunctionIterator it=currentProgram.getFunctionManager().getFunctions(true); int count=0;
  while(it.hasNext()) { Function f=it.next(); String n=f.getName(true);
   if(n.matches("(?i).*(YTPPivotTabBarController|watermark|floatingForced|layoutTabBar|placeTabBar).*") && count++<40) {
    println("FUNCTION "+f.getEntryPoint()+" "+n);
    DecompileResults r=d.decompileFunction(f,25,monitor);
    if(r.decompileCompleted()) println(r.getDecompiledFunction().getC());
   }
  }
  d.dispose();
 }
}


