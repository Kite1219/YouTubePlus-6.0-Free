import ghidra.app.script.GhidraScript;
import ghidra.app.decompiler.*;
import ghidra.program.model.address.*;
import ghidra.program.model.listing.*;
import java.nio.file.*;
import java.security.*;
public class GateVerify extends GhidraScript {
 public void run() throws Exception {
  byte[] b=Files.readAllBytes(Path.of(getScriptArgs()[0]));
  StringBuilder hash=new StringBuilder();for(byte x:MessageDigest.getInstance("SHA-256").digest(b))hash.append(String.format("%02x",x));println("PATCHED_LIBRARY_SHA256 "+hash);
  long[] a={0xc24bcL,0xc1bd8L,0xc4b48L,0xcac80L,0x34b38cL,0x34b3e8L,0xc23e0L,0xc3110L};int[] sizes={8,8,8,4,4,4,4,4};
  DecompInterface decomp=new DecompInterface();
  for(int i=0;i<a.length;i++){
   Address p=toAddr(a[i]);clearListing(p,p.add(sizes[i]-1));byte[] bytes=java.util.Arrays.copyOfRange(b,(int)a[i],(int)a[i]+sizes[i]);currentProgram.getMemory().setBytes(p,bytes);disassemble(p);
   for(int k=0;k<sizes[i];k+=4){Instruction ins=getInstructionAt(p.add(k));println("VERIFIED_INSTRUCTION "+p.add(k)+" "+ins);}
  }
  decomp.openProgram(currentProgram);
  for(int i=0;i<4;i++){Function f=getFunctionAt(toAddr(a[i]));if(f==null)f=createFunction(toAddr(a[i]),null);if(f!=null){DecompileResults d=decomp.decompileFunction(f,12,monitor);println("PATCHED_FUNCTION "+toAddr(a[i]));if(d.decompileCompleted())println(d.getDecompiledFunction().getC());}}
  decomp.dispose();
 }
}
