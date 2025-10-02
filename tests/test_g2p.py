# SPDX-FileCopyrightText: 2019 Kyubyong Park <kbpark.linguist@gmail.com>
# SPDX-FileContributor: Enno Hermann
#
# SPDX-License-Identifier: Apache-2.0

import pytest

from ko_speech_tools import G2p
from ko_speech_tools.g2p.numerals import convert_num, process_num


@pytest.fixture
def g2p():
    return G2p()


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("", ""),
        (
            "포상은 열심히 한 아이에게만 주어지기 때문에 포상인 것입니다.",
            "포상으 녈심히 하 나이에게만 주어지기 때무네 포상인 거심니다.",
        ),
        (
            "오늘 학교에서 밥을 먹고 집에 와서 game을 했다",
            "오늘 학꾜에서 바블 먹꼬 지베 와서 게이믈 핻따",
        ),
        (
            "나의 친구가 mp3 file 3개를 다운받고 있다",
            "나의 친구가 엠피쓰리 파일 세개를 다운받꼬 읻따",
        ),
    ],
)
def test_g2p(g2p, text, expected):
    assert g2p(text) == expected


def test_numerals():
    assert process_num("123,456,789", sino=True) == "일억이천삼백사십오만육천칠백팔십구"
    assert (
        process_num("123,456,789", sino=False) == "일억이천삼백사십오만육천칠백여든아홉"
    )

    assert convert_num("우리 3시/B 10분/B에 만나자.") == "우리 세시/B 십분/B에 만나자."
