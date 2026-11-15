import zipfile,re
p=r'C:/Users/Kiet/Downloads/YTLite-6.0.zip'
with zipfile.ZipFile(p) as z:
 names=z.namelist()
 print('FILES',len(names))
 print('\n'.join(n for n in names if n.count('/')<=2)[:7000])
 for n in names:
  if n.endswith(('control','Makefile','YTLite.x','Settings.x','README.md')):
   s=z.read(n).decode('utf-8','replace')
   print('\nFILE',n,'BYTES',len(s))
   if n.endswith(('control','Makefile')): print(s[:5000])
   else:
    for line in s.splitlines():
     if re.search(r'duo|YTPPivotTabBarController|YTPLiquidGlass|subscription|5\.2|6\.0|floating',line,re.I): print(line[:500])
