import ghidra.app.script.GhidraScript;
import ghidra.app.emulator.EmulatorHelper;
import java.nio.file.*;
public class GatePlayerTrace extends GhidraScript {
 String describe(EmulatorHelper e,long p){if(p==0)return "nil";try{long q=java.nio.ByteBuffer.wrap(e.readMemory(toAddr(p+16),8)).order(java.nio.ByteOrder.LITTLE_ENDIAN).getLong()&0xfffffffffL;if(q>0x1000000L&&q<0x2360000L)return e.readNullTerminatedString(toAddr(q),120);return "0x"+Long.toHexString(p);}catch(Exception ex){return "0x"+Long.toHexString(p);}}
 public void run() throws Exception{
  for(long fn:new long[]{0x1a80f0L,0x1ba514L})for(int selected=0;selected<2;selected++){
   EmulatorHelper e=new EmulatorHelper(currentProgram);int n=0;try{
    e.writeRegister("pc",fn);e.writeRegister("sp",0x70000000L);e.writeRegister("x30",0x7fff0000L);e.writeRegister("x0",0x60001000L);e.writeRegister("x2",0x60002000L);e.writeRegister("x3",0x60003000L);
    println("PLAYER_METHOD "+Long.toHexString(fn)+" selected="+selected);
    while(e.getExecutionAddress().getOffset()!=0x7fff0000L&&n++<12000){long pc=e.getExecutionAddress().getOffset();
     if(pc==0x17a47f4L){String sel=e.readNullTerminatedString(toAddr(e.readRegister("x1").longValue()),120);println("OBJC_CALL "+sel+" arg2="+describe(e,e.readRegister("x2").longValue())+" arg3="+describe(e,e.readRegister("x3").longValue()));
      if(sel.equals("standardUserDefaults"))e.writeRegister("x0",0x60004000L);
      else if(sel.equals("boolForKey:")||sel.equals("isSelected"))e.writeRegister("x0",selected);
      else if(sel.equals("setBool:forKey:")||sel.equals("setSelected:")||sel.equals("setImage:forState:")||sel.equals("synchronize"))e.writeRegister("x0",0);
      else{println("TRACE_BOUNDARY unmodeled UIKit/Foundation call");break;}
      e.writeRegister("pc",e.readRegister("x30"));continue;
     }
     if(pc==0x17a4818L||pc==0x17a4824L||pc==0x17a4848L||pc==0x17a474cL){e.writeRegister("pc",e.readRegister("x30"));continue;}
     if(!e.step(monitor)){println("TRACE_BOUNDARY "+e.getExecutionAddress()+" "+e.getLastError());break;}
    }
    println("PLAYER_TRACE_STOP "+e.getExecutionAddress()+" steps="+n);
   }finally{e.dispose();}
  }
 }
}
