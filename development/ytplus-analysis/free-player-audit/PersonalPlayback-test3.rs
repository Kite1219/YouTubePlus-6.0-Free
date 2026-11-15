#![feature(no_core, lang_items, auto_traits, intrinsics)]
#![no_core]
#![allow(internal_features, improper_ctypes, clashing_extern_declarations, ambiguous_wide_pointer_comparisons)]

#[lang="pointee_sized"] pub trait PointeeSized {}
#[lang="meta_sized"] pub trait MetaSized: PointeeSized {}
#[lang="sized"] pub trait Sized: MetaSized {}
#[lang="sync"] pub unsafe auto trait Sync {}
#[lang="copy"] pub trait Copy {}
impl<T:PointeeSized> Copy for *const T {}
impl<T:PointeeSized> Copy for *mut T {}
impl Copy for u8 {} impl Copy for u32 {} impl Copy for usize {} impl Copy for bool {}
#[lang="drop_glue"] pub unsafe fn drop_glue<T:PointeeSized>(_:*mut T) {}
#[lang="legacy_receiver"] pub trait LegacyReceiver:PointeeSized {}
impl<T:PointeeSized> LegacyReceiver for &T {}
impl<T:PointeeSized> LegacyReceiver for &mut T {}
#[lang="eq"] pub trait PartialEq<Rhs:PointeeSized=Self> {fn eq(&self,rhs:&Rhs)->bool;fn ne(&self,rhs:&Rhs)->bool;}
impl<T:PointeeSized> PartialEq for *mut T {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl<T:PointeeSized> PartialEq for *const T {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl PartialEq for usize {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl PartialEq for bool {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
impl PartialEq for u32 {fn eq(&self,rhs:&Self)->bool{*self==*rhs}fn ne(&self,rhs:&Self)->bool{*self!=*rhs}}
#[lang="add"] pub trait Add<Rhs=Self>{type Output;fn add(self,rhs:Rhs)->Self::Output;}
impl Add for usize{type Output=Self;fn add(self,rhs:Self)->Self{self+rhs}}
#[lang="not"] pub trait Not{type Output;fn not(self)->Self::Output;}
impl Not for bool{type Output=Self;fn not(self)->Self{if self{false}else{true}}}
#[lang="partial_ord"] pub trait PartialOrd<Rhs:PointeeSized=Self>:PartialEq<Rhs>{fn lt(&self,rhs:&Rhs)->bool;fn le(&self,rhs:&Rhs)->bool;fn gt(&self,rhs:&Rhs)->bool;fn ge(&self,rhs:&Rhs)->bool;}
impl PartialOrd for usize{fn lt(&self,rhs:&Self)->bool{*self<*rhs}fn le(&self,rhs:&Self)->bool{*self<=*rhs}fn gt(&self,rhs:&Self)->bool{*self>*rhs}fn ge(&self,rhs:&Self)->bool{*self>=*rhs}}
#[rustc_intrinsic] pub unsafe fn transmute<Src,Dst>(source:Src)->Dst;


type Id=*mut u8;type Sel=*mut u8;
unsafe extern "C" {
 fn objc_getClass(n:*const u8)->Id;fn object_getClass(o:Id)->Id;
 fn sel_registerName(n:*const u8)->Sel;fn class_getInstanceMethod(c:Id,s:Sel)->Id;
 fn class_getInstanceVariable(c:Id,n:*const u8)->Id;fn object_getIvar(o:Id,v:Id)->Id;
 fn MSHookMessageEx(c:Id,s:Sel,replacement:Id,old:*mut Id);
 fn dlsym(h:Id,n:*const u8)->Id;fn dispatch_async_f(q:Id,c:Id,f:unsafe extern "C" fn(Id));
 #[link_name="objc_msgSend"]fn m0(o:Id,s:Sel)->Id;
 #[link_name="objc_msgSend"]fn m1(o:Id,s:Sel,a:Id)->Id;
 #[link_name="objc_msgSend"]fn m2(o:Id,s:Sel,a:Id,b:Id)->Id;
 #[link_name="objc_msgSend"]fn b0(o:Id,s:Sel)->bool;
 #[link_name="objc_msgSend"]fn b1(o:Id,s:Sel,a:Id)->bool;
 #[link_name="objc_msgSend"]fn setb(o:Id,s:Sel,v:bool,k:Id);
 #[link_name="objc_msgSend"]fn boolarg(o:Id,s:Sel,v:bool);
}
unsafe fn s(n:*const u8)->Sel{unsafe{sel_registerName(n)}}
unsafe fn cls(n:*const u8)->Id{unsafe{objc_getClass(n)}}
unsafe fn ns(n:*const u8)->Id{unsafe{m1(cls(b"NSString\0" as *const u8),s(b"stringWithUTF8String:\0" as *const u8),n as Id)}}
unsafe fn defaults()->Id{unsafe{m0(cls(b"NSUserDefaults\0" as *const u8),s(b"standardUserDefaults\0" as *const u8))}}
unsafe fn pref(n:*const u8)->bool{unsafe{b1(defaults(),s(b"boolForKey:\0" as *const u8),ns(n))}}
unsafe fn put(n:*const u8,v:bool){unsafe{setb(defaults(),s(b"setBool:forKey:\0" as *const u8),v,ns(n));}}
unsafe fn responds(o:Id,n:*const u8)->bool{unsafe{if o==0 as Id{false}else{b1(o,s(b"respondsToSelector:\0" as *const u8),s(n))}}}
unsafe fn ivar(o:Id,n:*const u8)->Id{unsafe{if o==0 as Id{return 0 as Id;}let v=class_getInstanceVariable(object_getClass(o),n);if v==0 as Id{0 as Id}else{object_getIvar(o,v)}}}
unsafe fn hook(c:Id,n:*const u8,f:Id,old:*mut Id){unsafe{if c!=0 as Id{let sel=s(n);if class_getInstanceMethod(c,sel)!=0 as Id{MSHookMessageEx(c,sel,f,old);}}}}
static mut OLD_PLAYABILITY:Id=0 as Id;static mut OLD_MLVIDEO:Id=0 as Id;
static mut OLD_PIP_DISABLED:Id=0 as Id;static mut OLD_UPDATE:Id=0 as Id;
static mut OLD_OVERLAY:Id=0 as Id;static mut OLD_INLINE:Id=0 as Id;
type BoolMethod=unsafe extern "C" fn(Id,Sel)->bool;
type OneArg=unsafe extern "C" fn(Id,Sel,Id);
// Same two background-playability decisions as the free 5.2b4 source.
#[unsafe(no_mangle)]pub unsafe extern "C" fn personal_background(_o:Id,_s:Sel)->bool{unsafe{pref(b"backgroundPlayback\0" as *const u8)}}
unsafe extern "C" fn pip_disabled(o:Id,sel:Sel)->bool{unsafe{
 if pref(b"YouPiPEnabled\0" as *const u8){return false;}
 if OLD_PIP_DISABLED!=0 as Id{return transmute::<Id,BoolMethod>(OLD_PIP_DISABLED)(o,sel);}false
}}
unsafe extern "C" fn update_buttons(o:Id,sel:Sel,overlay:Id){unsafe{
 if OLD_UPDATE!=0 as Id{transmute::<Id,OneArg>(OLD_UPDATE)(o,sel,overlay);}
 if pref(b"YouPiPEnabled\0" as *const u8)&&responds(o,b"button:forOverlay:\0" as *const u8){
  let button=m2(o,s(b"button:forOverlay:\0" as *const u8),ns(b"pip\0" as *const u8),overlay);
  if responds(button,b"setHidden:\0" as *const u8){boolarg(button,s(b"setHidden:\0" as *const u8),true);}
 }
}}
unsafe fn controller_for_overlay(overlay:Id)->Id{unsafe{
 let mut delegate=ivar(overlay,b"_eventsDelegate\0" as *const u8);
 if delegate==0 as Id&&responds(overlay,b"delegate\0" as *const u8){delegate=ivar(m0(overlay,s(b"delegate\0" as *const u8)),b"_delegate\0" as *const u8);}
 if !responds(delegate,b"parentViewController\0" as *const u8){return 0 as Id;}
 let player=m0(delegate,s(b"parentViewController\0" as *const u8));
 ivar(ivar(player,b"_playbackController\0" as *const u8),b"_playerPIPController\0" as *const u8)
}}
unsafe fn manual_press(o:Id,sel:Sel,sender:Id,old:Id){unsafe{
 if pref(b"YouPiPEnabled\0" as *const u8){
  let controller=controller_for_overlay(o);
  if responds(controller,b"maybeTogglePictureInPicture\0" as *const u8){
   // Preserve YouPiP's user-action flag so its manual-only background guard agrees.
   let flag=dlsym(18446744073709551614usize as Id,b"FromUser\0" as *const u8);
   if flag!=0 as Id{*flag=1;m0(controller,s(b"maybeTogglePictureInPicture\0" as *const u8));return;}
  }
 }
 if old!=0 as Id{transmute::<Id,OneArg>(old)(o,sel,sender);}
}}
unsafe extern "C" fn overlay_press(o:Id,sel:Sel,sender:Id){unsafe{manual_press(o,sel,sender,OLD_OVERLAY);}}
unsafe extern "C" fn inline_press(o:Id,sel:Sel,sender:Id){unsafe{manual_press(o,sel,sender,OLD_INLINE);}}
unsafe extern "C" fn install_after_youpip(_context:Id){unsafe{
 let pm=cls(b"PlayerManager\0" as *const u8);if pm!=0 as Id{let meta=object_getClass(pm);
  hook(meta,b"isPiPDisabled\0" as *const u8,pip_disabled as Id,&raw mut OLD_PIP_DISABLED);
  hook(meta,b"updateButtonsForOverlay:\0" as *const u8,update_buttons as Id,&raw mut OLD_UPDATE);
 }
 hook(cls(b"YTMainAppControlsOverlayView\0" as *const u8),b"didPressPiP:\0" as *const u8,overlay_press as Id,&raw mut OLD_OVERLAY);
 hook(cls(b"YTInlinePlayerBarContainerView\0" as *const u8),b"didPressPiP:\0" as *const u8,inline_press as Id,&raw mut OLD_INLINE);
}}
#[unsafe(no_mangle)]pub unsafe extern "C" fn personal_playback_initialize(){unsafe{
 let pool=m0(m0(cls(b"NSAutoreleasePool\0" as *const u8),s(b"alloc\0" as *const u8)),s(b"init\0" as *const u8));
 if !pref(b"PersonalPlaybackMigration1\0" as *const u8){
  put(b"YouPiPEnabled\0" as *const u8,true);put(b"PiPActivationMethodKey\0" as *const u8,true);
  put(b"PiPActivationMethod2Key\0" as *const u8,false);put(b"PiPAllActivationMethodKey\0" as *const u8,false);
  put(b"CompatibilityModeKey\0" as *const u8,false);put(b"NoMiniPlayerPiPKey\0" as *const u8,false);
  put(b"backgroundPlayback\0" as *const u8,true);put(b"disablePiP\0" as *const u8,false);
  put(b"disablePiPButton\0" as *const u8,true);put(b"PersonalPlaybackMigration1\0" as *const u8,true);
 }
 hook(cls(b"YTIPlayabilityStatus\0" as *const u8),b"isPlayableInBackground\0" as *const u8,personal_background as Id,&raw mut OLD_PLAYABILITY);
 hook(cls(b"MLVideo\0" as *const u8),b"playableInBackground\0" as *const u8,personal_background as Id,&raw mut OLD_MLVIDEO);
 let main=dlsym(18446744073709551614usize as Id,b"_dispatch_main_q\0" as *const u8);
 if main!=0 as Id{dispatch_async_f(main,0 as Id,install_after_youpip);}
 m0(pool,s(b"drain\0" as *const u8));
}}
#[used]#[unsafe(link_section="__DATA,__mod_init_func")]static INITIALIZE:unsafe extern "C" fn()=personal_playback_initialize;
