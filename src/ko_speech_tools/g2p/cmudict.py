# SPDX-FileCopyrightText: 2017 Keith Ito <keeeto@gmail.com>
# SPDX-FileContributor: 2025 Enno Hermann
#
# SPDX-License-Identifier: MIT

"""CMUDict wrapper.

Adapted from: https://github.com/keithito/tacotron

Changed to use cmudict data from: https://github.com/cmusphinx/cmudict
"""

import re
from collections import defaultdict
from importlib.resources import files
from typing import IO


class CMUDict:
    """Wrapper for CMU Pronouncing Dictionary.

    Provides access to English word pronunciations in ARPAbet format.
    ARPAbet is a phonetic transcription code used for North American English.
    """

    def __init__(self, *, keep_ambiguous: bool = True) -> None:
        """Initialize CMUDict.

        Args:
            keep_ambiguous: If False, exclude words with multiple pronunciations.
        """
        with (
            files("ko_speech_tools.data.cmudict")
            .joinpath("cmudict.dict")
            .open(encoding="utf-8") as f
        ):
            entries = _parse_cmudict(f)
        if not keep_ambiguous:
            entries = {word: pron for word, pron in entries.items() if len(pron) == 1}
        self._entries = entries

    def __len__(self) -> int:
        """Return the number of entries in the dictionary."""
        return len(self._entries)

    def __getitem__(self, word: str) -> list[str]:
        """Return list of ARPAbet pronunciations of the given word."""
        return self._entries[word.lower()]

    def __contains__(self, word: str) -> bool:
        """Check if a word exists in the dictionary.

        Args:
            word: Word to check (case-insensitive).

        Returns:
            True if word is in dictionary, False otherwise.
        """
        return word.lower() in self._entries


_alt_re = re.compile(r"\([0-9]+\)")


def _parse_cmudict(file: IO[str]) -> dict[str, list[str]]:
    cmudict = defaultdict(list)
    for line in file:
        line = line.split("#")[0].strip()  # remove comments
        parts = line.split(" ", maxsplit=1)
        word = re.sub(_alt_re, "", parts[0])
        pronunciation = parts[1].strip()
        cmudict[word].append(pronunciation)
    return dict(cmudict)
