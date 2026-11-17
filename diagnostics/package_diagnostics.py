from pathlib import Path
import runpy,sys
# Reuse the already audited Mach-O injection and ZIP/member-preservation implementation.
source=Path(__file__).resolve().parents[1]/'tools/package_duo.py'
text=source.read_text().replace('DuoWatchLayout.dylib','LayoutDiagnostics.dylib')
text=text.replace('4ad31f12f9008ad233cbfadc59e4a0796133d88fec7957a545d6daf627b19044','db62288f7fb34509f7395e6848001b0aa123418dc370cf98ab1e564c75fce09f')
exec(compile(text,str(source),'exec'),{'__name__':'__main__'})
