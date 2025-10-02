# SPDX-FileCopyrightText: 2017 Joshua Dong <jdong42@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

"""Unit tests for functional tests on Hangul <-> jamo toolkit.

Source:
https://github.com/jdongian/python-jamo"""

import itertools
import random
import types
import unittest

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
_INVALID_CHARS_BASE = "abABzyZY ,.:;~`―—–/!@#$%^&*()[]{}"  # noqa: RUF001


def _get_random_hangul(count=(0xD7A4 - 0xAC00)):
    """Generate a sequence of random, unique, valid Hangul characters.
    Returns all possible modern Hangul characters by default.
    """
    valid_hangul = [chr(_) for _ in range(0xAC00, 0xD7A4)]
    return random.sample(valid_hangul, count)


class TestJamo(unittest.TestCase):
    def test_is_jamo(self):
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

    def test_is_jamo_modern(self):
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

    def test_is_hcj(self):
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

    def test_is_hcj_modern(self):
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

    def test_is_hangul_char(self):
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

    def test_get_jamo_class(self):
        """get_jamo_class tests
        Valid arguments are U+11xx characters (not HCJ). An InvalidJamoError
        exception is thrown if invalid input is used.

        get_jamo_class should return the class ["lead" | "vowel" | "tail"] of
        a given character.

        Note: strict adherence to Unicode 7.0
        """

        # Note: Fillers are considered initial consonants according to
        # www.unicode.org/charts/PDF/U1100.pdf
        leads = (chr(_) for _ in range(0x1100, 0x1160))
        lead_targets = ("lead" for _ in range(0x1100, 0x1160))
        vowels = (chr(_) for _ in range(0x1160, 0x11A8))
        vowel_targets = ("vowel" for _ in range(0x1160, 0x11A8))
        tails = (chr(_) for _ in range(0x11A8, 0x1200))
        tail_targets = ("tail" for _ in range(0x11A8, 0x1200))

        invalid_cases = [chr(0x10FF), chr(0x1200), "a", "~"]
        invalid_other_cases = ["", "ᄂᄃ"]

        all_tests = itertools.chain(
            zip(leads, lead_targets, strict=True),
            zip(vowels, vowel_targets, strict=True),
            zip(tails, tail_targets, strict=True),
        )

        # Test characters
        for test, target in all_tests:
            trial = jamo.get_jamo_class(test)
            assert trial == target, (
                f"Incorrectly decided {ord(test):X} was a {trial}. (it's a {target})"
            )

        # Negative tests
        for _ in invalid_cases:
            with pytest.raises(jamo.InvalidJamoError):
                jamo.get_jamo_class(_)
        for _ in invalid_other_cases:
            with pytest.raises((TypeError, jamo.InvalidJamoError)):
                jamo.get_jamo_class(_)

    def test_jamo_to_hcj(self):
        """jamo_to_hcj and j2hcj tests (j2hcj is string version of jamo_to_hcj).

        Arguments may be iterables or single characters.

        jamo_to_hcj (generator) and j2hcj (string) should convert every U+11xx jamo
        character into U+31xx HCJ in a given input. Anything else is unchanged.
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

        # Test jamo_to_hcj (generator version)
        for test, target in all_tests:
            trial = jamo.jamo_to_hcj(test)
            assert isinstance(trial, types.GeneratorType), (
                "jamo_to_hcj didn't return an instance of a generator."
            )
            trial, target = "".join(trial), "".join(target)
            test_str = "".join(test)
            assert trial == target, (
                f"Matched {test_str} to {trial}, but expected {target}."
            )

        # Test j2hcj (string version)
        test_strings = ["", "test123", "ᄀᄁᄂᄃᇹᇫ"]
        target_strings = ["", "test123", "ㄱㄲㄴㄷㆆㅿ"]

        for test, target in zip(test_strings, target_strings, strict=True):
            trial = jamo.j2hcj(test)
            assert trial == target, (
                "Matched {test} to {trial}, but expected {target}."
            ).format(test="".join(test), trial=trial, target=target)

    def test_hcj_to_jamo(self):
        """hcj_to_jamo and hcj2j tests (hcj2j is an alias for hcj_to_jamo).

        Arguments may be single characters along with the desired jamo class
        (lead, vowel, tail).
        """
        test_args = [
            ("ㄱ", "lead"),
            ("ㄱ", "tail"),
            ("ㅎ", "lead"),
            ("ㅎ", "tail"),
            ("ㅹ", "lead"),
            ("ㅥ", "tail"),
            ("ㅏ", "vowel"),
            ("ㅣ", "vowel"),
        ]
        targets = [
            chr(0x1100),
            chr(0x11A8),
            chr(0x1112),
            chr(0x11C2),
            chr(0x112C),
            chr(0x11FF),
            chr(0x1161),
            chr(0x1175),
        ]

        # Test both hcj_to_jamo and its alias hcj2j
        for func in (jamo.hcj_to_jamo, jamo.hcj2j):
            for (jamo_class, jamo_char), target in zip(test_args, targets, strict=True):
                trial = func(jamo_class, jamo_char)
                assert trial == target, (
                    f"{func.__name__}: Converted {ord(jamo_char):X} as {jamo_class} to "
                    f"{ord(trial):X}, but expected {ord(target):X}."
                )

    def test_hangul_to_jamo(self):
        """hangul_to_jamo tests
        Arguments may be iterables or characters.

        hangul_to_jamo should split every Hangul character into U+11xx jamo
        for any given string. Anything else is unchanged.
        """

        test_cases = [
            "자",
            "모",
            "한",
            "글",
            "서",
            "울",
            "평",
            "양",
            "한굴",
            "Do you speak 한국어?",
            "자모=字母",
        ]
        desired_jamo = [
            (chr(0x110C), chr(0x1161)),
            (chr(0x1106), chr(0x1169)),
            (chr(0x1112), chr(0x1161), chr(0x11AB)),
            (chr(0x1100), chr(0x1173), chr(0x11AF)),
            (chr(0x1109), chr(0x1165)),
            (chr(0x110B), chr(0x116E), chr(0x11AF)),
            (chr(0x1111), chr(0x1167), chr(0x11BC)),
            (chr(0x110B), chr(0x1163), chr(0x11BC)),
            (
                chr(0x1112),
                chr(0x1161),
                chr(0x11AB),
                chr(0x1100),
                chr(0x116E),
                chr(0x11AF),
            ),
            (
                *tuple(_ for _ in "Do you speak "),
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
            (chr(0x110C), chr(0x1161), chr(0x1106), chr(0x1169), "=", "字", "母"),
        ]

        for hangul, target in zip(test_cases, desired_jamo, strict=True):
            trial = jamo.hangul_to_jamo(hangul)
            assert isinstance(trial, types.GeneratorType), (
                "hangul_to_jamo didn't return an instance of a generator."
            )
            trial = tuple(trial)
            if len(hangul) == 1:
                lead = hex(ord(target[0]))
                vowel = hex(ord(target[1]))
                tail = hex(ord(target[2])) if len(target) == 3 else ""
                failure = tuple(hex(ord(_)) for _ in trial)
                error_msg = (
                    f"Converted {hangul} to {failure}, but expected "
                    f"({lead}, {vowel}, {tail})."
                )
            else:
                error_msg = (
                    f"Incorrectly converted {hangul} to {[hex(ord(_)) for _ in trial]}."
                )
            assert target == trial, error_msg

    def test_h2j(self):
        """h2j tests
        Arguments may be iterables or characters.

        h2j should split every Hangul character into U+11xx jamo for any given
        string. Anything else is unchanged.
        """
        tests = ["한굴", "자모=字母"]
        targets = ["한굴", "자모=字母"]
        tests_idempotent = ["", "test123~", "ㄱㄲㄴㄷㆆㅿ"]
        targets_idempotent = tests_idempotent

        all_tests = itertools.chain(
            zip(tests, targets, strict=True),
            zip(tests_idempotent, targets_idempotent, strict=True),
        )

        for test, target in all_tests:
            trial = jamo.h2j(test)
            assert trial == target, (
                f"Converted {test} to {trial}, but expected {target}."
            )

    def test_jamo_to_hangul(self):
        """jamo_to_hangul tests
        Arguments may be jamo characters including HCJ. Throws an
        InvalidJamoError if there is no corresponding Hangul character to the
        inputs.

        Outputs a single Hangul character.
        """

        # Support jamo -> Hangul conversion.
        chr_cases = (
            (chr(0x110C), chr(0x1161), chr(0)),
            (chr(0x1106), chr(0x1169), chr(0)),
            (chr(0x1112), chr(0x1161), chr(0x11AB)),
            (chr(0x1100), chr(0x1173), chr(0x11AF)),
            (chr(0x1109), chr(0x1165), chr(0)),
            (chr(0x110B), chr(0x116E), chr(0x11AF)),
            (chr(0x1111), chr(0x1167), chr(0x11BC)),
            (chr(0x110B), chr(0x1163), chr(0x11BC)),
        )
        # Support HCJ -> Hangul conversion.
        hcj_cases = (
            ("ㅈ", "ㅏ", ""),
            ("ㅁ", "ㅗ", ""),
            ("ㅎ", "ㅏ", "ㄴ"),
            ("ㄱ", "ㅡ", "ㄹ"),
            ("ㅅ", "ㅓ", ""),
            ("ㅇ", "ㅜ", "ㄹ"),
            ("ㅍ", "ㅕ", "ㅇ"),
            ("ㅇ", "ㅑ", "ㅇ"),
        )
        desired_hangul1 = ("자", "모", "한", "글", "서", "울", "평", "양")
        # Test the arity 2 version.
        arity2_cases = (("ㅎ", "ㅏ"),)
        desired_hangul2 = ("하",)
        # Support mixed jamo and hcj conversion.
        mixed_cases = (("ᄒ", "ㅏ", "ㄴ"),)
        desired_hangul3 = ("한",)

        invalid_cases = [("a", "b", "c"), ("a", "b"), ("ㄴ", "ㄴ", "ㄴ"), ("ㅏ", "ㄴ")]

        all_tests = itertools.chain(
            zip(chr_cases, desired_hangul1, strict=True),
            zip(hcj_cases, desired_hangul1, strict=True),
            zip(arity2_cases, desired_hangul2, strict=True),
            zip(mixed_cases, desired_hangul3, strict=True),
        )

        for args, hangul in all_tests:
            trial = jamo.jamo_to_hangul(*args)
            assert hangul == trial, (
                "Conversion from hcj to Hangul failed. "
                "Incorrect conversion from"
                f"({args}) to ({hangul}). Got {trial}."
            )

        # Negative tests
        for _ in invalid_cases:
            with pytest.raises(jamo.InvalidJamoError):
                jamo.jamo_to_hangul(*_)

    def test_j2h(self):
        """j2h hardcoded tests.
        Arguments may be integers corresponding to the U+11xx codepoints, the
        actual U+11xx jamo characters, or HCJ.

        Outputs a one-character Hangul string.

        This function is defined solely for naming consistency with
        jamo_to_hangul.
        """

        assert jamo.j2h("ㅎ", "ㅏ", "ㄴ") == "한", (
            "j2h doesn't work. Hint: it's the same as jamo_to_hangul."
        )

        assert jamo.j2h("ㅎ", "ㅏ") == "하", (
            "j2h doesn't work. Hint: it's the same as jamo_to_hangul."
        )

    def test_decompose_jamo(self):
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

        # Invalid
        invalid_strings = ["ab", "ㄸㄲ"]

        all_tests = itertools.chain(
            zip(test_chars, target_chars, strict=True),
            zip(test_chars_idempotent, target_chars_idempotent, strict=True),
        )

        for test, target in all_tests:
            trial = jamo.decompose_jamo(test)
            assert not jamo.is_jamo_compound(trial), (
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
            assert trial == target, (
                f"Matched {test_str} to {trial}, but expected {target}."
            )

        # Negative tests
        for test_string in invalid_strings:
            with pytest.raises(TypeError):
                jamo.decompose_jamo(test_string)

    def test_compose_jamo(self):
        """compose_jamo tests
        Arguments should be non-compound jamo that combine to form valid
        double consonants, consonant clusters, or dipthongs.

        Should output a compound jamo for every valid combination of
        components and raise InvalidJamoError in all other cases.
        """

        # TODO: Expand tests to be more comprehensive, maybe use unicode names
        test_chars = [("ㄷ", "ㄷ"), ("ᄃ", "ㄷ"), ("ᄃ", "ᄃ"), ("ㅡ", "ㅣ")]
        target_chars = ["ㄸ", "ㄸ", "ㄸ", "ㅢ"]

        # Invalid
        invalid_cases = [("ㄷ", "ㄷ", "ㄷ"), ("ㅡ", "ㄷ")]

        # Not implemented
        not_implemented_archaics = [("ㄹ", "ㅁ", "ㄱ"), ("ㄹ", "ㄹ")]

        all_tests = zip(test_chars, target_chars, strict=True)
        for test, target in all_tests:
            trial = jamo.compose_jamo(*test)
            assert jamo.is_jamo(trial), "compose_jamo returned non-jamo character"
            assert jamo.is_jamo_compound(trial), "compose_jamo returned non-compound"
            trial, target = "".join(trial), "".join(target)
            test_str = "".join(test)
            assert trial == target, (
                f"Matched {test_str} to {trial}, but expected {target}."
            )

        # Negative tests
        for invalid_case in invalid_cases:
            with pytest.raises((TypeError, jamo.InvalidJamoError)):
                jamo.compose_jamo(*invalid_case)
        for not_implemented_archaic in not_implemented_archaics:
            with pytest.raises((TypeError, jamo.InvalidJamoError, NotImplementedError)):
                jamo.compose_jamo(*not_implemented_archaic)

    def test_is_jamo_compound(self):
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
        for valid_compound in itertools.chain(valid_compounds):
            assert jamo.is_jamo_compound(valid_compound), (
                f"Incorrectly decided U+{ord(valid_compound):X} was not a "
                "jamo compound."
            )
        # Negative tests
        for invalid_case in itertools.chain(
            non_compound_jamo, invalid_hangul, invalid_other
        ):
            assert not jamo.is_jamo_compound(invalid_case), (
                f"Incorrectly decided U+{ord(invalid_case):X} was jamo."
            )

    def test_synth_hangul(self):
        """synth_hangul is not yet implemented and should raise NotImplementedError."""
        with pytest.raises(NotImplementedError):
            jamo.synth_hangul("test")
