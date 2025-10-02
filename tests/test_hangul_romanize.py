# SPDX-FileCopyrightText: 2015 Jeong YunWon <jeong+hangul-romanize@youknowone.org>
#
# SPDX-License-Identifier: BSD-2-Clause

"""Romanization tests.

Source:
https://github.com/youknowone/hangul-romanize"""

import pytest

from ko_speech_tools import hangul_romanize


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", ""),
        ("가", "ga"),
        ("힣", "hih"),
        ("밝", "balg"),
        ("밯망희", "bahmanghui"),
        ("안녕하세요", "annyeonghase-yo"),
        ("집", "jib"),
        ("짚", "jip"),
        ("밖", "bakk"),
        ("값", "gabs"),
        ("붓꽃", "buskkoch"),
        ("먹는", "meogneun"),
        ("독립", "doglib"),
        ("문리", "munli"),
        ("물엿", "mul-yeos"),
        ("굳이", "gud-i"),
        ("좋다", "johda"),
        ("가곡", "gagog"),
        ("조랑말", "jolangmal"),
        ("없었습니다", "eobs-eoss-seubnida"),
        ("띄고 문장부호! 있고!? @#())$#@()", "ttuigo munjangbuho! issgo!? @#())$#@()"),
    ],
)
def test_hangul_romanize(text, expected):
    assert hangul_romanize(text) == expected
