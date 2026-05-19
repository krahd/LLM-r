from llmr.remote_script import RemoteScriptClient
from llmr.ableton_osc import AbletonAction
from llmr.schemas import ToolName


def test_build_payload():
    action = AbletonAction(tool=ToolName.set_tempo, address="/live/song/set/tempo",
                           args=[128.0], description="Set tempo")
    client = RemoteScriptClient(host="127.0.0.1", port=20000)
    payload = client.build_payload(action)
    assert '"address": "/live/song/set/tempo"' in payload
    assert '"args": [128.0]' in payload or '"args": [128]' in payload
    assert '"tool": "set_tempo"' in payload
