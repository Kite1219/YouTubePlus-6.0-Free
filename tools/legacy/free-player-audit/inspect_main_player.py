from pathlib import Path
import zipfile,struct,json,re
r=Path('ytplus-analysis/free-player-audit')
with zipfile.ZipFile('ytplus-analysis/YouTubePlus-Personal-6.0-test.3-YouPiP.ipa') as z:b=z.read('Payload/YouTube.app/YouTube')
base=0x100000000;secs=[];o=32
for k in range(struct.unpack_from('<I',b,16)[0]):
 cmd,size=struct.unpack_from('<II',b,o)
 if cmd==0x19:
  for i in range(struct.unpack_from('<I',b,o+64)[0]):
   q=o+72+i*80;name=b[q:q+16].split(b'\0')[0].decode();addr,sz=struct.unpack_from('<QQ',b,q+32);off=struct.unpack_from('<I',b,q+48)[0];secs.append(dict(name=name,addr=addr,size=sz,offset=off))
 o+=size
cache={}
def off(a):
 for s in secs:
  if s['addr']<=a<s['addr']+s['size'] and s['offset']:return s['offset']+a-s['addr']
 raise ValueError(hex(a))
def rd(a,f):return struct.unpack_from(f,b,off(a))
def ptr(a):
 v=rd(a,'<Q')[0]
 return 0 if v==0 or v>>63 else base+(v&0xfffffffff)
def string(a):
 p=off(a);return b[p:b.index(0,p)].decode('utf8','replace')
def methods(a):
 if not a:return []
 flags,n=rd(a,'<II');size=flags&65535;out=[]
 for k in range(n):
  p=a+8+k*size
  if flags&0x80000000:
   no,ty,im=rd(p,'<iii');name=p+no if flags&0x40000000 else ptr(p+no);typ=p+4+ty;imp=p+8+im
  else:name,typ,imp=ptr(p),ptr(p+8),ptr(p+16)
  out.append(dict(name=string(name),types=string(typ),imp=hex(imp)))
 return out
def parse(c):
 ro=ptr(c+32)&~7;out={'name':string(ptr(ro+24)),'class':hex(c),'superclass':hex(ptr(c+8)),'methods':methods(ptr(ro+32)),'ivars':[]}
 iv=ptr(ro+48)
 if iv:
  size,count=rd(iv,'<II')
  for k in range(count):
   q=iv+8+k*size;out['ivars'].append({'name':string(ptr(q+8)),'type':string(ptr(q+16)),'offset':rd(ptr(q),'<I')[0]})
 return out
wanted={'YTMainAppControlsOverlayView','YTMainAppVideoPlayerOverlayViewController','YTPlayerViewController','YTLocalPlaybackController','YTPlayerPIPController','MLPIPControllerImpl','MLPIPController','YTInlinePlayerBarContainerView','YTBackgroundabilityPolicy','YTSystemNotifications'}
s=next(x for x in secs if x['name']=='__objc_classlist');found=[]
for q in range(s['addr'],s['addr']+s['size'],8):
 try:
  c=ptr(q);ro=ptr(c+32)&~7;n=string(ptr(ro+24))
  if n in wanted:found.append(parse(c))
 except Exception:pass
(r/'youtube-21.43.5-player-objc.json').write_text(json.dumps(found,indent=2))
for c in found:
 print('\nCLASS',c['name'])
 print('IVARS',[(x['name'],x['type']) for x in c['ivars'] if re.search('pip|delegate|playback|policy|player|parent',x['name'],re.I)])
 print('METHODS',[(x['name'],x['types'],x['imp']) for x in c['methods'] if re.search('pip|picture|resign|background|playbackController|eventsDelegate|parentViewController',x['name'],re.I)])
