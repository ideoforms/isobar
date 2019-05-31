""" Unit tests for isobar """

import pytest
import isobar
import time
import os

def test_pattern():
    p = isobar.PSeq([ 1, 2, 3, 4 ], 1)
    assert next(p) == 1
    assert next(p) == 2
    assert next(p) == 3
    assert next(p) == 4
    with pytest.raises(StopIteration) as excinfo:
        next(p)
