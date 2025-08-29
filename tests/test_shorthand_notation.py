from isobar.pattern import PSequence
from isobar.notation import parse_notation

def test_shorthand_notation_parser():
    seq = parse_notation('1 -2 [10 11] [c#4 [30.1 -30.2 30.3]]')
    expected = [1, -2, 10, 'c#4', 1, -2, 11, 30.1, 1, -2, 10, 'c#4', 1, -2, 11, -30.2]
    assert seq == expected

    seq = PSequence('1 -2 [10 11] [c#4 [30.1 -30.2 30.3]]')
    expected = [1, -2, 10, 'c#4', 1, -2, 11, 30.1, 1, -2, 10, 'c#4', 1, -2, 11, -30.2]
    output = seq.nextn(16)
    assert output == expected