# SPDX-FileCopyrightText: 2019 Kyubyong Park <kbpark.linguist@gmail.com>
# SPDX-FileContributor: 2022 harmlessman <harmlessman17@gmail.com>
# SPDX-FileContributor: 2025 Enno Hermann
#
# SPDX-License-Identifier: Apache-2.0

"""Korean G2P.

Adapted from: https://github.com/harmlessman/g2pkk

The original functionality is maintained. Main changes include:
- Code simplification.
- Adding type hints and docstrings.
- Update to modern Python standards.
"""

import re
from importlib.resources import files
from typing import Any

from ko_speech_tools.g2p.cmudict import CMUDict
from ko_speech_tools.g2p.english import convert_eng
from ko_speech_tools.g2p.numerals import convert_num
from ko_speech_tools.g2p.regular import link1, link2, link3, link4
from ko_speech_tools.g2p.special import (
    balb,
    consonant_ui,
    jamo,
    josa_ui,
    jyeo,
    modifying_rieul,
    palatalize,
    rieulbieub,
    rieulgiyeok,
    verb_nieun,
    vowel_ui,
    ye,
)
from ko_speech_tools.g2p.utils import (
    annotate,
    compose,
    get_rule_id2text,
    gloss,
    group,
    parse_table,
)
from ko_speech_tools.jamo import h2j

# Precompiled regex patterns
_ANNOTATION_TAG_RE = re.compile("/[PJEB]")


class G2p:
    """Korean grapheme-to-phoneme converter.

    Converts Korean text to phonetic representation using a multi-step pipeline:
    idiom replacement, English-to-Hangul conversion, morphological annotation,
    numeral conversion, jamo decomposition, phonological rules, and composition.

    Handles mixed Korean-English text, Arabic numerals, and special phonological
    processes like palatalization, assimilation, and liaison.

    Example:
        >>> g2p = G2p()
        >>> g2p("나의 친구가 mp3 file 3개를 다운받고 있다")
        '나의 친구가 엠피쓰리 파일 세개를 다운받꼬 읻따'
    """

    def __init__(self) -> None:
        """Create a G2p instance."""
        self.mecab = self.get_mecab()
        self.table = parse_table()

        self.cmu = CMUDict()  # for English
        self.rule2text = get_rule_id2text()  # for comments of main rules
        self._read_idioms()

    def get_mecab(self) -> Any:  # noqa: ANN401
        """Get MeCab morphological analyzer for Korean.

        Returns:
            MeCab Tagger instance.

        Raises:
            ImportError: If mecab_ko package is not installed.
        """
        try:
            import mecab_ko  # noqa: PLC0415
        except ImportError as e:
            msg = "G2P requires the mecab_ko package"
            raise ImportError(msg) from e
        return mecab_ko.Tagger()

    def _read_idioms(self) -> None:
        self._idioms = []
        with (
            files("ko_speech_tools.data.g2p")
            .joinpath("idioms.txt")
            .open(encoding="utf-8") as f
        ):
            for line in f:
                line = line.split("#")[0].strip()
                if "===" in line:
                    str1, str2 = line.split("===")
                    self._idioms.append((str1, str2))

    def idioms(self, string: str, *, verbose: bool = False) -> str:
        """Process each line in `idioms.txt`.

        Each line is delimited by "===", and the left string is replaced by the
        right one.

        inp: input string.
        verbose: boolean.

        >>> G2p().idioms("지금 mp3 파일을 다운받고 있어요")
        '지금 엠피쓰리 파일을 다운받고 있어요'
        """
        out = string
        for str1, str2 in self._idioms:
            out = out.replace(str1, str2)
        gloss(verbose, out, string, "from idioms.txt")
        return out

    def __call__(
        self,
        string: str,
        *,
        descriptive: bool = False,
        verbose: bool = False,
        group_vowels: bool = False,
        to_syl: bool = True,
    ) -> str:
        """Run G2P.

        Args:
            string: input string
            descriptive: boolean.
            verbose: boolean
            group_vowels: If True, the vowels of the identical sound are normalized.
            to_syl: If True, hangul letters or jamo are assembled to form syllables.

        For example, given an input string "나의 친구가 mp3 file 3개를 다운받고 있다",
        STEP 1. idioms
        -> 나의 친구가 엠피쓰리 file 3개를 다운받고 있다

        STEP 2. English to Hangul
        -> 나의 친구가 엠피쓰리 파일 3개를 다운받고 있다

        STEP 3. annotate
        -> 나의/J 친구가 엠피쓰리 파일 3개/B를 다운받고 있다

        STEP 4. Spell out arabic numbers
        -> 나의/J 친구가 엠피쓰리 파일 세개/B를 다운받고 있다

        STEP 5. decompose
        -> 나의/J 친구가 엠피쓰리 파일 세개/B를 다운받고 있다

        STEP 6-9. Hangul
        -> 나의 친구가 엠피쓰리 파일 세개를 다운받꼬 읻따
        """
        # 1. idioms
        string = self.idioms(string, verbose=verbose)

        # 2 English to Hangul
        string = convert_eng(string, self.cmu)

        # 3. annotate
        string = annotate(string, self.mecab)

        # 4. Spell out arabic numbers
        string = convert_num(string)

        # 5. decompose
        inp = h2j(string)

        # 6. special
        for func in (
            jyeo,
            ye,
            consonant_ui,
            josa_ui,
            vowel_ui,
            jamo,
            rieulgiyeok,
            rieulbieub,
            verb_nieun,
            balb,
            palatalize,
            modifying_rieul,
        ):
            inp = func(inp, descriptive=descriptive, verbose=verbose)
        inp = _ANNOTATION_TAG_RE.sub("", inp)

        # 7. regular table: batchim + onset
        for str1, str2, rule_ids in self.table:
            _inp = inp
            inp = re.sub(str1, str2, inp)

            if len(rule_ids) > 0:
                rule = "\n".join(
                    self.rule2text.get(rule_id, "") for rule_id in rule_ids
                )
            else:
                rule = ""
            gloss(verbose, inp, _inp, rule)

        # 8 link
        for func in (link1, link2, link3, link4):
            inp = func(inp, verbose=verbose)

        # 9. postprocessing
        if group_vowels:
            inp = group(inp)

        if to_syl:
            inp = compose(inp)
        return inp
