# SPDX-FileCopyrightText: 2019 Kyubyong Park <kbpark.linguist@gmail.com>
# SPDX-FileContributor: 2025 Enno Hermann
#
# SPDX-License-Identifier: Apache-2.0

"""
Special rule for processing Hangul.

Adapted from: https://github.com/harmlessman/g2pkk

Main change: precompiling regular expressions.
"""

import re

from ko_speech_tools.g2p.utils import get_rule_id2text, gloss

rule_id2text = get_rule_id2text()

# Precompiled regex patterns
_JYEO_RE = re.compile("([ᄌᄍᄎ])ᅧ")
_YE_RE = re.compile("([ᄀᄁᄃᄄㄹᄆᄇᄈᄌᄍᄎᄏᄐᄑᄒ])ᅨ")
_CONSONANT_UI_RE = re.compile("([ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄌᄍᄎᄏᄐᄑᄒ])ᅴ")
_JOSA_UI_RE = re.compile("의/J")
_VOWEL_UI_RE = re.compile(r"(\Sᄋ)ᅴ")
_JAMO_1_RE = re.compile("([그])ᆮᄋ")
_JAMO_2_RE = re.compile("([으])[ᆽᆾᇀᇂ]ᄋ")
_JAMO_3_RE = re.compile("([으])[ᆿ]ᄋ")
_JAMO_4_RE = re.compile("([으])[ᇁ]ᄋ")
_RIEULGIYEOK_RE = re.compile("ᆰ/P([ᄀᄁ])")
_RIEULBIEUB_1_RE = re.compile("([ᆲᆴ])/Pᄀ")
_RIEULBIEUB_2_RE = re.compile("([ᆲᆴ])/Pᄃ")
_RIEULBIEUB_3_RE = re.compile("([ᆲᆴ])/Pᄉ")
_RIEULBIEUB_4_RE = re.compile("([ᆲᆴ])/Pᄌ")
_VERB_NIEUN_1_RE = re.compile("([ᆫᆷ])/Pᄀ")
_VERB_NIEUN_2_RE = re.compile("([ᆫᆷ])/Pᄃ")
_VERB_NIEUN_3_RE = re.compile("([ᆫᆷ])/Pᄉ")
_VERB_NIEUN_4_RE = re.compile("([ᆫᆷ])/Pᄌ")
_VERB_NIEUN_5_RE = re.compile("ᆬ/Pᄀ")
_VERB_NIEUN_6_RE = re.compile("ᆬ/Pᄃ")
_VERB_NIEUN_7_RE = re.compile("ᆬ/Pᄉ")
_VERB_NIEUN_8_RE = re.compile("ᆬ/Pᄌ")
_VERB_NIEUN_9_RE = re.compile("ᆱ/Pᄀ")
_VERB_NIEUN_10_RE = re.compile("ᆱ/Pᄃ")
_VERB_NIEUN_11_RE = re.compile("ᆱ/Pᄉ")
_VERB_NIEUN_12_RE = re.compile("ᆱ/Pᄌ")
_BALB_1_RE = re.compile("(바)ᆲ($|[^ᄋᄒ])")
_BALB_2_RE = re.compile("(너)ᆲ([ᄌᄍ]ᅮ|[ᄃᄄ]ᅮ)")
_PALATALIZE_1_RE = re.compile("ᆮᄋ([ᅵᅧ])")
_PALATALIZE_2_RE = re.compile("ᇀᄋ([ᅵᅧ])")
_PALATALIZE_3_RE = re.compile("ᆴᄋ([ᅵᅧ])")
_PALATALIZE_4_RE = re.compile("ᆮᄒ([ᅵ])")
_MODIFYING_RIEUL_1_RE = re.compile("ᆯ/E ᄀ")
_MODIFYING_RIEUL_2_RE = re.compile("ᆯ/E ᄃ")
_MODIFYING_RIEUL_3_RE = re.compile("ᆯ/E ᄇ")
_MODIFYING_RIEUL_4_RE = re.compile("ᆯ/E ᄉ")
_MODIFYING_RIEUL_5_RE = re.compile("ᆯ/E ᄌ")


############################ vowels ############################
def jyeo(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:  # noqa: ARG001
    """Apply jyeo vowel rule: [ᄌᄍᄎ]ᅧ → [ᄌᄍᄎ]ᅥ.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with jyeo rule applied.
    """
    rule = rule_id2text["5.1"]
    # 일반적인 규칙으로 취급한다 by kyubyong

    out = _JYEO_RE.sub(r"\1ᅥ", inp)
    gloss(verbose, out, inp, rule)
    return out


def ye(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:
    """Apply ye vowel simplification: consonant+ᅨ → consonant+ᅦ (descriptive only).

    Args:
        inp: Input string with jamo characters.
        descriptive: If True, apply the simplification.
        verbose: If True, print transformation details.

    Returns:
        String with ye rule applied.
    """
    rule = rule_id2text["5.2"]
    # 실제로 언중은 예, 녜, 셰, 쎼 이외의 'ㅖ'는 [ㅔ]로 발음한다. by kyubyong

    out = _YE_RE.sub(r"\1ᅦ", inp) if descriptive else inp
    gloss(verbose, out, inp, rule)
    return out


def consonant_ui(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:  # noqa: ARG001
    """Apply consonant+ᅴ → consonant+ᅵ simplification.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with consonant_ui rule applied.
    """
    rule = rule_id2text["5.3"]

    out = _CONSONANT_UI_RE.sub(r"\1ᅵ", inp)
    gloss(verbose, out, inp, rule)
    return out


def josa_ui(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:
    """Handle particle 의/J pronunciation (descriptive: 의→에, otherwise remove tag).

    Args:
        inp: Input string with jamo and annotations.
        descriptive: If True, convert particle 의 to 에.
        verbose: If True, print transformation details.

    Returns:
        String with josa_ui rule applied.
    """
    rule = rule_id2text["5.4.2"]
    # 실제로 언중은 높은 확률로 조사 '의'는 [ㅔ]로 발음한다.
    out = _JOSA_UI_RE.sub("에", inp) if descriptive else inp.replace("/J", "")
    gloss(verbose, out, inp, rule)
    return out


def vowel_ui(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:
    """Apply non-initial ᅴ → ᅵ simplification in descriptive mode.

    Args:
        inp: Input string with jamo characters.
        descriptive: If True, apply the simplification.
        verbose: If True, print transformation details.

    Returns:
        String with vowel_ui rule applied.
    """
    rule = rule_id2text["5.4.1"]
    # 실제로 언중은 높은 확률로 단어의 첫음절 이외의 '의'는 [ㅣ]로 발음한다."""
    out = _VOWEL_UI_RE.sub(r"\1ᅵ", inp) if descriptive else inp
    gloss(verbose, out, inp, rule)
    return out


def jamo(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:  # noqa: ARG001
    """Apply jamo simplification for specific coda+onset combinations.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with jamo simplification applied.
    """
    rule = rule_id2text["16"]
    out = inp

    out = _JAMO_1_RE.sub(r"\1ᄉ", out)
    out = _JAMO_2_RE.sub(r"\1ᄉ", out)
    out = _JAMO_3_RE.sub(r"\1ᄀ", out)
    out = _JAMO_4_RE.sub(r"\1ᄇ", out)

    gloss(verbose, out, inp, rule)
    return out

    ############################ 어간 받침 ############################


def rieulgiyeok(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:  # noqa: ARG001
    """Apply rieul-giyeok tensification: ᆰ/P+ᄀ → ᆯᄁ.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with rieulgiyeok rule applied.
    """
    rule = rule_id2text["11.1"]

    out = inp
    out = _RIEULGIYEOK_RE.sub(r"ᆯᄁ", out)

    gloss(verbose, out, inp, rule)
    return out


def rieulbieub(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:  # noqa: ARG001
    """Apply rieul-bieub tensification for predicate stems: [ᆲᆴ]/P+consonant → tense.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with rieulbieub rule applied.
    """
    rule = rule_id2text["25"]
    out = inp

    out = _RIEULBIEUB_1_RE.sub(r"\1ᄁ", out)
    out = _RIEULBIEUB_2_RE.sub(r"\1ᄄ", out)
    out = _RIEULBIEUB_3_RE.sub(r"\1ᄊ", out)
    out = _RIEULBIEUB_4_RE.sub(r"\1ᄍ", out)

    gloss(verbose, out, inp, rule)
    return out


def verb_nieun(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:  # noqa: ARG001
    """Apply nasal coda tensification for predicate stems: [ᆫᆬᆷᆱ]/P+consonant → tense.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with verb_nieun rule applied.
    """
    rule = rule_id2text["24"]
    out = inp

    out = _VERB_NIEUN_1_RE.sub(r"\1ᄁ", out)
    out = _VERB_NIEUN_2_RE.sub(r"\1ᄄ", out)
    out = _VERB_NIEUN_3_RE.sub(r"\1ᄊ", out)
    out = _VERB_NIEUN_4_RE.sub(r"\1ᄍ", out)
    out = _VERB_NIEUN_5_RE.sub("ᆫᄁ", out)
    out = _VERB_NIEUN_6_RE.sub("ᆫᄄ", out)
    out = _VERB_NIEUN_7_RE.sub("ᆫᄊ", out)
    out = _VERB_NIEUN_8_RE.sub("ᆫᄍ", out)
    out = _VERB_NIEUN_9_RE.sub("ᆷᄁ", out)
    out = _VERB_NIEUN_10_RE.sub("ᆷᄄ", out)
    out = _VERB_NIEUN_11_RE.sub("ᆷᄊ", out)
    out = _VERB_NIEUN_12_RE.sub("ᆷᄍ", out)

    gloss(verbose, out, inp, rule)
    return out


def balb(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:  # noqa: ARG001
    """Apply exceptions for 밟 (balb) pronunciation in specific words.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with balb exceptions applied.
    """
    rule = rule_id2text["10.1"]
    out = inp

    # exceptions
    out = _BALB_1_RE.sub(r"\1ᆸ\2", out)
    out = _BALB_2_RE.sub(r"\1ᆸ\2", out)
    gloss(verbose, out, inp, rule)
    return out


def palatalize(inp: str, *, descriptive: bool = False, verbose: bool = False) -> str:  # noqa: ARG001
    """Apply palatalization: ᆮ+[ᅵᅧ]→ᄌ, ᇀ+[ᅵᅧ]→ᄎ, ᆴ+[ᅵᅧ]→ᆯᄎ, ᆮ히→치.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with palatalization applied.
    """
    rule = rule_id2text["17"]
    out = inp

    out = _PALATALIZE_1_RE.sub(r"ᄌ\1", out)
    out = _PALATALIZE_2_RE.sub(r"ᄎ\1", out)
    out = _PALATALIZE_3_RE.sub(r"ᆯᄎ\1", out)

    out = _PALATALIZE_4_RE.sub(r"ᄎ\1", out)

    gloss(verbose, out, inp, rule)
    return out


def modifying_rieul(
    inp: str,
    *,
    descriptive: bool = False,  # noqa: ARG001
    verbose: bool = False,
) -> str:
    """Apply tensification after rieul adnominal ending: ᆯ/E+consonant → tense.

    Args:
        inp: Input string with jamo characters.
        descriptive: Unused (kept for interface consistency).
        verbose: If True, print transformation details.

    Returns:
        String with modifying_rieul rule applied.
    """
    rule = rule_id2text["27"]
    out = inp

    out = _MODIFYING_RIEUL_1_RE.sub(r"ᆯ ᄁ", out)
    out = _MODIFYING_RIEUL_2_RE.sub(r"ᆯ ᄄ", out)
    out = _MODIFYING_RIEUL_3_RE.sub(r"ᆯ ᄈ", out)
    out = _MODIFYING_RIEUL_4_RE.sub(r"ᆯ ᄊ", out)
    out = _MODIFYING_RIEUL_5_RE.sub(r"ᆯ ᄍ", out)
    out = out.replace("ᆯ걸", "ᆯ껄")
    out = out.replace("ᆯ밖에", "ᆯ빠께")
    out = out.replace("ᆯ세라", "ᆯ쎄라")
    out = out.replace("ᆯ수록", "ᆯ쑤록")
    out = out.replace("ᆯ지라도", "ᆯ찌라도")
    out = out.replace("ᆯ지언정", "ᆯ찌언정")
    out = out.replace("ᆯ진대", "ᆯ찐대")

    gloss(verbose, out, inp, rule)
    return out
