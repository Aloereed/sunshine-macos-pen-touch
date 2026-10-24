"""Exercise refusal and idempotency using disposable real Git repositories."""
import hashlib
import importlib.util
from pathlib import Path
import subprocess
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('apply_patches', Path(__file__).resolve().parents[1] / 'scripts/apply-patches.py')
apply_patches = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apply_patches)


class PatchPreparationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.oldroot = apply_patches.ROOT
        apply_patches.ROOT = self.root
        self.entries = []
        for name in ['host', 'library']:
            repo = self.root / name
            repo.mkdir()
            self.command(repo, 'init', '-q')
            self.command(repo, 'config', 'user.name', 'Patch test')
            self.command(repo, 'config', 'user.email', 'patch-test@example.invalid')
            (repo / 'input.txt').write_text('before\n')
            self.command(repo, 'add', 'input.txt')
            self.command(repo, 'commit', '-qm', 'Fixture base')
            base = self.command(repo, 'rev-parse', 'HEAD').strip()
            (repo / 'input.txt').write_text('after\n')
            data = self.command(repo, 'diff', '--binary').encode()
            (self.root / (name + '.patch')).write_bytes(data)
            (repo / 'input.txt').write_text('before\n')
            self.entries.append({'file': name + '.patch', 'checkout': name,
                                 'base_commit': base, 'sha256': hashlib.sha256(data).hexdigest()})

    def tearDown(self):
        apply_patches.ROOT = self.oldroot
        self.tmp.cleanup()

    @staticmethod
    def command(repo, *args):
        return subprocess.check_output(['git', '-C', str(repo), *args], text=True, stderr=subprocess.PIPE)

    def test_check_only_preserves_both_checkouts(self):
        self.assertEqual([p[2] for p in apply_patches.prepare(self.root, self.entries)], ['ready', 'ready'])
        for entry in self.entries:
            self.assertEqual((self.root / entry['checkout'] / 'input.txt').read_text(), 'before\n')

    def test_applied_patches_are_recognized(self):
        for repo, patch, _ in apply_patches.prepare(self.root, self.entries):
            self.command(repo, 'apply', str(patch))
        self.assertEqual([p[2] for p in apply_patches.prepare(self.root, self.entries)],
                         ['already applied', 'already applied'])

    def test_wrong_dependency_base_does_not_modify_host(self):
        self.entries[1]['base_commit'] = '0' * 40
        with self.assertRaisesRegex(RuntimeError, 'expected HEAD'):
            apply_patches.prepare(self.root, self.entries)
        self.assertEqual((self.root / 'host/input.txt').read_text(), 'before\n')

    def test_checksum_failure_does_not_modify_host(self):
        (self.root / 'library.patch').write_text('tampered\n')
        with self.assertRaisesRegex(RuntimeError, 'checksum mismatch'):
            apply_patches.prepare(self.root, self.entries)
        self.assertEqual((self.root / 'host/input.txt').read_text(), 'before\n')

    def test_uncommitted_source_is_preserved(self):
        (self.root / 'host/input.txt').write_text('user change\n')
        with self.assertRaisesRegex(RuntimeError, 'tracked files have changes'):
            apply_patches.prepare(self.root, self.entries)
        self.assertEqual((self.root / 'host/input.txt').read_text(), 'user change\n')


if __name__ == '__main__':
    unittest.main()
