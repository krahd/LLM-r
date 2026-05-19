#!/usr/bin/env python3
"""Diagnostic: send test OSC messages to AbletonOSC and check for responses."""

import socket
import struct
import time

HOST = "127.0.0.1"
PORT = 11000
LISTEN_PORT = 11001


def pad4(n):
    return ((n + 3) // 4) * 4


def pack_string(s: str) -> bytes:
    encoded = s.encode() + b"\x00"
    return encoded.ljust(pad4(len(encoded)), b"\x00")


def pack_int32(v: int) -> bytes:
    return struct.pack(">i", v)


def pack_float32(v: float) -> bytes:
    return struct.pack(">f", v)


def build_message(address: str, type_tags: str, *args) -> bytes:
    data = pack_string(address)
    data += pack_string("," + type_tags)
    for tag, val in zip(type_tags, args):
        if tag == "i":
            data += pack_int32(int(val))
        elif tag == "f":
            data += pack_float32(float(val))
        elif tag == "s":
            data += pack_string(str(val))
    return data


def send_and_print(sock, label: str, address: str, type_tags: str, *args):
    msg = build_message(address, type_tags, *args)
    print(f"  Sending {label}: {address} {list(args)}")
    sock.sendto(msg, (HOST, PORT))
    time.sleep(0.05)


def try_receive(recv_sock, timeout=0.5) -> bytes | None:
    recv_sock.settimeout(timeout)
    try:
        data, _ = recv_sock.recvfrom(4096)
        return data
    except socket.timeout:
        return None


def main():
    print(f"Testing AbletonOSC at {HOST}:{PORT}")
    print()

    # Bind receive socket
    recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        recv_sock.bind(("0.0.0.0", LISTEN_PORT))
    except OSError as e:
        print(f"Warning: cannot bind receive port {LISTEN_PORT}: {e}")
        recv_sock = None

    send_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    # 1. Test if AbletonOSC responds at all
    print("Step 1: Connectivity test (get current tempo)")
    msg = build_message("/live/song/get/tempo", "")
    send_sock.sendto(msg, (HOST, PORT))
    if recv_sock:
        resp = try_receive(recv_sock, timeout=1.0)
        if resp:
            print(f"  ✓ AbletonOSC responded! ({len(resp)} bytes)")
            try:
                tempo_bytes = resp[8:12]
                tempo = struct.unpack(">f", tempo_bytes)[0]
                print(f"    Current tempo: {tempo:.1f} BPM")
            except Exception:
                print(f"    Raw response: {resp.hex()}")
        else:
            print("  ✗ No response - AbletonOSC may not be running or not configured")
            print()
            print("  To fix: in Ableton Live > Preferences > Link/Tempo/MIDI > MIDI,")
            print("  set one of the Control Surface slots to 'AbletonOSC'.")
            print("  AbletonOSC must be installed in your MIDI Remote Scripts folder.")
            print()
            print("  Continuing to send test notes anyway...")
    else:
        print("  (Cannot check response - no receive socket)")

    print()

    # 2. Set tempo
    print("Step 2: Set tempo to 120 BPM")
    send_and_print(send_sock, "set_tempo", "/live/song/set/tempo", "f", 120.0)

    # 3. Create MIDI track at position 0
    print("Step 3: Create MIDI track")
    send_and_print(send_sock, "create_midi_track", "/live/song/create_midi_track", "i", -1)
    time.sleep(0.2)

    # 4. Create clip (4 beats)
    print("Step 4: Create clip (track=0, slot=0, length=4 beats)")
    send_and_print(send_sock, "create_clip", "/live/clip_slot/create_clip", "iff", 0, 0, 4.0)
    time.sleep(0.2)

    # 5. Add a single simple note (middle C, beat 0, 1 beat long)
    print("Step 5: Add one note (pitch=60, start=0.0, dur=0.5, vel=100, mute=0)")
    note_args = [0, 0, 60, 0.0, 0.5, 100.0, 0]
    note_types = "iiifffi"
    send_and_print(send_sock, "add/notes", "/live/clip/add/notes", note_types, *note_args)
    time.sleep(0.2)

    print()
    print("Done. Check Ableton Live:")
    print("  - Did the tempo change to 120 BPM?")
    print("  - Did a new MIDI track appear?")
    print("  - Does the clip have a note in it?")
    print()
    print("If tempo changed but notes didn't appear, it's an OSC encoding issue.")
    print("If nothing changed at all, AbletonOSC is not running.")

    send_sock.close()
    if recv_sock:
        recv_sock.close()


if __name__ == "__main__":
    main()
