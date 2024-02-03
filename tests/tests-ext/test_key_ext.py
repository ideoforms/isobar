import isobar_ext as iso
import pytest

def test_key_nearest_note():
    scale = iso.Scale.major

    for scale in iso.Scale.all():
        key = iso.Key(tonic=0, scale=scale)

        # for t in range(128):
        for t in range(-200, 200):

            print('\n' + scale.name)
            key.tonic = t
            key = iso.Key(tonic=t, scale=scale)
            # x = key.nearest_note(60)
            # test_pattern_midi_nr = [x+key.tonic for x in key.scale.semitones]
            octave5_start = 5 * key.scale.octave_size
            test_pattern_midi_nr = [x + octave5_start + key.tonic for x in key.scale.semitones]
            # result_pattern = [key.nearest_note(x) for x in test_pattern_midi_nr]
            result_pattern = [key.nearest_note(x) for x in test_pattern_midi_nr]
            print(result_pattern)
            assert test_pattern_midi_nr == result_pattern, "Assert Scale Up"

            negative_test_pattern_midi_nr = [x + octave5_start + key.tonic for x in range(key.scale.octave_size)
                                             if x not in key.scale.semitones]
            # print(test_pattern_midi_nr,negative_test_pattern_midi_nr )
            negative_result_flags = [key.nearest_note(x) != x for x in negative_test_pattern_midi_nr]
            assert all(
                negative_result_flags), f"{[(key.nearest_note(x), x, key.nearest_note(x) != x) for x in negative_test_pattern_midi_nr]}"

            if hasattr(scale, 'semitones_down') and scale.semitones_down:
                print("semitones down")
                test_pattern_midi_nr = [x + key.tonic for x in key.scale.semitones_down]
                result_pattern = [key.nearest_note(x, scale_down=True) for x in test_pattern_midi_nr]
                print(result_pattern)
                assert test_pattern_midi_nr == result_pattern, "Assert Scale Down"

                negative_test_pattern_midi_nr = [x + octave5_start + key.tonic for x in range(key.scale.octave_size)
                                                 if x not in key.scale.semitones_down]
                # print(test_pattern_midi_nr,negative_test_pattern_midi_nr )
                negative_result_flags = [key.nearest_note(x, scale_down=True) != x for x in
                                         negative_test_pattern_midi_nr]
                assert all(
                    negative_result_flags), f"{[(key.nearest_note(x, scale_down=True), x, key.nearest_note(x, scale_down=True) != x) for x in negative_test_pattern_midi_nr]}"


def test_key_contains_ext():
    a = iso.Key("C", "major")
    assert 0 in a
    assert 1 not in a
    assert 2 in a
    assert 3 not in a
    assert 4 in a
    assert 12 in a
    assert 13 not in a
    assert -1 in a
    assert -2 not in a
    assert 240 in a
    assert 241 not in a
    assert -241 in a
    assert -242 not in a

    assert None in a

    scale = iso.Scale(semitones=[0, 1, 5], semitones_down=[0, 2, 4], name="test", octave_size=6)
    a = iso.Key("C", scale)

    assert 0 in a
    assert not(a.__contains__(semitone=1, scale_down=True))
    assert a.__contains__(semitone=1, scale_down=False)
    assert not(a.__contains__(semitone=7, scale_down=True))
    assert a.__contains__(semitone=7, scale_down=False)
    assert not(a.__contains__(semitone=-1, scale_down=True))
    assert a.__contains__(semitone=-1, scale_down=False)