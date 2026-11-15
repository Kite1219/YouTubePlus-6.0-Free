import zipfile
p=r'C:/Users/Kiet/Desktop/Apps/IPAs/21.13.6_YouTubePlus_5.2b4.ipa'
with zipfile.ZipFile(p) as z:
 for n in z.namelist():
  if n.endswith('.dylib') or 'YTLite.bundle/Info.plist' in n: print(n)
