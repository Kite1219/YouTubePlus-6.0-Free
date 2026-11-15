"""Restore historical script paths into an ignored work folder; no downloads."""
import argparse, hashlib, json, shutil, zipfile
from pathlib import Path

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--backup',type=Path,help='Optional complete development backup ZIP from the private release')
    parser.add_argument('--output',type=Path,default=Path('.work'))
    args=parser.parse_args()
    repo=Path(__file__).resolve().parents[1]
    output=args.output.resolve()
    if output.exists() and any(output.iterdir()):parser.error('Output must be empty; choose a new folder')
    if args.backup:
        expected='87bcd3fc3a3582d8c39da41d73e247ea20a5afe2758d87060ca137ee373c568c'
        with args.backup.open('rb') as f:actual=hashlib.file_digest(f,'sha256').hexdigest()
        if actual!=expected:parser.error('Backup checksum mismatch')
        with zipfile.ZipFile(args.backup) as z:
            for member in z.infolist():
                target=(output/member.filename).resolve()
                if not target.is_relative_to(output):parser.error('Unsafe archive path')
            z.extractall(output)
    mapping=json.loads((repo/'tools/workspace-map.json').read_text())
    for source,destination in mapping.items():
        target=output/destination
        if not target.resolve().is_relative_to(output):parser.error('Unsafe map path')
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copyfile(repo/source,target)
    print('Prepared historical workspace:',output)
    print('Run historical scripts from that directory. No build or publication was started.')
    if not args.backup:print('Binary inputs are absent; restore the release backup before packaging.')

if __name__=='__main__':main()

