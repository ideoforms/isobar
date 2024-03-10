import pytest
import isobar_ext as iso
import mido
import os

IN_CI_CD = "GITHUB_ACTION" in os.environ

@pytest.fixture()
def dummy_timeline():

    # def mid_meta_message(msg: mido.MetaMessage = None, *args, **kwargs):
    #     # return None
    #     track_idx = min(kwargs.pop('track_idx', 0), len(dummy_timeline.output_device.miditrack) - 1)
    #     if not msg:
    #         msg = mido.MetaMessage(*args, **kwargs)
    #     dummy_timeline.output_device.miditrack[track_idx].append(msg)
    #
    # def set_tempo(tempo):
    #     # dummy_timeline.set_tempo(int(tempo))
    #     # tempo = mido.tempo2bpm(msg.tempo)
    #     mid_meta_message(type='set_tempo', tempo=int(mido.tempo2bpm(tempo)), time=0)
    #
    # def track_name(name, track_idx=0):
    #     mid_meta_message(type='track_name', name=name, time=0, track_idx=track_idx)

    timeline = iso.Timeline(output_device=iso.io.DummyOutputDevice(), clock_source=iso.DummyClock())
    timeline.stop_when_done = True
    return timeline