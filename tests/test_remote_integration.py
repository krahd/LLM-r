import json
import socket
import threading
import time

from llmr.ableton_osc import AbletonAction
from llmr.schemas import ToolName
from llmr.remote_script import RemoteScriptClient


def _udp_server_collect(host, port, out_list, stop_event):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((host, port))
    sock.settimeout(0.5)
    try:
        while not stop_event.is_set():
            try:
                data, addr = sock.recvfrom(65536)
                out_list.append(data.decode("utf-8"))
            except socket.timeout:
                continue
    finally:
        sock.close()


def test_remote_client_sends_and_udp_server_receives():
    host = "127.0.0.1"
    port = 21000
    received = []
    stop_event = threading.Event()
    srv = threading.Thread(target=_udp_server_collect, args=(host, port, received, stop_event), daemon=True)
    srv.start()

    client = RemoteScriptClient(host=host, port=port)
    action = AbletonAction(tool=ToolName.set_tempo, address="/live/song/set/tempo", args=[123.0], description="Set tempo")
    client.send(action)

    # wait for server to receive
    timeout = time.time() + 2.0
    while time.time() < timeout and len(received) == 0:
        time.sleep(0.05)

    stop_event.set()
    srv.join(timeout=1.0)

    assert len(received) >= 1, f"No UDP messages received on {host}:{port}"
    payload = json.loads(received[0])
    assert payload.get("address") == "/live/song/set/tempo"
    assert payload.get("args") == [123.0] or payload.get("args") == [123]
