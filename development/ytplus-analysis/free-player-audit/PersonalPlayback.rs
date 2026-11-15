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
#[lang="sub"]pub trait Sub<Rhs=Self>{type Output;fn sub(self,rhs:Rhs)->Self::Output;}
impl Sub for usize{type Output=Self;fn sub(self,rhs:Self)->Self{self-rhs}}
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
static mut OLD_RESIGN:Id=0 as Id;static mut OLD_INLINE_AUTO:Id=0 as Id;static mut OLD_BACKGROUND_AUTO:Id=0 as Id;
static mut OLD_AV_GET_AUTO:Id=0 as Id;static mut OLD_ACTIVATE:Id=0 as Id;
type ZeroArg=unsafe extern "C" fn(Id,Sel);type BoolArg=unsafe extern "C" fn(Id,Sel,bool);
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

unsafe fn manual_only()->bool{unsafe{
 pref(b"YouPiPEnabled\0" as *const u8)&&!pref(b"PiPAllActivationMethodKey\0" as *const u8)&&
 (pref(b"PiPActivationMethodKey\0" as *const u8)||pref(b"PiPActivationMethod2Key\0" as *const u8))
}}
unsafe fn status(message:*const u8){unsafe{m2(defaults(),s(b"setObject:forKey:\0" as *const u8),ns(message),ns(b"PersonalPlaybackLastPiPResult\0" as *const u8));}}
unsafe fn pip_from_candidate(o:Id)->Id{unsafe{
 let local=ivar(o,b"_playbackController\0" as *const u8);let p=ivar(local,b"_playerPIPController\0" as *const u8);
 if p!=0 as Id{return p;}ivar(o,b"_playerPIPController\0" as *const u8)
}}
unsafe fn walk_player(mut o:Id)->Id{unsafe{
 let mut remaining=8usize;
 while o!=0 as Id&&remaining>0{let p=pip_from_candidate(o);if p!=0 as Id{return p;}
  let next=if responds(o,b"parentViewController\0" as *const u8){m0(o,s(b"parentViewController\0" as *const u8))}
   else{if responds(o,b"nextResponder\0" as *const u8){m0(o,s(b"nextResponder\0" as *const u8))}else{0 as Id}};
  if next==o{return 0 as Id;}o=next;remaining=remaining-1;
 }0 as Id
}}
unsafe fn controller_for_overlay(overlay:Id)->Id{unsafe{
 let p=walk_player(ivar(overlay,b"_eventsDelegate\0" as *const u8));if p!=0 as Id{return p;}
 let p=walk_player(ivar(overlay,b"_delegate\0" as *const u8));if p!=0 as Id{return p;}
 if responds(overlay,b"delegate\0" as *const u8){let d=m0(overlay,s(b"delegate\0" as *const u8));let p=walk_player(ivar(d,b"_delegate\0" as *const u8));if p!=0 as Id{return p;}}
 walk_player(overlay)
}}
unsafe fn av_for_controller(controller:Id)->Id{unsafe{ivar(ivar(controller,b"_pipController\0" as *const u8),b"_pictureInPictureController\0" as *const u8)}}
unsafe fn prime_manual(av:Id){unsafe{
 if manual_only(){
  if responds(av,b"setCanStartPictureInPictureAutomaticallyFromInline:\0" as *const u8){boolarg(av,s(b"setCanStartPictureInPictureAutomaticallyFromInline:\0" as *const u8),false);}
  if responds(av,b"setCanStartAutomaticallyWhenEnteringBackground:\0" as *const u8){boolarg(av,s(b"setCanStartAutomaticallyWhenEnteringBackground:\0" as *const u8),false);}
 }
}}
unsafe extern "C" fn inline_auto(o:Id,sel:Sel,value:bool){unsafe{if OLD_INLINE_AUTO!=0 as Id{transmute::<Id,BoolArg>(OLD_INLINE_AUTO)(o,sel,if manual_only(){false}else{value});}}}
unsafe extern "C" fn background_auto(o:Id,sel:Sel,value:bool){unsafe{if OLD_BACKGROUND_AUTO!=0 as Id{transmute::<Id,BoolArg>(OLD_BACKGROUND_AUTO)(o,sel,if manual_only(){false}else{value});}}}
unsafe extern "C" fn get_inline_auto(o:Id,sel:Sel)->bool{unsafe{
 if manual_only(){return false;}if OLD_AV_GET_AUTO!=0 as Id{return transmute::<Id,BoolMethod>(OLD_AV_GET_AUTO)(o,sel);}false
}}
unsafe extern "C" fn resign(o:Id,sel:Sel){unsafe{
 if manual_only(){prime_manual(av_for_controller(o));return;}
 if OLD_RESIGN!=0 as Id{transmute::<Id,ZeroArg>(OLD_RESIGN)(o,sel);}
}}
unsafe extern "C" fn activated(o:Id,sel:Sel){unsafe{
 if OLD_ACTIVATE!=0 as Id{transmute::<Id,ZeroArg>(OLD_ACTIVATE)(o,sel);}
 prime_manual(ivar(o,b"_pictureInPictureController\0" as *const u8));
}}
unsafe fn mark_user(){unsafe{let flag=dlsym(18446744073709551614usize as Id,b"FromUser\0" as *const u8);if flag!=0 as Id{*flag=1;}}}

unsafe fn manual_press(o:Id,sel:Sel,sender:Id,old:Id){unsafe{
 if pref(b"YouPiPEnabled\0" as *const u8){
  let controller=controller_for_overlay(o);let pip=ivar(controller,b"_pipController\0" as *const u8);
  let mut av=av_for_controller(controller);let mut prepared=false;
  prime_manual(av);
  if responds(av,b"isPictureInPictureActive\0" as *const u8)&&b0(av,s(b"isPictureInPictureActive\0" as *const u8)){
   if responds(av,b"stopPictureInPicture\0" as *const u8){m0(av,s(b"stopPictureInPicture\0" as *const u8));status(b"stopped-by-button\0" as *const u8);return;}
  }
  // The modern player may not create its AVKit controller until activation.
  // Prepare through the real player command; never fake platform eligibility.
  if (!responds(av,b"isPictureInPicturePossible\0" as *const u8)||!b0(av,s(b"isPictureInPicturePossible\0" as *const u8)))&&responds(pip,b"activatePiPController\0" as *const u8){
   mark_user();m0(pip,s(b"activatePiPController\0" as *const u8));prepared=true;
   av=av_for_controller(controller);prime_manual(av);
   if responds(av,b"isPictureInPictureActive\0" as *const u8)&&b0(av,s(b"isPictureInPictureActive\0" as *const u8)){status(b"active-after-player-activation\0" as *const u8);return;}
  }
  if responds(av,b"isPictureInPicturePossible\0" as *const u8)&&b0(av,s(b"isPictureInPicturePossible\0" as *const u8))&&responds(av,b"startPictureInPicture\0" as *const u8){
   mark_user();m0(av,s(b"startPictureInPicture\0" as *const u8));status(b"requested-avkit-start\0" as *const u8);return;
  }
  if prepared{status(b"requested-player-activation-awaiting-avkit\0" as *const u8);return;}
  if responds(controller,b"maybeTogglePictureInPicture\0" as *const u8){
   mark_user();m0(controller,s(b"maybeTogglePictureInPicture\0" as *const u8));status(b"requested-player-toggle\0" as *const u8);return;
  }
  status(if controller==0 as Id{b"controller-not-found\0" as *const u8}else{b"avkit-not-ready\0" as *const u8});
 }
 if old!=0 as Id{transmute::<Id,OneArg>(old)(o,sel,sender);}
}}
unsafe extern "C" fn overlay_press(o:Id,sel:Sel,sender:Id){unsafe{manual_press(o,sel,sender,OLD_OVERLAY);}}
unsafe extern "C" fn inline_press(o:Id,sel:Sel,sender:Id){unsafe{manual_press(o,sel,sender,OLD_INLINE);}}
unsafe extern "C" fn install_after_youpip(_context:Id){unsafe{
 let av=cls(b"AVPictureInPictureController\0" as *const u8);
 hook(av,b"setCanStartPictureInPictureAutomaticallyFromInline:\0" as *const u8,inline_auto as Id,&raw mut OLD_INLINE_AUTO);
 hook(av,b"setCanStartAutomaticallyWhenEnteringBackground:\0" as *const u8,background_auto as Id,&raw mut OLD_BACKGROUND_AUTO);
 hook(av,b"canStartPictureInPictureAutomaticallyFromInline\0" as *const u8,get_inline_auto as Id,&raw mut OLD_AV_GET_AUTO);
 hook(cls(b"YTPlayerPIPController\0" as *const u8),b"appWillResignActive\0" as *const u8,resign as Id,&raw mut OLD_RESIGN);
 hook(cls(b"MLPIPControllerImpl\0" as *const u8),b"activatePiPController\0" as *const u8,activated as Id,&raw mut OLD_ACTIVATE);

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

 if !pref(b"PersonalManualPiPFix1\0" as *const u8){
  put(b"YouPiPEnabled\0" as *const u8,true);put(b"PiPActivationMethodKey\0" as *const u8,true);
  put(b"PiPActivationMethod2Key\0" as *const u8,false);put(b"PiPAllActivationMethodKey\0" as *const u8,false);
  put(b"CompatibilityModeKey\0" as *const u8,false);put(b"PersonalManualPiPFix1\0" as *const u8,true);
 }
 hook(cls(b"YTIPlayabilityStatus\0" as *const u8),b"isPlayableInBackground\0" as *const u8,personal_background as Id,&raw mut OLD_PLAYABILITY);
 hook(cls(b"MLVideo\0" as *const u8),b"playableInBackground\0" as *const u8,personal_background as Id,&raw mut OLD_MLVIDEO);
 let main=dlsym(18446744073709551614usize as Id,b"_dispatch_main_q\0" as *const u8);
 if main!=0 as Id{dispatch_async_f(main,0 as Id,install_after_youpip);}
 m0(pool,s(b"drain\0" as *const u8));
}}
#[used]#[unsafe(link_section="__DATA,__mod_init_func")]static INITIALIZE:unsafe extern "C" fn()=personal_playback_initialize;
