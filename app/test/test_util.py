import util as u
import pytest


@pytest.mark.parametrize(
    'vs, n, expected',
    [
        ([], 1, []),
        ([1], 1, [[1]]),
        ([1], 2, [[1]]),
        ([1, 2], 1, [[1], [2]]),
        ([1, 2, 3], 2, [[1, 2], [3]]),
    ]
)
def test_chunked(vs: list[int], n: int, expected: list[list[int]]):
    actual = list(u.chunked(vs, n))
    assert actual == expected
    