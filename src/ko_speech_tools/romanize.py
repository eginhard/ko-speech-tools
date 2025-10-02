# SPDX-FileCopyrightText: 2015 Jeong YunWon <jeong+hangul-romanize@youknowone.org>
# SPDX-FileContributor: 2025 Enno Hermann
#
# SPDX-License-Identifier: BSD-2-Clause

"""Hangul romanization tool.

Adapted from: https://github.com/youknowone/hangul-romanize

The original functionality is maintained. Main changes include:
- Code simplification.
- Adding type hints and docstrings.
- Update to modern Python standards.
"""

import itertools

# fmt: off
_REVISED_INITIALS = (
    "g", "kk", "n", "d", "tt", "l", "m", "b", "pp", "s", "ss", "", "j", "jj",
    "ch", "k", "t", "p", "h"
)
_REVISED_VOWELS = (
    "a", "ae", "ya", "yae", "eo", "e", "yeo", "ye", "o", "wa", "wae", "oe",
    "yo", "u", "wo", "we", "wi", "yu", "eu", "ui", "i"
)
_REVISED_FINALS = (
    "", "g", "kk", "gs", "n", "nj", "nh", "d", "l", "lg", "lm", "lb", "ls", "lt",
    "lp", "lh", "m", "b", "bs", "s", "ss", "ng", "j", "ch", "k", "t", "p", "h"
)
# fmt: on


def _academic_ambiguous_patterns() -> set[str]:
    """Find final+initial combinations that can be split in multiple ways.

    For example, if "kk" can be split as both ("k", "k") and ("kk", ""),
    it's ambiguous and needs a hyphen marker for clarity.
    """
    ambiguous = set()
    for final, initial in itertools.product(_REVISED_FINALS, _REVISED_INITIALS):
        combined = final + initial

        # Count valid ways to split this combination (excluding boundaries)
        split_count = 0
        for i in range(len(combined)):
            head, tail = combined[:i], combined[i:]
            if head in _REVISED_FINALS and tail in _REVISED_INITIALS:
                split_count += 1
                if split_count > 1:
                    ambiguous.add(combined)
                    break

    return ambiguous


_ACADEMIC_AMBIGUOUS_PATTERNS = _academic_ambiguous_patterns()


class _Syllable:
    """Hangul syllable interface."""

    MIN = ord("가")
    MAX = ord("힣")

    def __init__(self, char: str | None = None, code: int | None = None) -> None:
        if char is None and code is None:
            msg = "__init__ takes char or code as a keyword argument (not given)"
            raise TypeError(msg)
        if char is not None and code is not None:
            msg = "__init__ takes char or code as a keyword argument (both given)"
            raise TypeError(msg)
        if char:
            code = ord(char)
        if not self.MIN <= code <= self.MAX:
            msg = f"Expected Hangul syllable but {code} not in [{self.MIN}..{self.MAX}]"
            raise TypeError(msg)
        self.code = code

    @property
    def index(self) -> int:
        return self.code - self.MIN

    @property
    def initial(self) -> int:
        return self.index // 588

    @property
    def vowel(self) -> int:
        return (self.index // 28) % 21

    @property
    def final(self) -> int:
        return self.index % 28

    @property
    def char(self) -> str:
        return chr(self.code)

    def __str__(self) -> str:
        return self.char

    def __repr__(self) -> str:
        return (
            f"<Syllable({self.code}({self.char}),"
            f"{self.initial},{self.vowel},{self.final})>"
        )


def _academic(
    char: str | None, syllable: _Syllable | None, prev_syllable: _Syllable | None
) -> str | None:
    """Rule for academic transliteration."""
    if not syllable:
        return char

    marker = prev_syllable and (
        _REVISED_INITIALS[syllable.initial] == ""
        or (_REVISED_FINALS[prev_syllable.final] + _REVISED_INITIALS[syllable.initial])
        in _ACADEMIC_AMBIGUOUS_PATTERNS
    )

    result = "-" if marker else ""
    result += (
        _REVISED_INITIALS[syllable.initial]
        + _REVISED_VOWELS[syllable.vowel]
        + _REVISED_FINALS[syllable.final]
    )
    return result


def hangul_romanize(text: str) -> str:
    """Transliterate to romanized text.

    >>> hangul_romanize("물엿")
    'mul-yeos'
    """
    result = []
    prev_syllable = None

    for c in text:
        try:
            syllable = _Syllable(c)
        except TypeError:
            result.append(c)
            prev_syllable = None
            continue

        romanized = _academic(c, syllable, prev_syllable)
        if romanized:
            result.append(romanized)
        prev_syllable = syllable

    return "".join(result)
