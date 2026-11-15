import zipfile,plistlib,re,json
from pathlib import Path
p=Path('ytplus-analysis/YouTubePlus-Personal-6.0-test.1-unsigned.ipa')
with zipfile.ZipFile(p) as z:
 names=z.namelist()
 print('PIP NAMED FILES',*[n for n in names if re.search('yourpip|pictureinpicture|/[^/]*pip[^/]*\\.(dylib|bundle|framework)',n,re.I)],sep='\n')
 for n in names:
  if n.endswith('en.lproj/Localizable.strings') and 'YTLite.bundle/' in n:
   d=plistlib.loads(z.read(n));print('ENGLISH SETTINGS',n)
   for k,v in d.items():
    if re.search(r'yourpip|\bpip\b|picture.?in.?picture',k+' '+str(v),re.I):print(k,':',v)
 b=z.read('Payload/YouTube.app/Frameworks/YTLite.dylib')
 print('DYLIB RELEVANT STRINGS')
 for m in re.finditer(rb'[\x20-\x7e]{5,}',b):
  s=m[0].decode()
  if re.search(r'yourpip|adaptivepip|pipsettings|pictureinpicture|enablepip|disablepip|piptoggle',s,re.I):print(s[:220])
 print('FRAMEWORK LIBRARIES')
 for n in names:
  if n.endswith('.dylib') and n.count('/')==3:print(n)
c=json.loads(Path('ytplus-analysis/subscription-audit/objc.json').read_text())
for a in c:
 methods=[m['name'] for m in a['methods'] if re.search('adaptivepip|pipsettings|togglepip',m['name'],re.I)]
 if methods:print('CLASS',a['name'],methods)
