#!/bin/bash
set -euxo pipefail
mkdir -p build/DiagnosticSmoke.app
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
ARCH=$(uname -m)
xcrun --sdk iphonesimulator clang -target "$ARCH-apple-ios17.0-simulator" -isysroot "$SDK" -fobjc-arc -DTP_DIAGNOSTIC_TEST=1 diagnostics/LayoutDiagnostics.m diagnostics/DiagnosticSmoke.m -framework Foundation -framework UIKit -framework QuartzCore -framework CoreGraphics -framework AVFoundation -o build/DiagnosticSmoke.app/DiagnosticSmoke
python3 - <<'PY'
import plistlib
info={'CFBundleExecutable':'DiagnosticSmoke','CFBundleIdentifier':'local.youtubeplus.diagnostics.smoke','CFBundleName':'Diagnostic Smoke','CFBundleVersion':'1','CFBundleShortVersionString':'1','CFBundlePackageType':'APPL','MinimumOSVersion':'17.0','UIDeviceFamily':[1],'UILaunchScreen':{},'UIApplicationSceneManifest':{'UIApplicationSupportsMultipleScenes':False,'UISceneConfigurations':{'UIWindowSceneSessionRoleApplication':[{'UISceneConfigurationName':'Default','UISceneDelegateClassName':'SmokeScene'}]}}}
with open('build/DiagnosticSmoke.app/Info.plist','wb') as f:plistlib.dump(info,f)
PY
codesign -s - build/DiagnosticSmoke.app
xcrun simctl list devices available -j > build/simulator-devices.json
DEVICE=$(python3 - <<'PY'
import json
d=json.load(open('build/simulator-devices.json'));matches=[v for k,vs in d['devices'].items() for v in vs if 'iOS' in k and 'Duo' in v['name']]
assert matches,'No preinstalled iPhone Duo simulator available; no substitute device is claimed'
print(sorted(matches,key=lambda v:v['state']!='Booted')[0]['udid'])
PY
)
xcrun simctl boot "$DEVICE" || true
python3 -u -c 'import subprocess,sys;subprocess.run(["xcrun","simctl","bootstatus",sys.argv[1],"-b"],check=True,timeout=300)' "$DEVICE"
python3 -u -c 'import subprocess,sys;subprocess.run(["xcrun","simctl","install",sys.argv[1],"build/DiagnosticSmoke.app"],check=True,timeout=120)' "$DEVICE"
xcrun simctl launch "$DEVICE" local.youtubeplus.diagnostics.smoke
CONTAINER=$(xcrun simctl get_app_container "$DEVICE" local.youtubeplus.diagnostics.smoke data)
python3 -u - "$CONTAINER/Documents/smoke.json" <<'PY'
import sys,time,json,pathlib,shutil
p=pathlib.Path(sys.argv[1]);deadline=time.monotonic()+90
while not p.exists() and time.monotonic()<deadline:time.sleep(1)
assert p.exists(),'Diagnostic smoke app did not produce its report'
r=json.loads(p.read_text());print(json.dumps(r,indent=2));shutil.copyfile(p,'build/diagnostic-smoke.json');assert r['passed']
PY
xcrun simctl io "$DEVICE" screenshot build/diagnostic-smoke.png
