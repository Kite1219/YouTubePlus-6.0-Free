from pathlib import Path
r=Path('ytplus-analysis/free-player-audit');(r/'PersonalPlayback-test3.rs').write_bytes((r/'PersonalPlayback.rs').read_bytes());(r/'PersonalPlayback-test3.dylib').write_bytes((r/'PersonalPlayback.dylib').read_bytes())
s=(r/'PersonalPlayback.rs').read_text()
s=s.replace('static mut OLD_OVERLAY:Id=0 as Id;static mut OLD_INLINE:Id=0 as Id;','''static mut OLD_OVERLAY:Id=0 as Id;static mut OLD_INLINE:Id=0 as Id;
static mut OLD_RESIGN:Id=0 as Id;static mut OLD_INLINE_AUTO:Id=0 as Id;static mut OLD_BACKGROUND_AUTO:Id=0 as Id;
static mut OLD_AV_GET_AUTO:Id=0 as Id;static mut OLD_ACTIVATE:Id=0 as Id;
type ZeroArg=unsafe extern "C" fn(Id,Sel);type BoolArg=unsafe extern "C" fn(Id,Sel,bool);''')
start=s.index('unsafe fn controller_for_overlay(');end=s.index('unsafe extern "C" fn overlay_press(',start)
s=s[:start]+r'''
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
  let controller=controller_for_overlay(o);let av=av_for_controller(controller);
  if av!=0 as Id{
   prime_manual(av);
   if responds(av,b"isPictureInPictureActive\0" as *const u8)&&b0(av,s(b"isPictureInPictureActive\0" as *const u8)){
    if responds(av,b"stopPictureInPicture\0" as *const u8){m0(av,s(b"stopPictureInPicture\0" as *const u8));status(b"stopped-by-button\0" as *const u8);return;}
   }
   if responds(av,b"isPictureInPicturePossible\0" as *const u8)&&b0(av,s(b"isPictureInPicturePossible\0" as *const u8))&&responds(av,b"startPictureInPicture\0" as *const u8){
    mark_user();m0(av,s(b"startPictureInPicture\0" as *const u8));status(b"requested-avkit-start\0" as *const u8);return;
   }
  }
  // A current selector is a fallback, not proof that the request succeeded.
  if responds(controller,b"maybeTogglePictureInPicture\0" as *const u8){
   mark_user();m0(controller,s(b"maybeTogglePictureInPicture\0" as *const u8));status(b"requested-player-toggle\0" as *const u8);return;
  }
  status(if controller==0 as Id{b"controller-not-found\0" as *const u8}else{b"avkit-not-ready\0" as *const u8});
 }
 if old!=0 as Id{transmute::<Id,OneArg>(old)(o,sel,sender);}
}}
''' + s[end:]
# usize subtraction is used only to bound responder walking.
s=s.replace('#[rustc_intrinsic] pub unsafe fn transmute', '#[lang="sub"]pub trait Sub<Rhs=Self>{type Output;fn sub(self,rhs:Rhs)->Self::Output;}\nimpl Sub for usize{type Output=Self;fn sub(self,rhs:Self)->Self{self-rhs}}\n#[rustc_intrinsic] pub unsafe fn transmute')
needle='unsafe extern "C" fn install_after_youpip(_context:Id){unsafe{'
s=s.replace(needle,needle+r'''
 let av=cls(b"AVPictureInPictureController\0" as *const u8);
 hook(av,b"setCanStartPictureInPictureAutomaticallyFromInline:\0" as *const u8,inline_auto as Id,&raw mut OLD_INLINE_AUTO);
 hook(av,b"setCanStartAutomaticallyWhenEnteringBackground:\0" as *const u8,background_auto as Id,&raw mut OLD_BACKGROUND_AUTO);
 hook(av,b"canStartPictureInPictureAutomaticallyFromInline\0" as *const u8,get_inline_auto as Id,&raw mut OLD_AV_GET_AUTO);
 hook(cls(b"YTPlayerPIPController\0" as *const u8),b"appWillResignActive\0" as *const u8,resign as Id,&raw mut OLD_RESIGN);
 hook(cls(b"MLPIPControllerImpl\0" as *const u8),b"activatePiPController\0" as *const u8,activated as Id,&raw mut OLD_ACTIVATE);
''')
(r/'PersonalPlayback.rs').write_text(s)
