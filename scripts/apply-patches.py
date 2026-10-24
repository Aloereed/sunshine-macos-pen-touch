#!/usr/bin/env python3
"""Check and apply the pinned Sunshine and libvirtualhid patches without resetting files."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, text=True)


def prepare(source, entries):
    """Preflight every patch before modifying either checkout."""
    plan = []
    for entry in entries:
        patch = ROOT / entry['file']
        if hashlib.sha256(patch.read_bytes()).hexdigest() != entry['sha256']:
            raise RuntimeError(f'Patch checksum mismatch: {patch.name}')
        repo = source / entry['checkout']
        head = git(repo, 'rev-parse', 'HEAD')
        if head.returncode or head.stdout.strip() != entry['base_commit']:
            raise RuntimeError(f'{repo}: expected HEAD {entry["base_commit"]}; check checkout/submodules')
        reverse = git(repo, 'apply', '--reverse', '--check', str(patch))
        if reverse.returncode == 0:
            plan.append((repo, patch, 'already applied'))
            continue
        dirty = git(repo, 'status', '--porcelain', '--untracked-files=no', '--ignore-submodules=all')
        if dirty.returncode or dirty.stdout.strip():
            raise RuntimeError(f'{repo}: tracked files have changes; use a separate clean checkout')
        check = git(repo, 'apply', '--check', '--whitespace=error', str(patch))
        if check.returncode:
            raise RuntimeError(f'{patch.name}: {check.stderr.strip()}')
        plan.append((repo, patch, 'ready'))
    return plan


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sunshine', type=Path, help='Sunshine checkout at the documented commit')
    parser.add_argument('--check-only', action='store_true')
    args = parser.parse_args()
    manifest = json.loads((ROOT / 'patches/manifest.json').read_text())
    entries = [e for e in manifest['patches'] if e['use'] == 'runtime']
    plan = prepare(args.sunshine.resolve(), entries)
    for repo, patch, status in plan:
        if status == 'ready' and not args.check_only:
            result = git(repo, 'apply', '--whitespace=error', str(patch))
            if result.returncode:
                raise RuntimeError(result.stderr.strip())
            status = 'applied'
        print(f'{patch.name}: {status}')
    print('Check only; no files changed.' if args.check_only else 'Done. No build, installation or service restart performed.')


if __name__ == '__main__':
    try:
        main()
    except (RuntimeError, OSError, ValueError) as error:
        print(f'Error: {error}', file=sys.stderr)
        sys.exit(1)
