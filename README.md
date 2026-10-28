# JioSTB-reverse-engineer
Reverse engineering the Jio set-top box (JioSTB)

## Clean up the box with cleanyourtv

[cleanyourtv](https://github.com/Gathin23/cleanyourtv) debloats Android TV boxes over network ADB and
replaces the home screen. Stock Jio firmware usually hides ADB, so check the box before anything else.

| File | What it is |
|---|---|
| [docs/cleanyourtv.md](docs/cleanyourtv.md) | The steps: check for ADB, run cleanyourtv if it's there, and what works without it |
| [tools/adb-check.py](tools/adb-check.py) | Looks for ADB on the box from a computer on the same router. Read-only, standard-library Python |
| [PROMPT-jiostb.md](PROMPT-jiostb.md) | The JioSTB part to paste after cleanyourtv's prompt: what to keep, launcher limits, closing ADB |

```bash
python3 tools/adb-check.py 192.168.29.50   # the box's IP; --all checks every port
```

Run it on a computer at home, not in a cloud session: the box is only reachable from your own network.
