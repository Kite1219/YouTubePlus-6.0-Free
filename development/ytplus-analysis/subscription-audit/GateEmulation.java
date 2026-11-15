import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import ghidra.program.model.address.*;
import java.nio.file.*;
import java.util.*;
public class GateEmulation extends GhidraScript {
 static final long KEY=0x2306a30L,STACK=0x70000000L,STOP=0x7fff0000L;
 String str(EmulatorHelper e,long p){try{return e.readNullTerminatedString(toAddr(p),120);}catch(Exception ex){return "<unreadable>";}}
 public void run() throws Exception {
  byte[] original=Files.readAllBytes(Path.of(getScriptArgs()[0]));byte[] patched=Files.readAllBytes(Path.of(getScriptArgs()[1]));
  long[] sites={0xc24bcL,0xc1bd8L,0xc4b48L,0xcac80L,0x34b38cL,0x34b3e8L,0xc23e0L,0xc3110L};int[] sizes={8,8,8,4,4,4,4,4};int passed=0,total=0;
  for(int build=1;build<=2;build++){
   for(int k=0;k<sites.length;k++){byte[] source=(build==1&&k>=6)?original:patched;clearListing(toAddr(sites[k]),toAddr(sites[k]+sizes[k]-1));currentProgram.getMemory().setBytes(toAddr(sites[k]),Arrays.copyOfRange(source,(int)sites[k],(int)sites[k]+sizes[k]));}
   for(long function:new long[]{0xc1ddcL,0xc2aa4L})for(int flag=0;flag<2;flag++)for(long saved:new long[]{0,1,37,-1}){
    total++;EmulatorHelper e=new EmulatorHelper(currentProgram);boolean sawSetting=false,ok=true;int count=0,external=0;
    try{
     e.writeRegister("pc",function);e.writeRegister("sp",STACK);e.writeRegister("x29",STACK);e.writeRegister("x30",STOP);e.writeRegister("x0",KEY);
     for(int k=19;k<=28;k++)e.writeRegister("x"+k,0x50000000L+k);
     e.writeMemoryValue(toAddr(0x2363040L),1,flag);
     while(e.getExecutionAddress().getOffset()!=STOP&&count++<10000){
      long pc=e.getExecutionAddress().getOffset();
      if(pc==0x17a47f4L){
       String selector=str(e,e.readRegister("x1").longValue());external++;
       if(selector.equals("standardUserDefaults"))e.writeRegister("x0",0x60001000L);
       else if(selector.equals("boolForKey:")||selector.equals("integerForKey:")){
        if(e.readRegister("x2").longValue()!=KEY)throw new Exception("Setting key was not preserved");
        e.writeRegister("x0",selector.equals("boolForKey:")?(saved==0?0:1):saved);sawSetting=true;
       }else throw new Exception("Unexpected selector "+selector+" at "+e.getExecutionAddress());
       e.writeRegister("pc",e.readRegister("x30"));continue;
      }
      if(pc==0x17a4818L||pc==0x17a4824L||pc==0x17a4848L){e.writeRegister("pc",e.readRegister("x30"));continue;}
      if(!e.step(monitor))throw new Exception(e.getLastError());
     }
     if(count>=10000)throw new Exception("Instruction limit");
     long actual=e.readRegister("x0").longValue();long expected=build==1&&flag==1?0:function==0xc1ddcL?(saved==0?0:1):saved;
     if(actual!=expected)throw new Exception("Result "+actual+" expected "+expected);
     if(e.readRegister("sp").longValue()!=STACK)throw new Exception("Stack was not restored");
     for(int k=19;k<=28;k++)if(e.readRegister("x"+k).longValue()!=0x50000000L+k)throw new Exception("Callee-saved register x"+k+" changed");
     if((build==2||flag==0)&&!sawSetting)throw new Exception("Saved preference was never read");
     passed++;println("PASS build="+build+" getter="+Long.toHexString(function)+" error="+flag+" saved="+saved+" result="+actual+" steps="+count+" externalCalls="+external);
    }catch(Exception ex){ok=false;println("FAIL build="+build+" getter="+Long.toHexString(function)+" error="+flag+" saved="+saved+" pc="+e.getExecutionAddress()+" "+ex);}
    finally{e.dispose();}
   }
  }
  println("GHIDRA_PCODE_EMULATION passed="+passed+" total="+total+" external_objc_calls=mocked runtime_device_test=false");
 }
}
