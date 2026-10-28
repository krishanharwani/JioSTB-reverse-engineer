# JioSTB addendum to cleanyourtv's prompt

Paste this right after cleanyourtv's [PROMPT.md](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md)
prompt, in a Claude Code session that runs on a computer on the same Jio router as the box (see
[docs/cleanyourtv.md](docs/cleanyourtv.md)). Fill in the three blanks first. If `tools/adb-check.py`
found no ADB, don't use it: nothing in cleanyourtv applies.

---

My device is a Jio set-top box (model on its label: <e.g. JHSD200>), connected to the Jio router by
<Ethernet / Wi-Fi>. ADB answered at <box ip>:<port>, according to `tools/adb-check.py` from
krishanharwani/JioSTB-reverse-engineer. It's an operator box, not a retail Android TV, so on top of
the steps above:

Connect
- Use `TV_HOST=<box ip> TV_PORT=<port>`, and don't scan my network.
- If adb-check reported "NO key check" (the box answered CNXN), tell me first. Then we do the whole job
  in one sitting and close the port at the end.

Back up first
- Do everything PROMPT.md asks. Also save `pm list packages -f -i` (each package's installer) and
  `dumpsys package` for every Jio package (`com.jio.*`, and anything else whose installer or path
  points to Jio) into `backup/`.

Debloat
- Jio's own packages run the box: the Jio home screen, JioTV+ live channels (they arrive over the
  router), Jio Store (the only app store here), the remote and voice search, the Jio login and device
  management, and the firmware updater. Treat every Jio package as one to keep until `dumpsys package`
  shows what it does. Ask me before disabling any of them, one per batch, with a screenshot and a
  check that Live TV still plays after each.
- Never disable the Live TV / JioTV+ app or the services it uses, Jio Store, the update service, Jio
  login or device management, remote and Bluetooth pairing, or the on-screen keyboard. If the box
  loses its channels, its login or the remote after a batch, re-enable that batch right away with
  `tools/restore.sh`.
- Jio's ad-push app: one owner reported that disabling it didn't stop the ads in JioTV+. Ask me
  before trying it.
- After the reboot, compare `pm list packages -d` with what you disabled. Jio can re-enable packages
  at boot or with a pushed update. Note which ones come back instead of disabling them again.
- Private DNS needs Android 9 or newer (`ro.build.version.sdk` 28+). Some Jio boxes run Android 7.
  Tell me that AdGuard DNS stopped Zee5 live channels for one owner.

Launcher
- Check the SDK against the launcher's `minSdk` 26 first. On Android 7 (SDK 24 or 25), do the debloat
  half only.
- Check that the box takes a sideloaded APK at all. Jio removed the package installer from some boxes
  in an update. If installs fail, or a package that claims HOME is refused, do the debloat half only
  and keep the Jio home screen.
- If the launcher installs, still keep the Jio home screen enabled, as PROMPT.md says for CVTE boards.
  Set the new launcher with `cmd package set-home-activity`, reboot once, and confirm that Home, Live
  TV and ADB all come back before anything else. Then ask me to press the remote's Jio, TV and app
  buttons, and remap the ones that do nothing.

Finish
- Close ADB as PROMPT.md describes, and check with `tools/adb-closed.py <box ip> <port>`.
- If Developer options had no toggle for the debugging that was on, tell me before you close it from
  the shell (`settings put global adb_enabled 0`). With no toggle on the box, there would be no way
  back in later to run `tools/restore.sh`. Let me decide, and give me the restore script either way.
