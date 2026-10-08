import pytest
import isobar as iso

@pytest.fixture()
def dummy_timeline():
    timeline = iso.Timeline(output_device=iso.io.DummyOutputDevice(),
                            clock_source=iso.DummyClock())
    timeline.stop_when_done = True

    # Simulate a timeline that is already running
    # This is necessary for tests that assume the timeline is already running,
    # e.g. recording notes into a track.
    timeline.is_running = True

    return timeline