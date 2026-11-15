from pathlib import Path
r=Path('ytplus-analysis/free-player-audit');s=(r/'test_playback.py').read_text().replace('PersonalPlayback-test.dll','PersonalPlayback-test4.dll')
s=s.replace('OLDB=C.CFUNCTYPE(C.c_bool,P,P)','OLDB=C.CFUNCTYPE(C.c_bool,P,P);OLD0=C.CFUNCTYPE(None,P,P);OLDA=C.CFUNCTYPE(None,P,P,C.c_bool)')
s=s.replace('KEEP=[]',"d.test_resign.argtypes=[P,P];d.test_set_auto.argtypes=[P,P,C.c_bool,C.c_size_t];d.test_get_auto.argtypes=[P,P];d.test_get_auto.restype=C.c_bool;d.test_activate.argtypes=[P,P]\nKEEP=[]")
s=s.replace('self.errors=[];self.missing=set()','self.errors=[];self.missing=set();self.av_possible=True;self.av_active=False;self.auto_setters=[];self.diagnostics={};self.links[(1400,\'_pipController\')]=1500;self.links[(1500,\'_pictureInPictureController\')]=1600')
s=s.replace("self.oldbool=cb(OLDB,lambda o,s:True)","self.oldbool=cb(OLDB,lambda o,s:True)\n  self.old0=cb(OLD0,lambda o,s:self.old.append(self.names.get(s,s)))\n  self.olda=cb(OLDA,lambda o,s,v:self.auto_setters.append((self.names.get(s),bool(v))))")
s=s.replace("C.cast(old,C.POINTER(P))[0]=C.cast(self.oldbool if name=='isPiPDisabled' else self.old3,P).value", "C.cast(old,C.POINTER(P))[0]=C.cast(self.oldbool if name in ['isPiPDisabled','canStartPictureInPictureAutomaticallyFromInline'] else self.old0 if name in ['appWillResignActive','activatePiPController'] else self.olda if name.startswith('setCanStart') else self.old3,P).value")
s=s.replace("if sel=='respondsToSelector:':", "if sel=='setObject:forKey:':self.diagnostics[self.names.get(b)]=self.names.get(a);return 0\n  if sel=='respondsToSelector:':")
s=s.replace("['parentViewController','button:forOverlay:','setHidden:','delegate']", "['parentViewController','button:forOverlay:','setHidden:','delegate','nextResponder','setCanStartPictureInPictureAutomaticallyFromInline:','setCanStartAutomaticallyWhenEnteringBackground:','isPictureInPictureActive','isPictureInPicturePossible','startPictureInPicture','stopPictureInPicture']")
s=s.replace("if sel=='parentViewController':", "if sel=='nextResponder':return self.links.get((o,'responder'),0)\n  if sel=='isPictureInPictureActive':return int(self.av_active)\n  if sel=='isPictureInPicturePossible':return int(self.av_possible)\n  if sel.startswith('setCanStart'):self.auto_setters.append((sel,bool(a)));return 0\n  if sel=='startPictureInPicture':self.av_active=True;return 0\n  if sel=='stopPictureInPicture':self.av_active=False;return 0\n  if sel=='parentViewController':")
s=s.replace('class Tests(unittest.TestCase):','class Tests(unittest.TestCase):\n def setUp(self):self.keep_start=len(KEEP)\n def tearDown(self):\n  for runtime in KEEP[self.keep_start:]:self.assertFalse(runtime.errors,runtime.errors)')
s=s.replace("self.assertEqual(sum(x[1]=='maybeTogglePictureInPicture' for x in r.messages),1)","self.assertEqual(sum(x[1]=='startPictureInPicture' for x in r.messages),1);self.assertEqual(sum(x[1]=='maybeTogglePictureInPicture' for x in r.messages),0)")
s=s.replace('test_manual_press_uses_modern_player_once','test_manual_press_uses_ready_avkit_once')
s=s.replace('test_missing_modern_method_falls_back','test_ready_avkit_does_not_need_modern_player_method')
s=s.replace("r.modern=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:']);self.assertEqual(r.flag.value,0)","r.modern=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,[]);self.assertTrue(r.av_active)")
s=s.replace('test_missing_youpip_flag_falls_back','test_ready_avkit_does_not_require_legacy_export')
s=s.replace("r.flag_present=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:'])","r.flag_present=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,[]);self.assertTrue(r.av_active)")
loc=s.index("if __name__=='__main__':")
s=s[:loc]+''' def test_wrapper_controller_in_parent_chain(self):
  r=self.rt();r.links[(1100,'parent')]=1150;r.links[(1150,'parent')]=1200;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertTrue(r.av_active);self.assertFalse(r.old)
 def test_parent_cycle_is_bounded(self):
  r=self.rt();r.links={(1000,'_eventsDelegate'):1100,(1100,'parent'):1100};d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:']);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'controller-not-found')
 def test_manual_press_toggles_active_pip_off(self):
  r=self.rt();r.av_active=True;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertFalse(r.av_active);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'stopped-by-button')
 def test_unready_avkit_uses_player_once(self):
  r=self.rt();r.av_possible=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(sum(x[1]=='maybeTogglePictureInPicture' for x in r.messages),1);self.assertFalse(r.old);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'requested-player-toggle')
 def test_unready_avkit_without_player_selector_falls_back(self):
  r=self.rt();r.av_possible=False;r.modern=False;d.test_press(1000,r.intern('didPressPiP:'),1700);self.assertEqual(r.old,['didPressPiP:']);self.assertEqual(r.diagnostics['PersonalPlaybackLastPiPResult'],'avkit-not-ready')
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
''' +s[loc:]
s=s.replace("native-host-tests.json","native-host-tests-test4.json")
(r/'test_manual_pip.py').write_text(s)
