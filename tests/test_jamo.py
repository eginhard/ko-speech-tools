# SPDX-FileCopyrightText: 2017 Joshua Dong <jdong42@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for functional tests on Hangul <-> jamo toolkit.

Source:
https://github.com/jdongian/python-jamo
"""

import itertools
import random
import types

import pytest

from ko_speech_tools import jamo

# Corresponding HCJ for all valid leads in modern Hangul.
_HCJ_LEADS_MODERN = list("ㄱㄲㄴㄷㄸㄹㅁㅂㅃㅅㅆㅇㅈㅉㅊㅋㅌㅍㅎ")
# Corresponding HCJ for all valid vowels in modern Hangul.
# "ㅏㅐㅑㅒㅓㅔㅕㅖㅗㅘㅙㅚㅛㅜㅝㅞㅟㅠㅡㅢㅣ"
# See http://www.unicode.org/charts/PDF/U3130.pdf
_HCJ_VOWELS_MODERN = [chr(_) for _ in range(0x314F, 0x3164)]
# Corresponding HCJ for all valid tails in modern Hangul.
_HCJ_TAILS_MODERN = "ㄱㄲㄳㄴㄵㄶㄷㄹㄺㄻㄼㄽㄾㄿㅀㅁㅂㅄㅅㅆㅇㅈㅊㅋㅌㅍㅎ"

# Common invalid test data (non-jamo characters)
_INVALID_CHARS_BASE = "abABzyZY ,.:;~`―—–/!@#$%^&*()[]{}"  # ruff: ignore[ambiguous-unicode-character-string]


def _get_random_hangul(count=(0xD7A4 - 0xAC00)):
    """Generate a sequence of random, unique, valid Hangul characters.
    Returns all possible modern Hangul characters by default.
    """
    valid_hangul = [chr(_) for _ in range(0xAC00, 0xD7A4)]
    return random.sample(valid_hangul, count)


def test_is_jamo():
    """is_jamo tests
    Test if a single character is a jamo character.
    Valid jamo includes all modern and archaic jamo, as well as all HCJ.
    Non-assigned code points are invalid.
    """
    # See http://www.unicode.org/charts/PDF/U1100.pdf
    valid_jamo = (chr(_) for _ in range(0x1100, 0x1200))
    # See http://www.unicode.org/charts/PDF/U3130.pdf
    valid_hcj = itertools.chain(
        (chr(_) for _ in range(0x3131, 0x3164)),
        (chr(_) for _ in range(0x3165, 0x318F)),
    )
    # See http://www.unicode.org/charts/PDF/UA960.pdf
    valid_ext_a = (chr(_) for _ in range(0xA960, 0xA97D))
    # See http://www.unicode.org/charts/PDF/UD7B0.pdf
    valid_ext_b = itertools.chain(
        (chr(_) for _ in range(0xD7B0, 0xD7C7)),
        (chr(_) for _ in range(0xD7CB, 0xD7FC)),
    )

    invalid_edge_cases = (
        chr(0x10FF),
        chr(0x1200),
        chr(0x3130),
        chr(0x3164),
        chr(0x318F),
        chr(0xA95F),
        chr(0xA07D),
        chr(0xD7AF),
        chr(0xD7C7),
        chr(0xD7CA),
        chr(0xD7FC),
    )
    invalid_hangul = _get_random_hangul(20)
    invalid_other = _INVALID_CHARS_BASE

    # Positive tests
    for _ in itertools.chain(valid_jamo, valid_hcj, valid_ext_a, valid_ext_b):
        assert jamo.is_jamo(_), f"Incorrectly decided U+{ord(_):X} was not jamo."
    # Negative tests
    for _ in itertools.chain(invalid_edge_cases, invalid_hangul, invalid_other):
        assert not jamo.is_jamo(_), f"Incorrectly decided U+{ord(_):X} was jamo."


def test_is_jamo_modern():
    """is_jamo_modern tests
    Test if a single character is a modern jamo character.
    Modern jamo includes all U+11xx jamo in addition to HCJ in usage.
    """
    modern_jamo = itertools.chain(
        jamo.JAMO_LEADS_MODERN, jamo.JAMO_VOWELS_MODERN, jamo.JAMO_TAILS_MODERN
    )
    modern_hcj = itertools.chain(
        _HCJ_LEADS_MODERN, _HCJ_VOWELS_MODERN, _HCJ_TAILS_MODERN
    )

    invalid_edge_cases = (
        chr(0x10FF),
        chr(0x1113),
        chr(0x1160),
        chr(0x1176),
        chr(0x11A7),
        chr(0x11C3),
    )
    invalid_hangul = _get_random_hangul(20)
    invalid_other = _INVALID_CHARS_BASE + "ᄓ"

    # Positive tests
    for _ in itertools.chain(modern_jamo, modern_hcj):
        assert jamo.is_jamo_modern(_), (
            f"Incorrectly decided U+{ord(_):X} was not modern jamo."
        )
    # Negative tests
    for _ in itertools.chain(invalid_edge_cases, invalid_hangul, invalid_other):
        assert not jamo.is_jamo_modern(_), (
            f"Incorrectly decided U+{ord(_):X} was modern jamo."
        )


def test_is_hcj():
    """is_hcj tests
    Test if a single character is a HCJ character.
    HCJ is defined as the U+313x to U+318x block, sans two non-assigned
    code points.
    """
    # Note: The chaeum filler U+3164 is not considered HCJ, but a special
    # character as defined in http://www.unicode.org/charts/PDF/U3130.pdf.
    valid_hcj = itertools.chain(
        (chr(_) for _ in range(0x3131, 0x3164)),
        (chr(_) for _ in range(0x3165, 0x318F)),
    )

    invalid_edge_cases = (chr(0x3130), chr(0x3164), chr(0x318F))
    invalid_hangul = _get_random_hangul(20)
    invalid_other = _INVALID_CHARS_BASE + "ᄀᄓᅡᅶᆨᇃᇿ"

    # Positive tests
    for _ in valid_hcj:
        assert jamo.is_hcj(_), f"Incorrectly decided U+{ord(_):X} was not hcj."
    # Negative tests
    for _ in itertools.chain(invalid_edge_cases, invalid_hangul, invalid_other):
        assert not jamo.is_hcj(_), f"Incorrectly decided U+{ord(_):X} was hcj."


def test_is_hcj_modern():
    """is_hcj_modern tests
    Test if a single character is a modern HCJ character.
    Modern HCJ is defined as HCJ that corresponds to a U+11xx jamo
    character in modern usage.
    """
    # Note: The chaeum filler U+3164 is not considered HCJ, but a special
    # character as defined in http://www.unicode.org/charts/PDF/U3130.pdf.
    valid_hcj_modern = (chr(_) for _ in range(0x3131, 0x3164))

    invalid_edge_cases = (chr(0x3130), chr(0x3164))
    invalid_hangul = _get_random_hangul(20)
    invalid_other = _INVALID_CHARS_BASE + "ᄀᄓᅡᅶᆨᇃᇿㆎㅥ"

    # Positive tests
    for _ in valid_hcj_modern:
        assert jamo.is_hcj_modern(_), (
            f"Incorrectly decided U+{ord(_):X} was not modern hcj."
        )
    # Negative tests
    for _ in itertools.chain(invalid_edge_cases, invalid_hangul, invalid_other):
        assert not jamo.is_hcj_modern(_), (
            f"Incorrectly decided U+{ord(_):X} was modern hcj."
        )


def test_is_hangul_char():
    """is_hangul_char tests
    Test if a single character is in the U+AC00 to U+D7A3 code block,
    excluding unassigned codes.
    """
    hardcoded_tests = "가나다한글한극어힣"

    invalid_edge_cases = (chr(0xABFF), chr(0xD7A4))
    invalid_other = "ㄱㄴㅓ" + _INVALID_CHARS_BASE + "ᄀᄓᅡᅶᆨᇃᇿㆎㅥ"

    for _ in itertools.chain(hardcoded_tests, _get_random_hangul(1024)):
        assert jamo.is_hangul_char(_), (
            f"Incorrectly decided U+{ord(_):X} was not a hangul character."
        )
    for _ in itertools.chain(invalid_edge_cases, invalid_other):
        assert not jamo.is_hangul_char(_), (
            f"Incorrectly decided U+{ord(_):X} was a hangul character."
        )


def test_get_jamo_class():
    """get_jamo_class tests
    Valid arguments are U+11xx characters (not HCJ).

    get_jamo_class should return the class ["lead" | "vowel" | "tail"] of
    a given character.

    Note: strict adherence to Unicode 7.0
    """
    # Note: Fillers are considered initial consonants according to
    # www.unicode.org/charts/PDF/U1100.pdf
    all_tests = itertools.chain(
        ((chr(_), "lead") for _ in range(0x1100, 0x1160)),
        ((chr(_), "vowel") for _ in range(0x1160, 0x11A8)),
        ((chr(_), "tail") for _ in range(0x11A8, 0x1200)),
    )

    for test, target in all_tests:
        trial = jamo.get_jamo_class(test)
        assert trial == target, (
            f"Incorrectly decided {ord(test):X} was a {trial}. (it's a {target})"
        )


@pytest.mark.parametrize("char", [chr(0x10FF), chr(0x1200), "a", "~"])
def test_get_jamo_class_invalid(char):
    """An InvalidJamoError exception is thrown if invalid input is used."""
    with pytest.raises(jamo.InvalidJamoError):
        jamo.get_jamo_class(char)


@pytest.mark.parametrize("text", ["", "ᄂᄃ"])
def test_get_jamo_class_invalid_other(text):
    with pytest.raises((TypeError, jamo.InvalidJamoError)):
        jamo.get_jamo_class(text)


def test_jamo_to_hcj():
    """jamo_to_hcj tests.

    Arguments may be iterables or single characters.

    jamo_to_hcj (generator) should convert every U+11xx jamo character into
    U+31xx HCJ in a given input. Anything else is unchanged.
    """
    test_chars = itertools.chain(
        jamo.JAMO_LEADS_MODERN, jamo.JAMO_VOWELS_MODERN, jamo.JAMO_TAILS_MODERN
    )
    target_chars = itertools.chain(
        _HCJ_LEADS_MODERN, _HCJ_VOWELS_MODERN, _HCJ_TAILS_MODERN
    )
    # TODO: Complete archaic jamo coverage
    test_archaic = ["ᄀᄁᄂᄃᇹᇫ"]
    target_archaic = ["ㄱㄲㄴㄷㆆㅿ"]
    test_strings_idempotent = [
        "",
        _INVALID_CHARS_BASE,
        "汉语 / 漢語; Hànyǔ or 中文; Zhōngwén",
        "ㄱㆎ",
    ]
    target_strings_idempotent = test_strings_idempotent
    # TODO: Add more tests for unmapped jamo characters.
    test_strings_unmapped = ["ᅶᅷᅸᅹᅺᅻᅼᅽᅾᅿᆆ", ""]
    target_strings_unmapped = test_strings_unmapped

    all_tests = itertools.chain(
        zip(test_chars, target_chars, strict=True),
        zip(test_archaic, target_archaic, strict=True),
        zip(test_strings_idempotent, target_strings_idempotent, strict=True),
        zip(test_strings_unmapped, target_strings_unmapped, strict=True),
    )

    for test, target in all_tests:
        trial = jamo.jamo_to_hcj(test)
        assert isinstance(trial, types.GeneratorType), (
            "jamo_to_hcj didn't return an instance of a generator."
        )
        trial, target = "".join(trial), "".join(target)
        test_str = "".join(test)
        assert trial == target, f"Matched {test_str} to {trial}, but expected {target}."


@pytest.mark.parametrize(
    ("test", "target"),
    [("", ""), ("test123", "test123"), ("ᄀᄁᄂᄃᇹᇫ", "ㄱㄲㄴㄷㆆㅿ")],
)
def test_j2hcj(test, target):
    """j2hcj is the string version of jamo_to_hcj."""
    assert jamo.j2hcj(test) == target


@pytest.mark.parametrize("func", [jamo.hcj_to_jamo, jamo.hcj2j])
@pytest.mark.parametrize(
    ("jamo_char", "jamo_class", "target"),
    [
        ("ㄱ", "lead", chr(0x1100)),
        ("ㄱ", "tail", chr(0x11A8)),
        ("ㅎ", "lead", chr(0x1112)),
        ("ㅎ", "tail", chr(0x11C2)),
        ("ㅹ", "lead", chr(0x112C)),
        ("ㅥ", "tail", chr(0x11FF)),
        ("ㅏ", "vowel", chr(0x1161)),
        ("ㅣ", "vowel", chr(0x1175)),
    ],
)
def test_hcj_to_jamo(func, jamo_char, jamo_class, target):
    """hcj_to_jamo and hcj2j tests (hcj2j is an alias for hcj_to_jamo).

    Arguments may be single characters along with the desired jamo class
    (lead, vowel, tail).
    """
    trial = func(jamo_char, jamo_class)
    assert trial == target, (
        f"{func.__name__}: Converted {ord(jamo_char):X} as {jamo_class} to "
        f"{ord(trial):X}, but expected {ord(target):X}."
    )


@pytest.mark.parametrize(
    ("hangul", "target"),
    [
        ("자", (chr(0x110C), chr(0x1161))),
        ("모", (chr(0x1106), chr(0x1169))),
        ("한", (chr(0x1112), chr(0x1161), chr(0x11AB))),
        ("글", (chr(0x1100), chr(0x1173), chr(0x11AF))),
        ("서", (chr(0x1109), chr(0x1165))),
        ("울", (chr(0x110B), chr(0x116E), chr(0x11AF))),
        ("평", (chr(0x1111), chr(0x1167), chr(0x11BC))),
        ("양", (chr(0x110B), chr(0x1163), chr(0x11BC))),
        (
            "한굴",
            (
                chr(0x1112),
                chr(0x1161),
                chr(0x11AB),
                chr(0x1100),
                chr(0x116E),
                chr(0x11AF),
            ),
        ),
        (
            "Do you speak 한국어?",
            (
                *"Do you speak ",
                chr(0x1112),
                chr(0x1161),
                chr(0x11AB),
                chr(0x1100),
                chr(0x116E),
                chr(0x11A8),
                chr(0x110B),
                chr(0x1165),
                "?",
            ),
        ),
        (
            "자모=字母",
            (chr(0x110C), chr(0x1161), chr(0x1106), chr(0x1169), "=", "字", "母"),
        ),
    ],
)
def test_hangul_to_jamo(hangul, target):
    """hangul_to_jamo tests
    Arguments may be iterables or characters.

    hangul_to_jamo should split every Hangul character into U+11xx jamo
    for any given string. Anything else is unchanged.
    """
    trial = jamo.hangul_to_jamo(hangul)
    assert isinstance(trial, types.GeneratorType), (
        "hangul_to_jamo didn't return an instance of a generator."
    )
    trial = tuple(trial)
    assert trial == target, (
        f"Converted {hangul} to {[hex(ord(_)) for _ in trial]}, "
        f"but expected {[hex(ord(_)) for _ in target]}."
    )


@pytest.mark.parametrize(
    ("test", "target"),
    [
        ("한굴", "한굴"),
        ("자모=字母", "자모=字母"),
        # Idempotent
        ("", ""),
        ("test123~", "test123~"),
        ("ㄱㄲㄴㄷㆆㅿ", "ㄱㄲㄴㄷㆆㅿ"),
    ],
)
def test_h2j(test, target):
    """h2j tests
    Arguments may be iterables or characters.

    h2j should split every Hangul character into U+11xx jamo for any given
    string. Anything else is unchanged.
    """
    trial = jamo.h2j(test)
    assert trial == target, f"Converted {test} to {trial}, but expected {target}."


@pytest.mark.parametrize(
    ("args", "hangul"),
    [
        # Support jamo -> Hangul conversion.
        ((chr(0x110C), chr(0x1161), chr(0)), "자"),
        ((chr(0x1106), chr(0x1169), chr(0)), "모"),
        ((chr(0x1112), chr(0x1161), chr(0x11AB)), "한"),
        ((chr(0x1100), chr(0x1173), chr(0x11AF)), "글"),
        ((chr(0x1109), chr(0x1165), chr(0)), "서"),
        ((chr(0x110B), chr(0x116E), chr(0x11AF)), "울"),
        ((chr(0x1111), chr(0x1167), chr(0x11BC)), "평"),
        ((chr(0x110B), chr(0x1163), chr(0x11BC)), "양"),
        # Support HCJ -> Hangul conversion.
        (("ㅈ", "ㅏ", ""), "자"),
        (("ㅁ", "ㅗ", ""), "모"),
        (("ㅎ", "ㅏ", "ㄴ"), "한"),
        (("ㄱ", "ㅡ", "ㄹ"), "글"),
        (("ㅅ", "ㅓ", ""), "서"),
        (("ㅇ", "ㅜ", "ㄹ"), "울"),
        (("ㅍ", "ㅕ", "ㅇ"), "평"),
        (("ㅇ", "ㅑ", "ㅇ"), "양"),
        # Test the arity 2 version.
        (("ㅎ", "ㅏ"), "하"),
        # Support mixed jamo and hcj conversion.
        (("ᄒ", "ㅏ", "ㄴ"), "한"),
    ],
)
def test_jamo_to_hangul(args, hangul):
    """jamo_to_hangul tests
    Arguments may be jamo characters including HCJ.

    Outputs a single Hangul character.
    """
    trial = jamo.jamo_to_hangul(*args)
    assert trial == hangul, (
        f"Incorrect conversion from ({args}) to ({hangul}). Got {trial}."
    )


@pytest.mark.parametrize(
    "args", [("a", "b", "c"), ("a", "b"), ("ㄴ", "ㄴ", "ㄴ"), ("ㅏ", "ㄴ")]
)
def test_jamo_to_hangul_invalid(args):
    """Throws an InvalidJamoError if there is no corresponding Hangul character
    to the inputs.
    """
    with pytest.raises(jamo.InvalidJamoError):
        jamo.jamo_to_hangul(*args)


def test_j2h():
    """j2h hardcoded tests.
    Arguments may be integers corresponding to the U+11xx codepoints, the
    actual U+11xx jamo characters, or HCJ.

    Outputs a one-character Hangul string.

    This function is defined solely for naming consistency with
    jamo_to_hangul.
    """
    assert jamo.j2h("ㅎ", "ㅏ", "ㄴ") == "한"
    assert jamo.j2h("ㅎ", "ㅏ") == "하"


def test_decompose_jamo():
    """decompose_jamo tests
    Arguments should be compound jamo - double consonants, consonant
    clusters, or dipthongs.

    Should output a tuple of non-compound jamo for every compound
    jamo.
    """
    invalid_hangul = _get_random_hangul(20)
    invalid_other = _INVALID_CHARS_BASE

    # TODO: Expand tests to be more comprehensive, maybe use unicode names.
    test_chars = ["ㄸ", "ㅢ"]
    target_chars = [("ㄷ", "ㄷ"), ("ㅡ", "ㅣ")]

    test_chars_idempotent = list(itertools.chain(invalid_hangul, invalid_other))
    target_chars_idempotent = test_chars_idempotent

    all_tests = itertools.chain(
        zip(test_chars, target_chars, strict=True),
        zip(test_chars_idempotent, target_chars_idempotent, strict=True),
    )

    for test, target in all_tests:
        trial = jamo.decompose_jamo(test)
        assert not any(jamo.is_jamo_compound(c) for c in trial), (
            "decompose_jamo returned a compound"
        )
        # Test for strict version of decompose_jamo():
        # assert 2 <= len(trial) <= 3,\
        #     "decompose_jamo failed to return a tuple of 2-3 jamo " +\
        #     "and instead returned " + str(trial) + " for " + str(test)
        if trial != test:  # for lenient version ONLY
            for trial_char in trial:
                assert jamo.is_jamo(trial_char), (
                    "decompose_jamo returned non-jamo character"
                )
        trial, target = "".join(trial), "".join(target)
        test_str = "".join(test)
        assert trial == target, f"Matched {test_str} to {trial}, but expected {target}."


@pytest.mark.parametrize("text", ["ab", "ㄸㄲ"])
def test_decompose_jamo_invalid(text):
    with pytest.raises(TypeError):
        jamo.decompose_jamo(text)


@pytest.mark.parametrize(
    ("test", "target"),
    [
        # TODO: Expand tests to be more comprehensive, maybe use unicode names
        (("ㄷ", "ㄷ"), "ㄸ"),
        (("ᄃ", "ㄷ"), "ㄸ"),
        (("ᄃ", "ᄃ"), "ㄸ"),
        (("ㅡ", "ㅣ"), "ㅢ"),
    ],
)
def test_compose_jamo(test, target):
    """compose_jamo tests
    Arguments should be non-compound jamo that combine to form valid
    double consonants, consonant clusters, or dipthongs.

    Should output a compound jamo for every valid combination of
    components.
    """
    trial = jamo.compose_jamo(*test)
    assert jamo.is_jamo(trial), "compose_jamo returned non-jamo character"
    assert jamo.is_jamo_compound(trial), "compose_jamo returned non-compound"
    assert trial == target, (
        f"Matched {''.join(test)} to {trial}, but expected {target}."
    )


@pytest.mark.parametrize("args", [("ㄷ", "ㄷ", "ㄷ"), ("ㅡ", "ㄷ")])
def test_compose_jamo_invalid(args):
    """compose_jamo raises InvalidJamoError for invalid combinations."""
    with pytest.raises((TypeError, jamo.InvalidJamoError)):
        jamo.compose_jamo(*args)


@pytest.mark.parametrize("args", [("ㄹ", "ㅁ", "ㄱ"), ("ㄹ", "ㄹ")])
def test_compose_jamo_not_implemented_archaic(args):
    with pytest.raises((TypeError, jamo.InvalidJamoError, NotImplementedError)):
        jamo.compose_jamo(*args)


def test_is_jamo_compound():
    """Returns True for modern or archaic jamo compounds and False
    for others, raising a TypeError if receiving more than one
    character as input.
    """
    valid_compounds = (
        "ᄁᄄᄈᄊᄍᄓᄔᄕᄖᄗᄘᄙᄚᄛᄜᄝᄞᄟᄠᄡᄢᄣᄤᄥᄦᄧᄨᄩᄪᄫᄬᄭᄮᄯᄰᄱᄲᄳᄴᄵᄶᄷᄸᄹᄺᄻᄽᄿ"
        "ᅁᅂᅃᅄᅅᅆᅇᅈᅉᅊᅋᅍᅏᅑᅒᅓᅖᅗᅘᅚᅛᅜᅝᅞᅪᅫᅬᅯᅰᅱᅴᅶᅷᅸᅹᅺᅻᅼᅽᅾᅿᆀᆁᆂᆃᆄᆅᆆ"
        "ᆇᆈᆉᆊᆋᆌᆍᆎᆏᆐᆑᆒᆓᆔᆕᆖᆗᆘᆙᆚᆛᆜᆝᆟᆠᆡᆢᆣᆤᆥᆦᆧᆩᆪᆬᆭᆰᆱᆲᆳᆴᆵᆶᆹᆻᇃᇄᇅ"
        "ᇆᇇᇈᇉᇊᇋᇌᇍᇎᇏᇐᇑᇒᇓᇔᇕᇖᇗᇘᇙᇚᇛᇜᇝᇞᇟᇠᇡᇢᇣᇤᇥᇦᇧᇨᇩᇪᇬᇭᇮᇯᇱᇲᇳᇴᇵᇶᇷ"
        "ᇸᇺᇻᇼᇽᇾᇿㄲㄳㄵㄶㄸㄺㄻㄼㄽㄾㄿㅀㅃㅄㅆㅉㅘㅙㅚㅝㅞㅟㅢㅥㅦㅧㅨㅩㅪㅫㅬㅭㅮㅯㅰㅱㅲㅳㅴㅵㅶ"
        "ㅷㅸㅹㅺㅻㅼㅽㅾㆀㆂㆃㆄㆅㆇㆈㆉㆊㆋㆌㆎꥠꥡꥢꥣꥤꥥꥦꥧꥨꥩꥪꥫꥬꥭꥮꥯꥰꥱꥲꥳꥴꥵꥶꥷꥸꥹꥺ"
        "ꥻꥼힰힱힲힳힴힵힶힷힸힹힺힻힼힽힾힿퟀퟁퟂퟃퟄퟅퟆퟋퟌퟍퟎퟏퟐퟑퟒퟓퟔퟕퟖퟗퟘퟙퟚퟛퟜퟝퟞퟟퟠퟡ"
        "ퟢퟣퟤퟥퟦퟧퟨퟩퟪퟫퟬퟭퟮퟯퟰퟱퟲퟳퟴퟵퟶퟷퟸퟹퟺퟻᅢᅤᅦᅨㅐㅒㅔㅖ"
    )

    non_compound_jamo = (
        "ᄀᄂᄃᄅᄆᄇᄉᄋᄌᄎᄏᄐᄑᄒᄼᄾᅀᅌᅎᅐᅔᅕᅟᅠᅡᅣᅥᅧᅩᅭᅮᅲᅳᅵᆞᆨᆫᆮᆯᆷᆸᆺᆼᆽᆾᆿ"
        "ᇀᇁᇂᇫᇰㄱㄴㄷㄹㅁ ㅂㅅㅇㅈㅊㅋㅌㅍㅎㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣㅿㆁㆍ"
    )
    invalid_hangul = _get_random_hangul(20)
    invalid_other = _INVALID_CHARS_BASE

    # Positive tests
    for valid_compound in valid_compounds:
        assert jamo.is_jamo_compound(valid_compound), (
            f"Incorrectly decided U+{ord(valid_compound):X} was not a jamo compound."
        )
    # Negative tests
    for invalid_case in itertools.chain(
        non_compound_jamo, invalid_hangul, invalid_other
    ):
        assert not jamo.is_jamo_compound(invalid_case), (
            f"Incorrectly decided U+{ord(invalid_case):X} was jamo."
        )


def test_synth_hangul():
    """synth_hangul is not yet implemented and should raise NotImplementedError."""
    with pytest.raises(NotImplementedError):
        jamo.synth_hangul("test")
