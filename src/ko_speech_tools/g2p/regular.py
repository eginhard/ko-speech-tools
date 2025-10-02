# SPDX-FileCopyrightText: 2019 Kyubyong Park <kbpark.linguist@gmail.com>
#
# SPDX-License-Identifier: Apache-2.0

"""Source: https://github.com/harmlessman/g2pkk."""

from ko_speech_tools.g2p.utils import get_rule_id2text, gloss

rule_id2text = get_rule_id2text()


def link1(inp: str, *, verbose: bool = False) -> str:
    """Apply basic liaison: simple coda + ᄋ → onset (e.g., ᆨᄋ→ᄀ).

    Args:
        inp: Input string with jamo characters.
        verbose: If True, print transformation details.

    Returns:
        String with link1 rule applied.
    """
    rule = rule_id2text["13"]
    out = inp

    pairs = [
        ("ᆨᄋ", "ᄀ"),
        ("ᆩᄋ", "ᄁ"),
        ("ᆫᄋ", "ᄂ"),
        ("ᆮᄋ", "ᄃ"),
        ("ᆯᄋ", "ᄅ"),
        ("ᆷᄋ", "ᄆ"),
        ("ᆸᄋ", "ᄇ"),
        ("ᆺᄋ", "ᄉ"),
        ("ᆻᄋ", "ᄊ"),
        ("ᆽᄋ", "ᄌ"),
        ("ᆾᄋ", "ᄎ"),
        ("ᆿᄋ", "ᄏ"),
        ("ᇀᄋ", "ᄐ"),
        ("ᇁᄋ", "ᄑ"),
    ]
    for str1, str2 in pairs:
        out = out.replace(str1, str2)

    gloss(verbose, out, inp, rule)
    return out


def link2(inp: str, *, verbose: bool = False) -> str:
    """Apply liaison for compound codas: compound coda + ᄋ → split (e.g., ᆪᄋ→ᆨᄊ).

    Args:
        inp: Input string with jamo characters.
        verbose: If True, print transformation details.

    Returns:
        String with link2 rule applied.
    """
    rule = rule_id2text["14"]
    out = inp

    pairs = [
        ("ᆪᄋ", "ᆨᄊ"),
        ("ᆬᄋ", "ᆫᄌ"),
        ("ᆰᄋ", "ᆯᄀ"),
        ("ᆱᄋ", "ᆯᄆ"),
        ("ᆲᄋ", "ᆯᄇ"),
        ("ᆳᄋ", "ᆯᄊ"),
        ("ᆴᄋ", "ᆯᄐ"),
        ("ᆵᄋ", "ᆯᄑ"),
        ("ᆹᄋ", "ᆸᄊ"),
    ]
    for str1, str2 in pairs:
        out = out.replace(str1, str2)

    gloss(verbose, out, inp, rule)
    return out


def link3(inp: str, *, verbose: bool = False) -> str:
    """Apply liaison across word boundaries (with space between syllables).

    Args:
        inp: Input string with jamo characters.
        verbose: If True, print transformation details.

    Returns:
        String with link3 rule applied.
    """
    rule = rule_id2text["15"]
    out = inp

    pairs = [
        ("ᆨ ᄋ", " ᄀ"),
        ("ᆩ ᄋ", " ᄁ"),
        ("ᆫ ᄋ", " ᄂ"),
        ("ᆮ ᄋ", " ᄃ"),
        ("ᆯ ᄋ", " ᄅ"),
        ("ᆷ ᄋ", " ᄆ"),
        ("ᆸ ᄋ", " ᄇ"),
        ("ᆺ ᄋ", " ᄉ"),
        ("ᆻ ᄋ", " ᄊ"),
        ("ᆽ ᄋ", " ᄌ"),
        ("ᆾ ᄋ", " ᄎ"),
        ("ᆿ ᄋ", " ᄏ"),
        ("ᇀ ᄋ", " ᄐ"),
        ("ᇁ ᄋ", " ᄑ"),
        ("ᆪ ᄋ", "ᆨ ᄊ"),
        ("ᆬ ᄋ", "ᆫ ᄌ"),
        ("ᆰ ᄋ", "ᆯ ᄀ"),
        ("ᆱ ᄋ", "ᆯ ᄆ"),
        ("ᆲ ᄋ", "ᆯ ᄇ"),
        ("ᆳ ᄋ", "ᆯ ᄊ"),
        ("ᆴ ᄋ", "ᆯ ᄐ"),
        ("ᆵ ᄋ", "ᆯ ᄑ"),
        ("ᆹ ᄋ", "ᆸ ᄊ"),
    ]

    for str1, str2 in pairs:
        out = out.replace(str1, str2)

    gloss(verbose, out, inp, rule)
    return out


def link4(inp: str, *, verbose: bool = False) -> str:
    """Apply special liaison for ᇂ, ᆭ, ᆶ before ᄋ (deletion or simplification).

    Args:
        inp: Input string with jamo characters.
        verbose: If True, print transformation details.

    Returns:
        String with link4 rule applied.
    """
    rule = rule_id2text["12.4"]

    out = inp

    pairs = [("ᇂᄋ", "ᄋ"), ("ᆭᄋ", "ᄂ"), ("ᆶᄋ", "ᄅ")]

    for str1, str2 in pairs:
        out = out.replace(str1, str2)

    gloss(verbose, out, inp, rule)
    return out
