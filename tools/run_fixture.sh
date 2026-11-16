#!/bin/bash
set -euxo pipefail
mkdir -p build/Fixture.app
SDK=$(xcrun --sdk iphonesimulator --show-sdk-path)
ARCH=$(uname -m)
xcrun --sdk iphonesimulator clang -target "$ARCH-apple-ios16.0-simulator" -isysroot "$SDK" -fobjc-arc -DTP_FIXTURE=1 src/DuoWatchLayout.m tests/DuoWatchFixture.m -framework UIKit -framework Foundation -framework CoreGraphics -framework QuartzCore -o build/Fixture.app/Fixture
cat > build/Fixture.app/Info.plist <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?><!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd"><plist version="1.0"><dict><key>CFBundleExecutable</key><string>Fixture</string><key>CFBundleIdentifier</key><string>local.youtubeplus.duofixture</string><key>CFBundleName</key><string>Fixture</string><key>CFBundleVersion</key><string>1</string><key>CFBundleShortVersionString</key><string>1</string><key>CFBundlePackageType</key><string>APPL</string><key>MinimumOSVersion</key><string>16.0</string><key>UIDeviceFamily</key><array><integer>1</integer></array></dict></plist>
PLIST
codesign -s - build/Fixture.app
DEVICE=$(xcrun simctl list devices available -j | python3 -c 'import json,sys;d=json.load(sys.stdin);keys=sorted(d["devices"],key=lambda k:("iOS-18-5" in k,k),reverse=True);print(next(v["udid"] for k in keys if "iOS" in k for v in d["devices"][k] if "iPhone" in v["name"]))')
xcrun simctl boot "$DEVICE" || true
python3 -u -c 'import subprocess,sys;subprocess.run(["xcrun","simctl","bootstatus",sys.argv[1],"-b"],check=True,timeout=300)' "$DEVICE"
python3 -u -c 'import subprocess,sys;subprocess.run(["xcrun","simctl","install",sys.argv[1],"build/Fixture.app"],check=True,timeout=120)' "$DEVICE"
python3 -u -c 'import subprocess,sys;subprocess.run(["xcrun","simctl","launch","--console",sys.argv[1],"local.youtubeplus.duofixture"],check=True,timeout=90)' "$DEVICE"
CONTAINER=$(xcrun simctl get_app_container "$DEVICE" local.youtubeplus.duofixture data)
cp "$CONTAINER/Documents/fixture.json" build/fixture.json
python3 -c 'import json; r=json.load(open("build/fixture.json"));print(r);assert r["passed"]'
