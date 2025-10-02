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

    out = re.sub("([ᄌᄍᄎ])ᅧ", r"\1ᅥ", inp)
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

    if descriptive:
        out = re.sub("([ᄀᄁᄃᄄㄹᄆᄇᄈᄌᄍᄎᄏᄐᄑᄒ])ᅨ", r"\1ᅦ", inp)
    else:
        out = inp
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

    out = re.sub("([ᄀᄁᄂᄃᄄᄅᄆᄇᄈᄉᄊᄌᄍᄎᄏᄐᄑᄒ])ᅴ", r"\1ᅵ", inp)
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
    out = re.sub("의/J", "에", inp) if descriptive else inp.replace("/J", "")
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
    out = re.sub(r"(\Sᄋ)ᅴ", r"\1ᅵ", inp) if descriptive else inp
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

    out = re.sub("([그])ᆮᄋ", r"\1ᄉ", out)
    out = re.sub("([으])[ᆽᆾᇀᇂ]ᄋ", r"\1ᄉ", out)
    out = re.sub("([으])[ᆿ]ᄋ", r"\1ᄀ", out)
    out = re.sub("([으])[ᇁ]ᄋ", r"\1ᄇ", out)

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
    out = re.sub("ᆰ/P([ᄀᄁ])", r"ᆯᄁ", out)

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

    out = re.sub("([ᆲᆴ])/Pᄀ", r"\1ᄁ", out)
    out = re.sub("([ᆲᆴ])/Pᄃ", r"\1ᄄ", out)
    out = re.sub("([ᆲᆴ])/Pᄉ", r"\1ᄊ", out)
    out = re.sub("([ᆲᆴ])/Pᄌ", r"\1ᄍ", out)

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

    pairs = [
        ("([ᆫᆷ])/Pᄀ", r"\1ᄁ"),
        ("([ᆫᆷ])/Pᄃ", r"\1ᄄ"),
        ("([ᆫᆷ])/Pᄉ", r"\1ᄊ"),
        ("([ᆫᆷ])/Pᄌ", r"\1ᄍ"),
        ("ᆬ/Pᄀ", "ᆫᄁ"),
        ("ᆬ/Pᄃ", "ᆫᄄ"),
        ("ᆬ/Pᄉ", "ᆫᄊ"),
        ("ᆬ/Pᄌ", "ᆫᄍ"),
        ("ᆱ/Pᄀ", "ᆷᄁ"),
        ("ᆱ/Pᄃ", "ᆷᄄ"),
        ("ᆱ/Pᄉ", "ᆷᄊ"),
        ("ᆱ/Pᄌ", "ᆷᄍ"),
    ]

    for str1, str2 in pairs:
        out = re.sub(str1, str2, out)

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
    syllable_final_or_consonants = "($|[^ᄋᄒ])"

    # exceptions
    out = re.sub(f"(바)ᆲ({syllable_final_or_consonants})", r"\1ᆸ\2", out)
    out = re.sub("(너)ᆲ([ᄌᄍ]ᅮ|[ᄃᄄ]ᅮ)", r"\1ᆸ\2", out)
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

    out = re.sub("ᆮᄋ([ᅵᅧ])", r"ᄌ\1", out)
    out = re.sub("ᇀᄋ([ᅵᅧ])", r"ᄎ\1", out)
    out = re.sub("ᆴᄋ([ᅵᅧ])", r"ᆯᄎ\1", out)

    out = re.sub("ᆮᄒ([ᅵ])", r"ᄎ\1", out)

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

    pairs = [
        ("ᆯ/E ᄀ", r"ᆯ ᄁ"),
        ("ᆯ/E ᄃ", r"ᆯ ᄄ"),
        ("ᆯ/E ᄇ", r"ᆯ ᄈ"),
        ("ᆯ/E ᄉ", r"ᆯ ᄊ"),
        ("ᆯ/E ᄌ", r"ᆯ ᄍ"),
        ("ᆯ걸", "ᆯ껄"),
        ("ᆯ밖에", "ᆯ빠께"),
        ("ᆯ세라", "ᆯ쎄라"),
        ("ᆯ수록", "ᆯ쑤록"),
        ("ᆯ지라도", "ᆯ찌라도"),
        ("ᆯ지언정", "ᆯ찌언정"),
        ("ᆯ진대", "ᆯ찐대"),
    ]

    for str1, str2 in pairs:
        out = re.sub(str1, str2, out)

    gloss(verbose, out, inp, rule)
    return out
