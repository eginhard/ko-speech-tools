# SPDX-FileCopyrightText: 2017 Joshua Dong <jdong42@gmail.com>
# SPDX-FileContributor: 2025 Enno Hermann
#
# SPDX-License-Identifier: Apache-2.0

"""Syllable and jamo analysis for Korean.

Default internal exchange form is Hangul characters, not codepoints. Jamo
exchange form is U+11xx characters, not U+3xxx Hangul Compatibility Jamo (HCJ)
characters or codepoints.

For more information, see:
http://python-jamo.readthedocs.org/ko/latest/

Adapted from:
https://github.com/jdongian/python-jamo

The original functionality is maintained. Main changes include:
- Code simplification.
- Adding type hints and docstrings.
- Update to modern Python standards.
"""

from __future__ import annotations

import json
import re
from importlib.resources import files
from itertools import chain
from typing import TYPE_CHECKING, Literal

if TYPE_CHECKING:
    from collections.abc import Generator, Iterable

_DATA_PATH = files("ko_speech_tools.data.jamo")

_JAMO_OFFSET = 44032
_JAMO_LEAD_OFFSET = 0x10FF
_JAMO_VOWEL_OFFSET = 0x1160
_JAMO_TAIL_OFFSET = 0x11A7

with _DATA_PATH.joinpath("U+11xx.json").open(encoding="utf-8") as namedata:
    _JAMO_TO_NAME: dict[str, str] = json.load(namedata)
_JAMO_REVERSE_LOOKUP = {name: char for char, name in _JAMO_TO_NAME.items()}
with _DATA_PATH.joinpath("U+31xx.json").open(encoding="utf-8") as namedata:
    _HCJ_TO_NAME: dict[str, str] = json.load(namedata)
_HCJ_REVERSE_LOOKUP = {name: char for char, name in _HCJ_TO_NAME.items()}
with _DATA_PATH.joinpath("decompositions.json").open(encoding="utf-8") as namedata:
    _JAMO_TO_COMPONENTS: dict[str, str] = json.load(namedata)
_COMPONENTS_REVERSE_LOOKUP = {
    tuple(comps): char for char, comps in _JAMO_TO_COMPONENTS.items()
}

JAMO_LEADS = [chr(_) for _ in range(0x1100, 0x115F)]
JAMO_LEADS_MODERN = [chr(_) for _ in range(0x1100, 0x1113)]
JAMO_VOWELS = [chr(_) for _ in range(0x1161, 0x11A8)]
JAMO_VOWELS_MODERN = [chr(_) for _ in range(0x1161, 0x1176)]
JAMO_TAILS = [chr(_) for _ in range(0x11A8, 0x1200)]
JAMO_TAILS_MODERN = [chr(_) for _ in range(0x11A8, 0x11C3)]
JAMO_COMPOUNDS = _JAMO_TO_COMPONENTS.keys()


class InvalidJamoError(Exception):
    """Exception raised for invalid jamo characters.

    Attributes:
        jamo: Hexadecimal representation of the invalid jamo codepoint.
    """

    def __init__(self, message: str, jamo: str) -> None:
        """Initialize InvalidJamoError.

        Args:
            message: Error message describing the invalid jamo.
            jamo: The invalid jamo character that caused the error.
        """
        super().__init__(message)
        self.jamo = hex(ord(jamo))


def _hangul_char_to_jamo(syllable: str) -> tuple[str, str] | tuple[str, str, str] | str:
    """Return a 2-tuple or 3-tuple of lead, vowel, and tail jamo characters.

    Note: Non-Hangul characters are echoed back.
    """
    if is_hangul_char(syllable):
        rem = ord(syllable) - _JAMO_OFFSET
        tail = rem % 28
        vowel = 1 + ((rem - tail) % 588) // 28
        lead = 1 + rem // 588
        if tail:
            return (
                chr(lead + _JAMO_LEAD_OFFSET),
                chr(vowel + _JAMO_VOWEL_OFFSET),
                chr(tail + _JAMO_TAIL_OFFSET),
            )
        return (chr(lead + _JAMO_LEAD_OFFSET), chr(vowel + _JAMO_VOWEL_OFFSET))
    return syllable


def _jamo_to_hangul_char(lead: str, vowel: str, tail: str | None = None) -> str:
    """Return the Hangul character for the given jamo characters."""
    lead_val = ord(lead) - _JAMO_LEAD_OFFSET
    vowel_val = ord(vowel) - _JAMO_VOWEL_OFFSET
    tail_val = ord(tail) - _JAMO_TAIL_OFFSET if tail else 0
    return chr(tail_val + (vowel_val - 1) * 28 + (lead_val - 1) * 588 + _JAMO_OFFSET)


def _jamo_char_to_hcj(char: str) -> str:
    if is_jamo(char):
        hcj_name = re.sub(r"(?<=HANGUL )(\w+)", "LETTER", _get_unicode_name(char))
        if hcj_name in _HCJ_REVERSE_LOOKUP:
            return _HCJ_REVERSE_LOOKUP[hcj_name]
    return char


def _get_unicode_name(char: str) -> str:
    """Fetch the unicode name for jamo characters."""
    if char not in _JAMO_TO_NAME and char not in _HCJ_TO_NAME:
        msg = "Not jamo or nameless jamo character"
        raise InvalidJamoError(msg, char)
    if is_hcj(char):
        return _HCJ_TO_NAME[char]
    return _JAMO_TO_NAME[char]


def is_jamo(character: str) -> bool:
    """Test if a single character is a jamo character.

    Valid jamo includes all modern and archaic jamo, as well as all HCJ.
    Non-assigned code points are invalid.
    """
    code = ord(character)
    return (
        0x1100 <= code <= 0x11FF
        or 0xA960 <= code <= 0xA97C
        or 0xD7B0 <= code <= 0xD7C6
        or 0xD7CB <= code <= 0xD7FB
        or is_hcj(character)
    )


def is_jamo_modern(character: str) -> bool:
    """Test if a single character is a modern jamo character.

    Modern jamo includes all U+11xx jamo in addition to HCJ in modern usage,
    as defined in Unicode 7.0.

    WARNING: U+1160 is NOT considered a modern jamo character, but it is listed
    under 'Medial Vowels' in the Unicode 7.0 spec.
    """
    code = ord(character)
    return (
        0x1100 <= code <= 0x1112
        or 0x1161 <= code <= 0x1175
        or 0x11A8 <= code <= 0x11C2
        or is_hcj_modern(character)
    )


def is_hcj(character: str) -> bool:
    """Test if a single character is a HCJ character.

    HCJ is defined as the U+313x to U+318x block, sans two non-assigned code
    points.
    """
    return 0x3131 <= ord(character) <= 0x318E and ord(character) != 0x3164


def is_hcj_modern(character: str) -> bool:
    """Test if a single character is a modern HCJ character.

    Modern HCJ is defined as HCJ that corresponds to a U+11xx jamo character
    in modern usage.
    """
    code = ord(character)
    return 0x3131 <= code <= 0x314E or 0x314F <= code <= 0x3163


def is_hangul_char(character: str) -> bool:
    """Test if char is in U+AC00 to U+D7A3 code block, excluding unassigned codes."""
    return 0xAC00 <= ord(character) <= 0xD7A3


def is_jamo_compound(character: str) -> bool:
    """Test if a single character is a compound.

    Compound: a consonant cluster, double consonant, or dipthong.
    """
    if len(character) != 1:
        return False
    return is_jamo(character) and character in JAMO_COMPOUNDS


def get_jamo_class(jamo: str) -> Literal["lead", "vowel", "tail"]:
    """Determine if a jamo character is a lead, vowel, or tail.

    U+11xx characters are valid arguments. HCJ consonants are not valid here.

    Returns the class ["lead" | "vowel" | "tail"] of a given character.

    Note: jamo class directly corresponds to the Unicode 7.0 specification,
    thus includes filler characters as having a class.
    """
    if jamo in JAMO_LEADS or jamo == chr(0x115F):
        return "lead"
    if jamo in JAMO_VOWELS or jamo == chr(0x1160) or 0x314F <= ord(jamo) <= 0x3163:
        return "vowel"
    if jamo in JAMO_TAILS:
        return "tail"
    msg = "Invalid or classless jamo argument."
    raise InvalidJamoError(msg, jamo)


def jamo_to_hcj(data: Iterable[str]) -> Generator[str]:
    """Convert jamo to HCJ.

    Arguments may be iterables or single characters.

    jamo_to_hcj should convert every jamo character into HCJ in a given input,
    if possible. Anything else is unchanged.

    jamo_to_hcj is the generator version of j2hcj, the string version. Passing
    a character to jamo_to_hcj will still return a generator.
    """
    return (_jamo_char_to_hcj(_) for _ in data)


def j2hcj(jamo: Iterable[str]) -> str:
    """Convert jamo into HCJ.

    Arguments may be iterables or single characters.

    j2hcj should convert every jamo character into HCJ in a given input, if
    possible. Anything else is unchanged.

    j2hcj is the string version of jamo_to_hcj, the generator version.
    """
    return "".join(jamo_to_hcj(jamo))


def hcj_to_jamo(
    hcj_char: str, position: Literal["lead", "vowel", "tail"] = "vowel"
) -> str:
    """Convert a HCJ character to a jamo character.

    Args:
        hcj_char: Single HCJ character to convert.
        position: Desired jamo class ("lead", "vowel", or "tail").

    Returns:
        The corresponding U+11xx jamo character.

    Raises:
        InvalidJamoError: If the input cannot be mapped to jamo.
    """
    if position == "lead":
        jamo_class = "CHOSEONG"
    elif position == "vowel":
        jamo_class = "JUNGSEONG"
    elif position == "tail":
        jamo_class = "JONGSEONG"
    else:
        msg = "No mapping from input to jamo."
        raise InvalidJamoError(msg, hcj_char)
    jamo_name = re.sub(r"(?<=HANGUL )(\w+)", jamo_class, _get_unicode_name(hcj_char))
    if jamo_name in _JAMO_REVERSE_LOOKUP:
        return _JAMO_REVERSE_LOOKUP[jamo_name]
    return hcj_char


def hcj2j(hcj_char: str, position: Literal["lead", "vowel", "tail"] = "vowel") -> str:
    """Convert a HCJ character to a jamo character.

    Identical to hcj_to_jamo().
    """
    return hcj_to_jamo(hcj_char, position)


def hangul_to_jamo(hangul_string: Iterable[str]) -> Generator[str]:
    """Convert a string of Hangul to jamo.

    Arguments may be iterables of characters.

    hangul_to_jamo should split every Hangul character into U+11xx jamo
    characters for any given string. Non-hangul characters are not changed.

    hangul_to_jamo is the generator version of h2j, the string version.
    """
    return (
        _ for _ in chain.from_iterable(_hangul_char_to_jamo(_) for _ in hangul_string)
    )


def h2j(hangul_string: Iterable[str]) -> str:
    """Convert a string of Hangul to jamo.

    Arguments may be iterables of characters.

    h2j should split every Hangul character into U+11xx jamo for any given
    string. Non-hangul characters are not touched.

    h2j is the string version of hangul_to_jamo, the generator version.
    """
    return "".join(hangul_to_jamo(hangul_string))


def jamo_to_hangul(lead: str, vowel: str, tail: str | None = None) -> str:
    """Return the Hangul character for the given jamo input.

    U+11xx jamo characters or HCJ are valid inputs.

    Outputs a one-character Hangul string.

    This function is identical to j2h.
    """
    # Internally, we convert everything to a jamo char,
    # then pass it to _jamo_to_hangul_char
    lead_jamo = hcj_to_jamo(lead, "lead")
    vowel_jamo = hcj_to_jamo(vowel, "vowel")
    tail_jamo: str | None = None
    if tail and ord(tail) != 0:
        tail_jamo = hcj_to_jamo(tail, "tail") if is_hcj(tail) else tail

    if (
        (is_jamo(lead_jamo) and get_jamo_class(lead_jamo) == "lead")
        and (is_jamo(vowel_jamo) and get_jamo_class(vowel_jamo) == "vowel")
        and (
            (not tail_jamo)
            or (is_jamo(tail_jamo) and get_jamo_class(tail_jamo) == "tail")
        )
    ):
        result = _jamo_to_hangul_char(lead_jamo, vowel_jamo, tail_jamo)
        if is_hangul_char(result):
            return result
    msg = "Could not synthesize characters to Hangul."
    raise InvalidJamoError(msg, "\x00")


def j2h(lead: str, vowel: str, tail: str | None = None) -> str:
    """Return the Hangul character for the given jamo input.

    U+11xx jamo characters or HCJ are valid inputs.

    Outputs a one-character Hangul string.

    This function is defined solely for naming consistency with
    jamo_to_hangul.
    """
    return jamo_to_hangul(lead, vowel, tail)


def decompose_jamo(compound: str) -> tuple[str, ...] | str:
    """Return a tuple of jamo character constituents of a compound.

    Note: Non-compound characters are echoed back.

    WARNING: Archaic jamo compounds will raise NotImplementedError.
    """
    if len(compound) != 1:
        msg = (
            "decompose_jamo() expects a single character, but received "
            f"{type(compound)} length {len(compound)}"
        )
        raise TypeError(msg)
    if compound not in JAMO_COMPOUNDS:
        return compound
    return _JAMO_TO_COMPONENTS.get(compound, compound)


def compose_jamo(*parts: str) -> str:
    """Compose jamo characters into a compound jamo.

    U+11xx jamo characters or HCJ are valid inputs.

    Args:
        *parts: 2-3 single jamo characters to compose.

    Returns:
        A single compound jamo character (e.g., ㄳ, ㅘ).

    Raises:
        TypeError: If parts count is not 2-3 or if any part is not a single character.
        InvalidJamoError: If the parts cannot be composed into a valid compound.
    """
    if not (
        2 <= len(parts) <= 3 and all(isinstance(p, str) and len(p) == 1 for p in parts)
    ):
        msg = f"compose_jamo() expected 2-3 single characters but received {parts}"
        raise TypeError(msg)

    hcparts = tuple(j2hcj(_) for _ in parts)
    if hcparts in _COMPONENTS_REVERSE_LOOKUP:
        return _COMPONENTS_REVERSE_LOOKUP[hcparts]

    parts_repr = ", ".join(f"{p}(U+{ord(p):X})" for p in parts)
    msg = f"Could not synthesize characters to compound: {parts_repr}"
    raise InvalidJamoError(msg, "\x00")


def synth_hangul(string: str) -> str:
    """Convert jamo characters in a string into hcj as much as possible."""
    raise NotImplementedError
