# About this fork

This is [BeamNG.Earth](https://github.com/TecnaGamer/BeamNG.Earth) with one addition: **BeamMP join fixes**, until BeamMP ships them itself.

When BeamNG.Earth starts BeamMP's official launcher, the launcher installs the official BeamMP mod. Right after that, before the game starts, this fork replaces six files in that mod with fixed ones (`bmppatch.py`, files in `beammp_patch/files`):

- The BeamMP menu no longer bounces back to the main menu or loses its styling when a server's mod reloads the UI.
- Local mods the server doesn't use are switched off in one batch. This fixes the crash at map load with hundreds of mods.
- A session's mods are cleaned up in one batch when leaving: no freeze or crash, and rejoining works.
- Server mods are not loaded a second time.
- The mod manager's `db.json` and UI updates are held while joining. A 400-mod server: about 11 min → about 1 min.
- The launcher's loading status is polled every frame while syncing.

**Applied only to the version it was made for.** The patch is applied only to the exact official BeamMP mod it was made for (4.23.1, checked by its SHA-256). Any other version, such as a newer BeamMP, is left as it is.

**Source.** The fixed files come from [Aaexy/BeamMP, branch `all-fixes`](https://github.com/Aaexy/BeamMP/tree/all-fixes) (AGPL-3.0, like BeamMP). Each fix is on its own branch there and is offered to BeamMP.

## A faster launcher too (since 1.8.2-beta.2, Windows)

The BeamMP launcher used is the one from [Aaexy/BeamMP-Launcher](https://github.com/Aaexy/BeamMP-Launcher). It is BeamMP's launcher plus the faster sync of cached mods proposed in [BeamMP/BeamMP-Launcher#279](https://github.com/BeamMP/BeamMP-Launcher/issues/279): cached mods are hardlinked into the game instead of copied on every join, and their checksums are remembered.

- **Where it goes.** It's put in place of the player's launcher, in the same folder (usually `%APPDATA%\BeamMP-Launcher`). That keeps its cache of the servers' mods and its settings. The launcher it replaces is kept once beside it, as `BeamMP-Launcher.exe.before-fork`. A player with no launcher gets it the usual way (BeamNG.Earth asks first).
- **Checksum.** It's downloaded from the fork's releases and checked against its published SHA-256 (`bmplaunch.py`).
- **BeamMP updates.** When BeamMP publishes a newer launcher, this one updates itself to the official one, and the fork leaves that in place.
- **Opting out.** Not done when a launcher is named with `--beammp-launcher` or `BEAMMP_LAUNCHER`.

**Updates.** This fork's app updates from this fork's releases (`server/updates.py`), so it keeps the fixes.

Everything else is BeamNG.Earth as published by TecnaGamer.
