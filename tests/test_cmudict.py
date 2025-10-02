# SPDX-FileCopyrightText: 2017 Keith Ito <keeeto@gmail.com>
# SPDX-FileContributor: Enno Hermann
#
# SPDX-License-Identifier: MIT

"""CMUDict tests.

Source: https://github.com/keithito/tacotron"""

import pytest

from ko_speech_tools.g2p.cmudict import CMUDict


@pytest.fixture
def cmudict():
    return CMUDict()


@pytest.mark.parametrize(
    ("word", "expected"),
    [
        ("ADVERSITY", ["AE0 D V ER1 S IH0 T IY2", "AH0 D V ER1 S IH0 T IY0"]),
        ("BarberShop", ["B AA1 R B ER0 SH AA2 P"]),
        ("You'll", ["Y UW1 L"]),
        ("'tis", ["T IH1 Z"]),
    ],
)
def test_cmudict(cmudict, word, expected):
    assert cmudict[word] == expected


def test_cmudict_error(cmudict):
    assert "" not in cmudict
