"""bmppatch (this fork): BeamMP's join fixes put into the official BeamMP mod, only the version they were made for."""
import hashlib
import os
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import bmppatch  # noqa: E402


def make_zip(path, files):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in files.items():
            z.writestr(name, data)
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


class BmpPatchTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.user = os.path.join(self.tmp.name, "current")
        self.zip = os.path.join(self.user, "mods", "multiplayer", "BeamMP.zip")
        self.patch = os.path.join(self.tmp.name, "patch")
        os.makedirs(os.path.join(self.patch, "lua"))
        with open(os.path.join(self.patch, "lua", "a.lua"), "wb") as f:
            f.write(b"fixed")

    def tearDown(self):
        self.tmp.cleanup()

    def test_patches_the_version_it_was_made_for_once(self):
        base = make_zip(self.zip, {"lua/a.lua": b"official", "lua/b.lua": b"untouched"})
        ok, msg = bmppatch.apply(self.user, patch_dir=self.patch, base_sha256=base)
        self.assertTrue(ok, msg)
        with zipfile.ZipFile(self.zip) as z:
            self.assertEqual(z.read("lua/a.lua"), b"fixed")
            self.assertEqual(z.read("lua/b.lua"), b"untouched")
        ok, msg = bmppatch.apply(self.user, patch_dir=self.patch, base_sha256=base)
        self.assertTrue(ok)
        self.assertIn("already", msg)
        self.assertFalse(os.path.exists(self.zip + ".patching"))

    def test_leaves_another_version_alone(self):
        make_zip(self.zip, {"lua/a.lua": b"newer beammp"})
        before = Path(self.zip).read_bytes()
        ok, msg = bmppatch.apply(self.user, patch_dir=self.patch, base_sha256="0" * 64)
        self.assertFalse(ok)
        self.assertIn("left as it is", msg)
        self.assertEqual(Path(self.zip).read_bytes(), before)

    def test_a_file_missing_from_the_mod_leaves_it_alone(self):
        base = make_zip(self.zip, {"lua/other.lua": b"x"})
        before = Path(self.zip).read_bytes()
        ok, _ = bmppatch.apply(self.user, patch_dir=self.patch, base_sha256=base)
        self.assertFalse(ok)
        self.assertEqual(Path(self.zip).read_bytes(), before)
        self.assertFalse(os.path.exists(self.zip + ".patching"))

    def test_no_mod_installed(self):
        ok, msg = bmppatch.apply(self.user, patch_dir=self.patch)
        self.assertFalse(ok)
        self.assertIn("not found", msg)

    def test_the_bundled_fixes_fit_beammp_4_23_1(self):
        files = bmppatch.patch_files()
        self.assertEqual(len(files), 6)
        self.assertIn("lua/ge/extensions/MPModManager.lua", files)
        for name, data in files.items():
            self.assertNotIn(b"\r\n", data, name)
            self.assertNotIn(b"profProbe", data, name)     # (the test-only timing probe never ships)


if __name__ == "__main__":
    unittest.main()
