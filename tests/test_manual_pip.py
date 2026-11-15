import ctypes as C,json,unittest
from pathlib import Path
R=Path(__file__).parent;P=C.c_void_p
F1=C.CFUNCTYPE(P,P);F2=C.CFUNCTYPE(P,P,P);FM=C.CFUNCTYPE(P,P,P,P,P)
FH=C.CFUNCTYPE(None,P,P,P,P);FD=C.CFUNCTYPE(None,P,P,P);OLD=C.CFUNCTYPE(None,P,P,P);OLDB=C.CFUNCTYPE(C.c_bool,P,P);OLD0=C.CFUNCTYPE(None,P,P);OLDA=C.CFUNCTYPE(None,P,P,C.c_bool)
d=C.CDLL(str((R/'PersonalPlayback-test4.dll').resolve()));d.test_callback.argtypes=[C.c_size_t,P]
d.personal_background.argtypes=[P,P];d.personal_background.restype=C.c_bool
d.test_disabled.argtypes=[P,P];d.test_disabled.restype=C.c_bool
d.test_press.argtypes=[P,P,P];d.test_update.argtypes=[P,P,P]
d.test_resign.argtypes=[P,P];d.test_set_auto.argtypes=[P,P,C.c_bool,C.c_size_t];d.test_get_auto.argtypes=[P,P];d.test_get_auto.restype=C.c_bool;d.test_activate.argtypes=[P,P]
KEEP=[]
class Runtime:
 def __init__(self,prefs=None):
  self.prefs=dict(prefs or {});self.ids={};self.names={};self.next=10000;self.callbacks=[];self.queue=[];self.hooks=[];self.old=[];self.messages=[];self.hidden=[];self.flag=C.c_ubyte(0);self.flag_present=True;self.modern=True;self.links={(1000,'_eventsDelegate'):1100,(1100,'parent'):1200,(1200,'_playbackController'):1300,(1300,'_playerPIPController'):1400};self.errors=[];self.missing=set();self.av_possible=True;self.av_active=False;self.activation_supported=True;self.prepare_ready=True;self.prepare_starts=False;self.auto_setters=[];self.diagnostics={};self.links[(1400,'_pipController')]=1500;self.links[(1500,'_pictureInPictureController')]=1600
  def cb(kind,fn):
   def safe(*a):
    try:return fn(*a)
    except Exception as e:self.errors.append(repr(e));return 0
   f=kind(safe);self.callbacks.append(f);return f
  self.old3=cb(OLD,lambda o,s,a:self.old.append(self.names.get(s,s)))
  self.oldbool=cb(OLDB,lambda o,s:True)
  self.old0=cb(OLD0,lambda o,s:self.old.append(self.names.get(s,s)))
  self.olda=cb(OLDA,lambda o,s,v:self.auto_setters.append((self.names.get(s),bool(v))))
  cbs=[cb(F1,lambda n:self.intern('class:'+C.string_at(n).decode())),cb(F1,lambda n:self.intern(C.string_at(n).decode())),cb(FM,self.message),cb(F1,lambda o:(o or 0)+1000000),cb(F2,lambda c,s:0 if self.names.get(s) in self.missing else 1),cb(F2,lambda c,n:self.intern(C.string_at(n).decode())),cb(F2,lambda o,v:self.links.get((o,self.names.get(v)),0)),cb(FH,self.hook),cb(F2,self.symbol),cb(FD,lambda q,c,f:self.queue.append((c,f)))]
  for i,f in enumerate(cbs):d.test_callback(i,f)
  KEEP.append(self)
 def intern(self,s):
  if s not in self.ids:self.next+=1;self.ids[s]=self.next;self.names[self.next]=s
  return self.ids[s]
 def symbol(self,h,n):
  s=C.string_at(n).decode()
  if s=='_dispatch_main_q':return 99
  if s=='FromUser' and self.flag_present:return C.addressof(self.flag)
  return 0
 def hook(self,c,s,f,old):
  name=self.names[s];self.hooks.append(name);C.cast(old,C.POINTER(P))[0]=C.cast(self.oldbool if name in ['isPiPDisabled','canStartPictureInPictureAutomaticallyFromInline'] else self.old0 if name in ['appWillResignActive','activatePiPController'] else self.olda if name.startswith('setCanStart') else self.old3,P).value
 def message(self,o,s,a,b):
  sel=self.names.get(s,'?');self.messages.append((o,sel,a,b))
  if sel=='stringWithUTF8String:':return self.intern(C.string_at(a).decode())
  if sel=='standardUserDefaults':return 100
  if sel=='boolForKey:':return int(self.prefs.get(self.names.get(a),False))
  if sel=='setBool:forKey:':self.prefs[self.names.get(b)]=bool(a);return 0
  if sel=='setObject:forKey:':self.diagnostics[self.names.get(b)]=self.names.get(a);return 0
  if sel=='respondsToSelector:':
   name=self.names.get(a)
   if name=='activatePiPController':return int(self.activation_supported and o==1500)
   if name=='maybeTogglePictureInPicture':return int(self.modern and o==1400)
   return int(name in ['parentViewController','button:forOverlay:','setHidden:','delegate','nextResponder','setCanStartPictureInPictureAutomaticallyFromInline:','setCanStartAutomaticallyWhenEnteringBackground:','isPictureInPictureActive','isPictureInPicturePossible','startPictureInPicture','stopPictureInPicture'])
  if sel=='nextResponder':return self.links.get((o,'responder'),0)
  if sel=='isPictureInPictureActive':return int(self.av_active)
  if sel=='isPictureInPicturePossible':return int(self.av_possible)
  if sel.startswith('setCanStart'):self.auto_setters.append((sel,bool(a)));return 0
  if sel=='activatePiPController':
   if self.prepare_ready:self.links[(1500,'_pictureInPictureController')]=1600;self.av_possible=True
   if self.prepare_starts:self.av_active=True
   return 0
  if sel=='startPictureInPicture':self.av_active=True;return 0
  if sel=='stopPictureInPicture':self.av_active=False;return 0
  if sel=='parentViewController':return self.links.get((o,'parent'),0)
  if sel=='delegate':return self.links.get((o,'delegate'),0)
  if sel=='button:forOverlay:':return 700 if self.names.get(a)=='pip' else 0
  if sel=='setHidden:':self.hidden.append((o,bool(a)));return 0
  if sel=='maybeTogglePictureInPicture':return 0
  if sel=='alloc':return 400
  if sel=='init':return o
  if sel=='drain':return 0
  raise ValueError(sel)
 def initialize(self):
  d.personal_playback_initialize()
  for context,fn in self.queue: C.CFUNCTYPE(None,P)(fn)(context)
  self.queue=[]
  assert not self.errors,self.errors
class Tests(unittest.TestCase):
 def setUp(self):self.keep_start=len(KEEP)
 def tearDown(self):
  for runtime in KEEP[self.keep_start:]:self.assertFalse(runtime.errors,runtime.errors)
 def rt(self,prefs=None):r=Runtime(prefs);r.initialize();return r
 def test_manual_defaults_and_background_on(self):
  r=self.rt();self.assertTrue(r.prefs['YouPiPEnabled']);self.assertTrue(r.prefs['PiPActivationMethodKey']);self.assertFalse(r.prefs['PiPAllActivationMethodKey']);self.assertFalse(r.prefs['CompatibilityModeKey']);self.assertTrue(d.personal_background(1,2))
 def test_migration_preserves_later_user_choices(self):
  r=self.rt({'PersonalPlaybackMigration1':True,'PersonalManualPiPFix1':True,'backgroundPlayback':False,'PiPAllActivationMethodKey':True});self.assertFalse(d.personal_background(1,2));self.assertTrue(r.prefs['PiPAllActivationMethodKey'])
 def test_background_switch_is_live(self):
  r=self.rt();r.prefs['backgroundPlayback']=False;self.assertFalse(d.personal_background(1,2));r.prefs['backgroundPlayback']=True;self.assertTrue(d.personal_background(1,2))
 def test_manual_press_uses_ready_avkit_once(self):
  r=self.rt();d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.flag.value,1);self.assertEqual(sum(x[1]=='startPictureInPicture' for x in r.messages),1);self.assertEqual(sum(x[1]=='maybeTogglePictureInPicture' for x in r.messages),0);self.assertNotIn('didPressPiP:',r.old);self.assertFalse(r.errors)
 def test_ready_avkit_does_not_need_modern_player_method(self):
  r=self.rt();r.modern=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,[]);self.assertTrue(r.av_active)
 def test_missing_player_chain_falls_back(self):
  r=self.rt();r.links={};d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:'])
 def test_ready_avkit_does_not_require_legacy_export(self):
  r=self.rt();r.flag_present=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,[]);self.assertTrue(r.av_active)
 def test_disabled_youpip_preserves_original(self):
  r=self.rt();r.prefs['YouPiPEnabled']=False;self.assertTrue(d.test_disabled(1,2));d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:'])
 def test_enabled_youpip_removes_old_veto(self):
  r=self.rt();self.assertFalse(d.test_disabled(1,2))
 def test_only_legacy_pip_button_hidden_after_original_update(self):
  r=self.rt();d.test_update(50,r.intern('updateButtonsForOverlay:'),1000);self.assertEqual(r.old,['updateButtonsForOverlay:']);self.assertEqual(r.hidden,[(700,True)]);self.assertFalse(r.errors)
 def test_disabled_youpip_keeps_old_button(self):
  r=self.rt();r.prefs['YouPiPEnabled']=False;d.test_update(50,r.intern('updateButtonsForOverlay:'),1000);self.assertEqual(r.hidden,[])
 def test_missing_methods_skipped(self):
  r=Runtime();r.missing={'playableInBackground','didPressPiP:'};r.initialize();self.assertNotIn('playableInBackground',r.hooks);self.assertNotIn('didPressPiP:',r.hooks)
 def test_wrapper_controller_in_parent_chain(self):
  r=self.rt();r.links[(1100,'parent')]=1150;r.links[(1150,'parent')]=1200;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertTrue(r.av_active);self.assertFalse(r.old)
 def test_parent_cycle_is_bounded(self):
  r=self.rt();r.links={(1000,'_eventsDelegate'):1100,(1100,'parent'):1100};d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:']);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'controller-not-found')
 def test_manual_press_toggles_active_pip_off(self):
  r=self.rt();r.av_active=True;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertFalse(r.av_active);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'stopped-by-button')
 def test_unready_avkit_uses_player_once(self):
  r=self.rt();r.av_possible=False;r.activation_supported=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(sum(x[1]=='maybeTogglePictureInPicture' for x in r.messages),1);self.assertFalse(r.old);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'requested-player-toggle')
 def test_unready_avkit_without_player_selector_falls_back(self):
  r=self.rt();r.av_possible=False;r.modern=False;r.activation_supported=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:']);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'avkit-not-ready')
 def test_exact_current_resign_selector_is_hooked(self):
  r=self.rt();self.assertIn('appWillResignActive',r.hooks);self.assertNotIn('appWillResignActive:',r.hooks)
 def test_home_does_not_start_pip_in_button_mode(self):
  r=self.rt();d.test_resign(1400,r.intern('appWillResignActive'));self.assertNotIn('appWillResignActive',r.old);self.assertFalse(r.av_active);self.assertEqual(sum(x[1] in ['startPictureInPicture','maybeTogglePictureInPicture'] for x in r.messages),0)
 def test_home_does_not_stop_manually_started_pip(self):
  r=self.rt();r.av_active=True;d.test_resign(1400,r.intern('appWillResignActive'));self.assertTrue(r.av_active)
 def test_automatic_mode_forwards_resign_to_original(self):
  r=self.rt();r.prefs['PiPAllActivationMethodKey']=True;d.test_resign(1400,r.intern('appWillResignActive'));self.assertIn('appWillResignActive',r.old)
 def test_automatic_setters_cannot_enable_automatic_pip_in_button_mode(self):
  r=self.rt();r.auto_setters=[];d.test_set_auto(1600,r.intern('setCanStartPictureInPictureAutomaticallyFromInline:'),True,0);d.test_set_auto(1600,r.intern('setCanStartAutomaticallyWhenEnteringBackground:'),True,1);self.assertEqual([x[1] for x in r.auto_setters],[False,False]);self.assertFalse(d.test_get_auto(1600,r.intern('canStartPictureInPictureAutomaticallyFromInline')))
 def test_unrestricted_mode_preserves_automatic_setters(self):
  r=self.rt();r.prefs['PiPAllActivationMethodKey']=True;r.auto_setters=[];d.test_set_auto(1600,r.intern('setCanStartPictureInPictureAutomaticallyFromInline:'),True,0);self.assertEqual(r.auto_setters[-1][1],True);self.assertTrue(d.test_get_auto(1600,r.intern('canStartPictureInPictureAutomaticallyFromInline')))
 def test_new_controller_is_primed_after_original_activation(self):
  r=self.rt();r.auto_setters=[];d.test_activate(1500,r.intern('activatePiPController'));self.assertIn('activatePiPController',r.old);self.assertEqual([x[1] for x in r.auto_setters],[False,False])
 def test_upgrade_resets_only_pip_mode_once(self):
  r=self.rt({'PersonalPlaybackMigration1':True,'backgroundPlayback':False,'PiPAllActivationMethodKey':True,'CompatibilityModeKey':True});self.assertFalse(r.prefs['backgroundPlayback']);self.assertTrue(r.prefs['PiPActivationMethodKey']);self.assertFalse(r.prefs['PiPAllActivationMethodKey']);self.assertFalse(r.prefs['CompatibilityModeKey']);self.assertTrue(r.prefs['PersonalManualPiPFix1'])
 def test_missing_avkit_controller_is_prepared(self):
  r=self.rt();del r.links[(1500,'_pictureInPictureController')];d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertTrue(r.av_active);self.assertEqual(sum(x[1]=='activatePiPController' for x in r.messages),1);self.assertEqual(sum(x[1]=='startPictureInPicture' for x in r.messages),1)
 def test_player_activation_does_not_toggle_started_pip_off(self):
  r=self.rt();r.av_possible=False;r.prepare_starts=True;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertTrue(r.av_active);self.assertEqual(sum(x[1] in ['stopPictureInPicture','maybeTogglePictureInPicture','startPictureInPicture'] for x in r.messages),0)
 def test_pending_platform_activation_is_not_double_toggled(self):
  r=self.rt();r.av_possible=False;r.prepare_ready=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'requested-player-activation-awaiting-avkit');self.assertEqual(sum(x[1]=='maybeTogglePictureInPicture' for x in r.messages),0)
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));(R/'native-host-tests-test4.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Production Rust hooks compiled for Windows with mocked Objective-C, UIKit and dispatch; not an iOS runtime test'},indent=2));raise SystemExit(not result.wasSuccessful())
