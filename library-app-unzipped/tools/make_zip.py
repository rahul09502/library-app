import zipfile
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT.parent / 'library_app_for_github.zip'

EXCLUDE_DIRS = {'venv', '.venv', '.git', 'instance', '__pycache__', '.pytest_cache'}
EXCLUDE_FILES = {'library_app_for_github.zip'}

def should_exclude(p: Path):
    # exclude if any part of path matches excluded dirs
    for part in p.parts:
        if part in EXCLUDE_DIRS:
            return True
    if p.name in EXCLUDE_FILES:
        return True
    return False

def main():
    if OUT.exists():
        OUT.unlink()
    with zipfile.ZipFile(OUT, 'w', zipfile.ZIP_DEFLATED) as z:
        for p in ROOT.rglob('*'):
            if should_exclude(p):
                continue
            if p.is_file():
                rel = p.relative_to(ROOT)
                z.write(p, rel)
    print('Created:', OUT)

if __name__ == '__main__':
    main()
