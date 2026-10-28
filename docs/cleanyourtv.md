# cleanyourtv on a JioSTB

[cleanyourtv](https://github.com/Gathin23/cleanyourtv) debloats Android TV sets over network ADB and can
replace the home screen with a clean launcher. This page is how to try it on a Jio set-top box (JioFiber
or AirFiber) plugged into the Jio router.

## It may not work: check first

cleanyourtv needs network ADB on the box, and stock Jio firmware usually doesn't have it. Owners report
that Developer options unlock (press Build 7 times), but the USB debugging and Network debugging
toggles aren't there, and port 5555 refuses connections. Some boxes also lost their package installer
in a firmware update:

- [India Broadband Forum, 2020](https://broadband.forum/threads/can-adb-work-on-jio-setup-box-nougat.198808/):
  Developer options open, no USB debugging toggle, ADB over Wi-Fi refused.
- [jellyfin-androidtv#3570](https://github.com/jellyfin/jellyfin-androidtv/issues/3570): "no adb
  access to side-load any app"; the package manager gone after an update.
- [OnlyTech, 2025](https://onlytech.com/threads/access-hidden-options-and-settings-in-jiofiber-and-airfiber-set-top-box-adguard-dns-stb-hotspot.55857/page-2):
  Developer options open on JioFiber boxes only, not AirFiber, and still no ADB option.

So step 1 is a two-minute check, and its answer decides the rest. If the box has no ADB, cleanyourtv's
own rule is to stop there.

**Out of scope:** the ways people force ADB onto these boxes, like flashing a ported Android TV image
with the Amlogic USB tool or factory-mode tricks. Forum users report dead boxes, and you can lose
JioTV+. cleanyourtv never roots or flashes anything, and neither does this repo.

## Step 1: find the box and check for ADB

You need a computer on the same network as the box, meaning on the same Jio router, over cable or
Wi-Fi. A cloud session (Claude Code on the web) can't do this step, because it runs outside your home.

1. **On the box:** Settings → About (on some firmware, Device Preferences → About). Press OK on
   **Build** 7 times, go back, and open **Developer options**. Turn on **USB debugging** and
   **Network debugging** (or ADB debugging) if either one is listed. Note which ones you see.
2. **Find the box's IP address:** Settings → Network on the box shows it. Or open the router's page,
   which lists connected devices: on JioFiber that's usually `http://192.168.29.1`, and otherwise
   it's the Gateway address in the box's network settings.
3. **On the computer** (Python 3.8 or newer):

   ```bash
   git clone https://github.com/krishanharwani/JioSTB-reverse-engineer
   cd JioSTB-reverse-engineer
   python3 tools/adb-check.py 192.168.29.50          # the box's IP
   python3 tools/adb-check.py 192.168.29.50 --all    # if nothing turned up: every port, up to two minutes
   ```

   The check sends one ADB hello to each open port and offers no key, so it changes nothing on the box.

| Exit | It says | Next |
|---|---|---|
| 0 | `ADB answers` on some port | [Step 2](#step-2-adb-answers-run-cleanyourtv) |
| 1 | `No ADB on this box` (after `--all`) | [Without ADB](#without-adb-what-still-works) |
| 2 | `did not answer` | The box is asleep or off, the IP is wrong, or the computer is on another network. Wake the box and check the IP. |

## Step 2: ADB answers, run cleanyourtv

Do this on the same computer, in a Claude Code session that runs there: the terminal `claude`, or
the Claude desktop app. A cloud session can't reach the box.

```bash
git clone https://github.com/Gathin23/cleanyourtv
cd cleanyourtv
python3 -m venv tools/venv
tools/venv/bin/pip install -r tools/requirements.txt
TV_HOST=192.168.29.50 TV_PORT=5555 tools/venv/bin/python -I tools/tv.py --probe   # IP and port from step 1
```

When "Allow USB debugging?" appears on the TV, accept it. `--probe` prints the model and Android
version. Then start `claude` in that `cleanyourtv` folder and paste two things: cleanyourtv's
[PROMPT.md](https://github.com/Gathin23/cleanyourtv/blob/main/PROMPT.md) (the part between the
`---` lines), then this repo's [PROMPT-jiostb.md](../PROMPT-jiostb.md) with its blanks filled in.
The second part tells the agent what's different on an operator box: what to keep, where the launcher
stops, and how to close ADB again.

**If step 1 said "NO key check"** (the box answered `CNXN`), anyone on your network can get a shell on
that port right now. Do the whole session in one sitting, then close it as the prompt describes.

## Without ADB: what still works

Nothing gets disabled or replaced, but these work with just the remote:

- **Ad-blocking DNS on the box.** Settings → Network → your connection → IP settings → **Static**.
  Keep the box's current IP address, set the gateway to the router's address and the prefix length to
  24, then DNS 1 `94.140.14.14` and DNS 2 `94.140.15.15`
  ([AdGuard DNS](https://adguard-dns.io/en/public-dns.html)). So nothing else takes that IP, reserve it
  for the box in the router's DHCP settings. To undo, set IP settings back to **DHCP**.
  - What people reported in the [OnlyTech thread](https://onlytech.com/threads/access-hidden-options-and-settings-in-jiofiber-and-airfiber-set-top-box-adguard-dns-stb-hotspot.55857/):
    fewer in-app ads, but Zee5 live channels stopped for one user. On one AirFiber box, a static
    IP over Ethernet lost the connection.
  - It doesn't block YouTube ads, and it doesn't touch the Jio home screen or its apps.
- **DNS blocking for the whole network.** If you run Pi-hole or AdGuard Home, or your router lets you
  set the DNS it hands out, that covers the box and every other device, with the same caveats.
- **The box's own settings.** Turn off any usage-and-diagnostics or ad-personalisation toggle the
  firmware shows.

## Afterwards

- Close network ADB and check that it's closed. cleanyourtv's prompt walks through this, ending with
  `tools/adb-closed.py <box ip>`.
- Don't commit backups, screenshots or `tv.py --probe` output to a public repo. They carry the box's
  serial number, IP address and account details. The `.gitignore` here keeps `backup/`, `shots/` and
  `work/` out.
