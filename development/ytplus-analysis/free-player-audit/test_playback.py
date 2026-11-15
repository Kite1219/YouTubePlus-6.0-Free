import ctypes as C,json,unittest
from pathlib import Path
R=Path(__file__).parent;P=C.c_void_p
F1=C.CFUNCTYPE(P,P);F2=C.CFUNCTYPE(P,P,P);FM=C.CFUNCTYPE(P,P,P,P,P)
FH=C.CFUNCTYPE(None,P,P,P,P);FD=C.CFUNCTYPE(None,P,P,P);OLD=C.CFUNCTYPE(None,P,P,P);OLDB=C.CFUNCTYPE(C.c_bool,P,P)
d=C.CDLL(str((R/'PersonalPlayback-test.dll').resolve()));d.test_callback.argtypes=[C.c_size_t,P]
d.personal_background.argtypes=[P,P];d.personal_background.restype=C.c_bool
d.test_disabled.argtypes=[P,P];d.test_disabled.restype=C.c_bool
d.test_press.argtypes=[P,P,P];d.test_update.argtypes=[P,P,P]
KEEP=[]
class Runtime:
 def __init__(self,prefs=None):
  self.prefs=dict(prefs or {});self.ids={};self.names={};self.next=10000;self.callbacks=[];self.queue=[];self.hooks=[];self.old=[];self.messages=[];self.hidden=[];self.flag=C.c_ubyte(0);self.flag_present=True;self.modern=True;self.links={(1000,'_eventsDelegate'):1100,(1100,'parent'):1200,(1200,'_playbackController'):1300,(1300,'_playerPIPController'):1400};self.errors=[];self.missing=set()
  def cb(kind,fn):
   def safe(*a):
    try:return fn(*a)
    except Exception as e:self.errors.append(repr(e));return 0
   f=kind(safe);self.callbacks.append(f);return f
  self.old3=cb(OLD,lambda o,s,a:self.old.append(self.names.get(s,s)))
  self.oldbool=cb(OLDB,lambda o,s:True)
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
  name=self.names[s];self.hooks.append(name);C.cast(old,C.POINTER(P))[0]=C.cast(self.oldbool if name=='isPiPDisabled' else self.old3,P).value
 def message(self,o,s,a,b):
  sel=self.names.get(s,'?');self.messages.append((o,sel,a,b))
  if sel=='stringWithUTF8String:':return self.intern(C.string_at(a).decode())
  if sel=='standardUserDefaults':return 100
  if sel=='boolForKey:':return int(self.prefs.get(self.names.get(a),False))
  if sel=='setBool:forKey:':self.prefs[self.names.get(b)]=bool(a);return 0
  if sel=='respondsToSelector:':
   name=self.names.get(a)
   if name=='maybeTogglePictureInPicture':return int(self.modern and o==1400)
   return int(name in ['parentViewController','button:forOverlay:','setHidden:','delegate'])
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
 def rt(self,prefs=None):r=Runtime(prefs);r.initialize();return r
 def test_manual_defaults_and_background_on(self):
  r=self.rt();self.assertTrue(r.prefs['YouPiPEnabled']);self.assertTrue(r.prefs['PiPActivationMethodKey']);self.assertFalse(r.prefs['PiPAllActivationMethodKey']);self.assertFalse(r.prefs['CompatibilityModeKey']);self.assertTrue(d.personal_background(1,2))
 def test_migration_preserves_later_user_choices(self):
  r=self.rt({'PersonalPlaybackMigration1':True,'backgroundPlayback':False,'PiPAllActivationMethodKey':True});self.assertFalse(d.personal_background(1,2));self.assertTrue(r.prefs['PiPAllActivationMethodKey'])
 def test_background_switch_is_live(self):
  r=self.rt();r.prefs['backgroundPlayback']=False;self.assertFalse(d.personal_background(1,2));r.prefs['backgroundPlayback']=True;self.assertTrue(d.personal_background(1,2))
 def test_manual_press_uses_modern_player_once(self):
  r=self.rt();d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.flag.value,1);self.assertEqual(sum(x[1]=='maybeTogglePictureInPicture' for x in r.messages),1);self.assertNotIn('didPressPiP:',r.old);self.assertFalse(r.errors)
 def test_missing_modern_method_falls_back(self):
  r=self.rt();r.modern=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:']);self.assertEqual(r.flag.value,0)
 def test_missing_player_chain_falls_back(self):
  r=self.rt();r.links={};d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:'])
 def test_missing_youpip_flag_falls_back(self):
  r=self.rt();r.flag_present=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:'])
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
if __name__=='__main__':
 result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Tests));(R/'native-host-tests.json').write_text(json.dumps({'tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'scope':'Production Rust hooks compiled for Windows with mocked Objective-C, UIKit and dispatch; not an iOS runtime test'},indent=2));raise SystemExit(not result.wasSuccessful())
