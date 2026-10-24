#!/usr/bin/env python3
"""Create a separately named, ad-hoc-signed macOS test application; never replace an existing app."""
import argparse
import plistlib
from pathlib import Path
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('built_app', type=Path)
    parser.add_argument('output_app', type=Path, help='New path ending in .app; must not exist')
    args = parser.parse_args()
    source, dest = args.built_app.resolve(), args.output_app.resolve()
    if sys.platform != 'darwin':
        parser.error('Run on macOS.')
    if not (source / 'Contents/MacOS/Sunshine').is_file():
        parser.error('Expected the built Sunshine.app.')
    if not (source / 'Contents/Resources/assets/web/index.html').is_file():
        parser.error('Web assets missing: build web-ui and copy build/assets into Contents/Resources/assets first.')
    if dest.exists() or dest.suffix != '.app':
        parser.error('Output must be a new .app path; an existing app will not be overwritten.')
    if dest.is_relative_to(source):
        parser.error('Output cannot be inside the source application.')
    subprocess.run(['ditto', str(source), str(dest)], check=True)
    plist = dest / 'Contents/Info.plist'
    info = plistlib.loads(plist.read_bytes())
    info.update(CFBundleIdentifier='io.github.aloereed.sunshine-pen-touch',
                CFBundleName='Sunshine Pen Touch', CFBundleDisplayName='Sunshine Pen Touch')
    plist.write_bytes(plistlib.dumps(info))
    subprocess.run(['codesign', '--force', '--deep', '--sign', '-', str(dest)], check=True)
    subprocess.run(['codesign', '--verify', '--deep', '--strict', str(dest)], check=True)
    print(f'Staged: {dest}')
    print('Nothing was started. Grant Accessibility and Screen Recording to this app, then follow docs/INSTALL.md.')


if __name__ == '__main__':
    main()
