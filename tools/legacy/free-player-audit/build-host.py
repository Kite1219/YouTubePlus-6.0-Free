from pathlib import Path
import re
r=Path('ytplus-analysis/free-player-audit');s=(r/'PersonalPlayback.rs').read_text();s=re.sub(r'#\[used\]#\[unsafe\(link_section="__DATA,__mod_init_func"\)\]static INITIALIZE:[^;]+;','',s)
s=re.sub(r'#\[link_name="objc_msgSend"\]fn (\w+)',lambda m:'#[link_name="host_'+m[1]+'"]fn '+m[1],s)
for i in range(10):s+=f'\nstatic mut H{i}:Id=0 as Id;'
s+='''
type F1=unsafe extern "C" fn(Id)->Id;type F2=unsafe extern "C" fn(Id,Id)->Id;type FM=unsafe extern "C" fn(Id,Id,Id,Id)->Id;type FH=unsafe extern "C" fn(Id,Id,Id,*mut Id);type FD=unsafe extern "C" fn(Id,Id,unsafe extern "C" fn(Id));
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_callback(i:usize,p:Id){unsafe{
'''
for i in range(10):s+=f'if i=={i}'+'{'+f'H{i}=p;'+'}\n'
s+='}}\n'
def export(name,args,ret,body):
 global s
 s+=f'#[unsafe(export_name="{name}")]pub unsafe extern "C" fn stub_{name}({args})->{ret}'+'{unsafe{'+body+'}}\n'
for n,args,body in [('objc_getClass','p:*const u8','transmute::<Id,F1>(H0)(p as Id)'),('sel_registerName','p:*const u8','transmute::<Id,F1>(H1)(p as Id)'),('object_getClass','o:Id','transmute::<Id,F1>(H3)(o)'),('class_getInstanceMethod','c:Id,s:Id','transmute::<Id,F2>(H4)(c,s)'),('class_getInstanceVariable','c:Id,n:*const u8','transmute::<Id,F2>(H5)(c,n as Id)'),('object_getIvar','o:Id,v:Id','transmute::<Id,F2>(H6)(o,v)'),('dlsym','h:Id,n:*const u8','transmute::<Id,F2>(H8)(h,n as Id)')]:export(n,args,'Id',body)
export('MSHookMessageEx','c:Id,s:Id,f:Id,old:*mut Id','()','transmute::<Id,FH>(H7)(c,s,f,old);')
export('dispatch_async_f','q:Id,c:Id,f:unsafe extern "C" fn(Id)','()','transmute::<Id,FD>(H9)(q,c,f);')
msg='transmute::<Id,FM>(H2)'
export('host_m0','o:Id,s:Id','Id',msg+'(o,s,0 as Id,0 as Id)')
export('host_m1','o:Id,s:Id,a:Id','Id',msg+'(o,s,a,0 as Id)')
export('host_m2','o:Id,s:Id,a:Id,b:Id','Id',msg+'(o,s,a,b)')
export('host_b0','o:Id,s:Id','bool',msg+'(o,s,0 as Id,0 as Id)!=0 as Id')
export('host_b1','o:Id,s:Id,a:Id','bool',msg+'(o,s,a,0 as Id)!=0 as Id')
export('host_setb','o:Id,s:Id,a:bool,b:Id','()',msg+'(o,s,a as usize as Id,b);')
export('host_boolarg','o:Id,s:Id,a:bool','()',msg+'(o,s,a as usize as Id,0 as Id);')
s+='''#[unsafe(no_mangle)]pub unsafe extern "C" fn test_update(o:Id,s:Sel,a:Id){unsafe{update_buttons(o,s,a);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_disabled(o:Id,s:Sel)->bool{unsafe{pip_disabled(o,s)}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_press(o:Id,s:Sel,a:Id){unsafe{overlay_press(o,s,a);}}
'''
s+='''
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_resign(o:Id,s:Sel){unsafe{resign(o,s);}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_set_auto(o:Id,s:Sel,v:bool,kind:usize){unsafe{if kind==0{inline_auto(o,s,v);}else{background_auto(o,s,v);}}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_get_auto(o:Id,s:Sel)->bool{unsafe{get_inline_auto(o,s)}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn test_activate(o:Id,s:Sel){unsafe{activated(o,s);}}
'''
(r/'PersonalPlayback-host.rs').write_text(s)
