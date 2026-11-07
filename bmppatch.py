"""BeamMP join fixes, applied to the official BeamMP mod (this fork only, until BeamMP ships them).

The official BeamMP launcher installs BeamMP's mod (mods/multiplayer/BeamMP.zip) every time it starts. Once it is
ready, and before the game starts, apply() replaces six files in that zip with the fixed ones in beammp_patch/files:

- the BeamMP menu no longer bounces to the main menu or loses its styling when a server's mod reloads the UI;
- local mods the server doesn't use are switched off in one batch (no crash at map load with hundreds of mods);
- a session's mods are cleaned up in one batch when leaving (no freeze or crash, rejoining works);
- server mods already loaded while syncing are not loaded a second time;
- the mod manager's db.json and UI updates are held while joining (a 400-mod join: ~11 min -> ~1 min);
- the launcher's loading status is polled every frame while syncing.

Source of those files (AGPL-3.0, like BeamMP): https://github.com/Aaexy/BeamMP/tree/all-fixes, branch "all-fixes"
(each fix on its own branch, offered to BeamMP). The patch is applied only to the exact BeamMP version it was made
for (BASE_SHA256); any other version, e.g. a newer BeamMP, is left as it is.
"""
import hashlib
import os
import sys
import zipfile

BASE_VERSION = "4.23.1"
# sha256 of BeamMP's official mod 4.23.1 (BeamMP.zip as its launcher installs it)
BASE_SHA256 = "5a9692a89a4e65a27af67cc8aae9872c51af8a878d9e6f99036b9be783b1ddc8"
SOURCE = "https://github.com/Aaexy/BeamMP/tree/all-fixes"
ROOT = getattr(sys, "_MEIPASS", None) or os.path.dirname(os.path.abspath(__file__))
PATCH_DIR = os.path.join(ROOT, "beammp_patch", "files")


def mod_zip(user_dir):
    """BeamMP's mod in the game's user folder (the launcher names it beammp.zip on Linux), or None."""
    for name in ("BeamMP.zip", "beammp.zip"):
        p = os.path.join(user_dir, "mods", "multiplayer", name)
        if os.path.isfile(p):
            return p
    return None


def patch_files(patch_dir=PATCH_DIR):
    """{path in the zip: content} of the fixed files."""
    out = {}
    for d, _, names in os.walk(patch_dir):
        for n in names:
            p = os.path.join(d, n)
            with open(p, "rb") as f:
                out[os.path.relpath(p, patch_dir).replace(os.sep, "/")] = f.read()
    return out


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def is_patched(zip_path, files):
    try:
        with zipfile.ZipFile(zip_path) as z:
            names = set(z.namelist())
            return all(p in names and z.read(p) == data for p, data in files.items())
    except (OSError, zipfile.BadZipFile):
        return False


def apply(user_dir, patch_dir=PATCH_DIR, base_sha256=BASE_SHA256):
    """Put the fixed files into BeamMP's mod when it is exactly the version they were made for.
    Returns (applied, message): applied is True when the mod has the fixes now."""
    files = patch_files(patch_dir)
    if not files:
        return False, "BeamMP join fixes not bundled with this copy"
    zp = mod_zip(user_dir)
    if not zp:
        return False, "BeamMP join fixes not applied: BeamMP's mod not found in mods/multiplayer"
    if is_patched(zp, files):
        return True, f"BeamMP join fixes already applied ({SOURCE})"
    if _sha256(zp) != base_sha256:
        return False, (f"BeamMP join fixes not applied: the installed BeamMP is not the official {BASE_VERSION} "
                       "they were made for (BeamMP was updated?); it is left as it is")
    tmp = zp + ".patching"
    try:
        with zipfile.ZipFile(zp) as zin, zipfile.ZipFile(tmp, "w", zipfile.ZIP_DEFLATED) as zout:
            missing = [p for p in files if p not in set(zin.namelist())]
            if missing:
                raise ValueError("not in BeamMP's mod: " + ", ".join(missing))
            for info in zin.infolist():
                zout.writestr(info, files.get(info.filename, zin.read(info)))
        if not is_patched(tmp, files):
            raise ValueError("the patched mod did not read back")
        os.replace(tmp, zp)
    except (OSError, ValueError, zipfile.BadZipFile) as e:
        try:
            os.remove(tmp)
        except OSError:
            pass
        return False, f"BeamMP join fixes not applied ({e}); the official BeamMP is used"
    return True, f"BeamMP join fixes applied to BeamMP {BASE_VERSION} ({SOURCE})"


if __name__ == "__main__":      # (by hand: python bmppatch.py <the game's user folder, e.g. ...\BeamNG.drive\current>)
    print(apply(sys.argv[1]))
