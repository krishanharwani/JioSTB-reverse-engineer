#!/usr/bin/env python3
"""Look for network ADB on a Jio set-top box, from a computer on the same network as the box.

    adb-check.py <box ip> [--all]

Checks 5555 (network ADB) and the other ports ADB has been seen on (5556-5585, 5877); --all checks
every TCP port, which can take two minutes. Each open port gets one ADB hello (CNXN), and the answer
says whether adbd is behind it:
    AUTH  adbd asking for a key: the box shows "Allow USB debugging?" when tools/tv.py connects
    CNXN  adbd with no key check: anyone on the network gets a shell on that port
    STLS  adbd behind TLS (Wireless debugging): pair first with `adb pair`
Nothing else is sent to the box, and no key is offered, so this cannot change anything on it.

Exits 0 when adbd answered on some port, 1 when the box answered but no port runs adbd, 2 when
nothing answered (the box off or in standby, a wrong address, or a computer on another network).
Only private addresses are accepted: 192.168.x.x, 10.x.x.x, 172.16-31.x.x, and Tailscale's 100.x.
Python 3.8+, standard library only.
"""
import argparse
import concurrent.futures
import ipaddress
import socket
import struct
import sys

CNXN, AUTH, STLS = 0x4E584E43, 0x48545541, 0x534C5453
ADB_REPLIES = {
    CNXN: "adbd with NO key check: anyone on your network gets a shell on this port",
    AUTH: 'adbd, asks for a key: accept "Allow USB debugging?" on the TV when tools/tv.py connects',
    STLS: "adbd behind TLS (Wireless debugging): pair first, see cleanyourtv's docs/REMOTE.md",
}
LIKELY_PORTS = [5555] + list(range(5556, 5586)) + [5877]
TAILSCALE = ipaddress.ip_network("100.64.0.0/10")
CONNECT_TIMEOUT_S = 1.5
SCAN_TIMEOUT_S = 0.5
REPLY_TIMEOUT_S = 3.0


def box_address(host):
    """The box's address as a string, or an error message when it is not on a private network."""
    try:
        infos = socket.getaddrinfo(host, None, type=socket.SOCK_STREAM)
    except (socket.gaierror, UnicodeError):
        return None, f"{host} does not resolve: give the box's IP address, e.g. 192.168.29.50"
    address = ipaddress.ip_address(infos[0][4][0].split("%", 1)[0])
    if address.is_loopback or address.is_unspecified:
        return None, f"{address} is this computer, not the box: give the box's own IP address"
    if address.is_private or address in TAILSCALE:
        return str(address), None
    return None, f"{address} is not a private address: run this from your home network, never against the internet"


def knock(host, port, timeout):
    """'open', 'refused' (the box said no) or 'silent' (no answer in time)."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return "open"
    except ConnectionRefusedError:
        return "refused"
    except OSError:
        return "silent"


def adb_hello():
    payload = b"host::\x00"
    header = struct.pack("<6I", CNXN, 0x01000001, 256 * 1024, len(payload), sum(payload), CNXN ^ 0xFFFFFFFF)
    return header + payload


def adb_reply(host, port):
    """The command adbd answers our hello with (CNXN, AUTH or STLS), or None when it is not adbd."""
    reply = b""
    try:
        with socket.create_connection((host, port), timeout=CONNECT_TIMEOUT_S) as sock:
            sock.settimeout(REPLY_TIMEOUT_S)
            sock.sendall(adb_hello())
            while len(reply) < 24:
                chunk = sock.recv(24 - len(reply))
                if not chunk:
                    break
                reply += chunk
    except OSError:
        pass
    if len(reply) < 24:
        return None
    command, _arg0, _arg1, _length, _check, magic = struct.unpack("<6I", reply)
    if command in ADB_REPLIES and magic == command ^ 0xFFFFFFFF:
        return command
    return None


def main():
    parser = argparse.ArgumentParser(description="Look for network ADB on a Jio set-top box.")
    parser.add_argument("host", help="the box's IP address on your network")
    parser.add_argument("--all", action="store_true", help="check every TCP port, not only the usual ADB ones")
    args = parser.parse_args()

    host, error = box_address(args.host)
    if error:
        print(error, file=sys.stderr)
        return 2

    ports = list(range(1, 65536)) if args.all else LIKELY_PORTS
    timeout = SCAN_TIMEOUT_S if args.all else CONNECT_TIMEOUT_S
    if args.all:
        print(f"Checking all 65535 TCP ports on {host}; this can take two minutes...")
    with concurrent.futures.ThreadPoolExecutor(max_workers=256) as pool:
        states = dict(zip(ports, pool.map(lambda port: knock(host, port, timeout), ports)))

    open_ports = sorted(port for port, state in states.items() if state == "open")
    if not open_ports and "refused" not in states.values():
        print(f"{host} did not answer on any port checked. The box is off or in standby, the address is "
              "wrong, or this computer is not on the box's network (a cloud session never is).")
        return 2

    if states[5555] == "refused":
        print(f"{host}:5555 refused (network ADB is off)")
    elif states[5555] == "silent":
        print(f"{host}:5555 no answer")
    adb_ports = []
    for port in open_ports:
        command = adb_reply(host, port)
        if command is None:
            print(f"{host}:{port} open, not ADB")
        else:
            print(f"{host}:{port} open, {ADB_REPLIES[command]}")
            adb_ports.append(port)

    if adb_ports:
        print(f"\nADB answers. Next: docs/cleanyourtv.md, step 2, with TV_HOST={host} TV_PORT={adb_ports[0]}")
        return 0
    print("\nNo ADB on this box" + ("" if args.all else " on the usual ports; --all checks every port") + ". "
          "Stock Jio firmware hides the debugging toggles, and cleanyourtv cannot run without ADB. "
          "What still works with the remote: docs/cleanyourtv.md, 'Without ADB'.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
