"""Add the scoped layout helper while preserving the existing playback library."""
import argparse,copy,hashlib,json,struct,zipfile
from pathlib import Path
BASE_SHA='4ad31f12f9008ad233cbfadc59e4a0796133d88fec7957a545d6daf627b19044'
def sha(b):return hashlib.sha256(b).hexdigest()
def inject(data,name):
    b=bytearray(data);assert struct.unpack_from('<I',b)[0]==0xfeedfacf
    count,size=struct.unpack_from('<II',b,16);p=32;start=len(b);names=[]
    for _ in range(count):
        cmd,n=struct.unpack_from('<II',b,p)
        if cmd in (0xc,0x80000018):
            pos=p+struct.unpack_from('<I',b,p+8)[0];names.append(b[pos:b.index(0,pos)].decode())
        if cmd==0x19:
            for i in range(struct.unpack_from('<I',b,p+64)[0]):
                off=struct.unpack_from('<I',b,p+72+i*80+48)[0]
                if off:start=min(start,off)
        p+=n
    assert p==32+size and name not in names
    raw=name.encode()+b'\0';length=(24+len(raw)+7)&~7
    assert p+length<=start and not any(b[p:p+length]),'No verified Mach-O header padding'
    b[p:p+length]=struct.pack('<IIIIII',0xc,length,24,0,0,0)+raw+b'\0'*(length-24-len(raw))
    struct.pack_into('<II',b,16,count+1,size+length)
    return bytes(b)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--base',type=Path,required=True);ap.add_argument('--helper',type=Path,required=True);ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    assert sha(args.base.read_bytes())==BASE_SHA
    lib='Payload/YouTube.app/Frameworks/DuoWatchLayout.dylib';main='Payload/YouTube.app/YouTube'
    helper=args.helper.read_bytes();assert struct.unpack_from('<I',helper)[0]==0xfeedfacf
    with zipfile.ZipFile(args.base) as src,zipfile.ZipFile(args.output,'w',zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=False) as out:
        assert src.testzip() is None and lib not in src.namelist()
        for info in src.infolist():
            b=src.read(info);out.writestr(copy.copy(info),inject(b,'@executable_path/Frameworks/DuoWatchLayout.dylib') if info.filename==main else b)
        info=zipfile.ZipInfo(lib,src.getinfo(main).date_time);info.create_system=3;info.external_attr=0o100755<<16;info.compress_type=zipfile.ZIP_DEFLATED;out.writestr(info,helper)
    with zipfile.ZipFile(args.base) as src,zipfile.ZipFile(args.output) as out:
        assert out.testzip() is None
        assert set(out.namelist())==set(src.namelist())|{lib}
        for n in src.namelist():
            if n!=main:assert out.read(n)==src.read(n),n
        assert out.read('Payload/YouTube.app/Frameworks/PersonalPlayback.dylib')==src.read('Payload/YouTube.app/Frameworks/PersonalPlayback.dylib')
    report={'baseSHA256':BASE_SHA,'ipaSHA256':sha(args.output.read_bytes()),'helperSHA256':sha(helper),'ipaBytes':args.output.stat().st_size,'changed':[main],'added':[lib],'allOtherMembersIdentical':True,'playbackHelperIdentical':True,'InfoPlistIdentical':True,'zipCRC':'passed','deviceTested':False}
    args.output.with_suffix('.validation.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report))
if __name__=='__main__':main()
