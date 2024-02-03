import isobar_ext as iso


def test_scale_get():
    scale = iso.Scale(semitones=[0, 2, 4, 6, 8, 10], name="test_scale", octave_size=12,
                      semitones_down=[0, 1, 3, 5, 7, 9, 11])
    assert [scale.get(x, scale_down=False) for x in range(7)] == [0, 2, 4, 6, 8, 10, 12]
    assert [scale.get(x, scale_down=True) for x in range(8)] == [0, 1, 3, 5, 7, 9, 11, 12]

def test_single_key_index_of():
    scalex = iso.Scale.major
    scale = iso.Scale(semitones=[0, 2, 4, 6, 8, 10], name="test_scale", octave_size=12,
                      semitones_down=[0, 1, 3, 5, 7, 9, 11])
    # for scale in iso.Scale.all():
    for scale in [iso.Scale.chromatic]:
        key = iso.Key(tonic=0, scale=scale)
        print('\n' + scale.name)

        x = key.scale.indexOf(202)
        x = key.scale.indexOf(-202)


        # for t in range(-200, 200):
        for t in [-200, 200]:
            key.tonic = t % key.scale.octave_size
            test_pattern_midi_nr = [x + t for x in key.scale.semitones]
            result_pattern = [key.nearest_note(x) for x in test_pattern_midi_nr]
            index_pattern = [key.scale.indexOf(x - key.tonic) for x in result_pattern]

            rng_start = t // key.scale.octave_size * len(key.scale.semitones)
            pdegree_pattern = list(iso.PDegree(iso.PSequence(index_pattern, repeats=1), key))
            print(result_pattern, index_pattern, pdegree_pattern)
            assert index_pattern == list(range(rng_start, rng_start + len(
                key.scale.semitones))), f"Scale Up IndexOf error {(t,key.tonic, scale.name)=}"
            assert result_pattern == pdegree_pattern, f"Scale Up PDegree error {(t, key.tonic,key.scale.name)=}"


def test_key_index_of():
    scalex = iso.Scale.major
    scale = iso.Scale(semitones=[0, 2, 4, 6, 8, 10], name="test_scale", octave_size=12,
                      semitones_down=[0, 1, 3, 5, 7, 9, 11])
    for scale in iso.Scale.all():
        key = iso.Key(tonic=0, scale=scale)
        print('\n' + scale.name)

        for t in range(-200, 200):
            key.tonic = t % key.scale.octave_size
            test_pattern_midi_nr = [x + t for x in key.scale.semitones]
            result_pattern = [key.nearest_note(x) for x in test_pattern_midi_nr]
            index_pattern = [key.scale.indexOf(x - key.tonic) for x in result_pattern]

            rng_start = t // key.scale.octave_size * len(key.scale.semitones)
            pdegree_pattern = list(iso.PDegree(iso.PSequence(index_pattern, repeats=1), key))
            print(result_pattern, index_pattern, pdegree_pattern)
            assert index_pattern == list(range(rng_start, rng_start + len(
                key.scale.semitones))), f"Scale Up IndexOf error {(t,key.tonic, scale.name)=}"
            assert result_pattern == pdegree_pattern, f"Scale Up PDegree error {(t, key.tonic,key.scale.name)=}"
            if hasattr(scale, 'semitones_down') and scale.semitones_down:
                test_pattern_midi_nr = [x + t for x in key.scale.semitones_down]
                test_pattern_midi_nr.reverse()
                result_pattern = [key.nearest_note(x, scale_down=True) for x in test_pattern_midi_nr]
                index_pattern = [key.scale.indexOf(x - key.tonic, scale_down=True) for x in result_pattern]

                rng_start = t // key.scale.octave_size * len(key.scale.semitones_down)
                pdegree_pattern = list(iso.PDegree(iso.PSequence(index_pattern, repeats=1), key))
                print(t, result_pattern, index_pattern, pdegree_pattern)
                assert index_pattern == list(
                    range(rng_start + len(key.scale.semitones_down) - 1, rng_start - 1, -1)), "Scale Down IndexOf error"
                assert result_pattern == pdegree_pattern, f"Scale Down PDegree error {(key.tonic,key.scale.name)=}"

def test_generic_get_indexOf():
    scale = iso.Scale(semitones=[0, 2, 4, 6, 8, 10], name="test_scale", octave_size=12,
                      semitones_down=[0, 1, 3, 5, 7, 9, 11])

    # scale = iso.Scale.minor
    for scale in iso.Scale.all():
        print(scale.name)
        if hasattr(scale, "semitones_down") and scale.semitones_down:
            print("scale_down tested too")
        for t in range(-200, 200):
            key = iso.Key(tonic=t, scale=scale)
            exp_result = [s + key.tonic for s in scale.semitones]
            assert [key.get(x) for x in range(len(scale.semitones))] == exp_result, "IndexOf UP1"
            assert [scale.indexOf(x - key.tonic) for x in exp_result] == list(
                range(len(scale.semitones))), "IndexOf UP2"

            if hasattr(scale, "semitones_down") and scale.semitones_down:
                exp_result = [s + key.tonic for s in scale.semitones_down]

                assert [key.get(x, scale_down=True) for x in
                        range(len(scale.semitones_down))] == exp_result, "IndexOf DOWN1"
                assert [scale.indexOf(x - key.tonic, scale_down=True) for x in exp_result] == list(
                    range(len(scale.semitones_down))), "IndexOf DOWN2"