# SPDX-FileCopyrightText: 2019 Kyubyong Park <kbpark.linguist@gmail.com>
# SPDX-FileContributor: 2022 harmlessman <harmlessman17@gmail.com>
# SPDX-FileContributor: 2025 Enno Hermann
#
# SPDX-License-Identifier: Apache-2.0

"""Adapted from: https://github.com/harmlessman/g2pkk."""

import re
from importlib.resources import files
from typing import Any

from ko_speech_tools.jamo import h2j, j2h

_DATA_PATH = files("ko_speech_tools.data.g2p")

# Precompiled regex patterns
_DIGIT_RE = re.compile(r"\d")
_VOWEL_PLACEHOLDER_RE = re.compile("(^|[^\u1100-\u1112])([\u1161-\u1175])")
_CVC_RE = re.compile("[\u1100-\u1112][\u1161-\u1175][\u11a8-\u11c2]")
_CV_RE = re.compile("[\u1100-\u1112][\u1161-\u1175]")
_EXAMPLE_RE = re.compile(r"([ㄱ-힣][ ㄱ-힣]*)\[([ㄱ-힣][ ㄱ-힣]*)]")
_ANNOTATION_TAG_RE = re.compile("/[EJPB]")

# fmt: off
_ARPABET_TO_CHOSEONG = {
    "B": "ᄇ", "CH": "ᄎ", "D": "ᄃ", "DH": "ᄃ", "DZ": "ᄌ", "F": "ᄑ",
    "G": "ᄀ", "HH": "ᄒ", "JH": "ᄌ", "K": "ᄏ", "L": "ᄅ", "M": "ᄆ",
    "N": "ᄂ", "NG": "ᄋ", "P": "ᄑ", "R": "ᄅ", "S": "ᄉ", "SH": "ᄉ",
    "T": "ᄐ", "TH": "ᄉ", "TS": "ᄎ", "V": "ᄇ", "W": "W", "Y": "Y",
    "Z": "ᄌ", "ZH": "ᄌ",
}

_ARPABET_TO_JUNGSEONG = {
    "AA": "ᅡ", "AE": "ᅢ", "AH": "ᅥ", "AO": "ᅩ", "AW": "ᅡ우", "AWER": "ᅡ워",
    "AY": "ᅡ이", "EH": "ᅦ", "ER": "ᅥ", "EY": "ᅦ이", "IH": "ᅵ", "IY": "ᅵ",
    "OW": "ᅩ", "OY": "ᅩ이", "UH": "ᅮ", "UW": "ᅮ",
}

_ARPABET_TO_JONGSEONG = {
    "B": "ᆸ", "CH": "ᆾ", "D": "ᆮ", "DH": "ᆮ", "F": "ᇁ", "G": "ᆨ",
    "HH": "ᇂ", "JH": "ᆽ", "K": "ᆨ", "L": "ᆯ", "M": "ᆷ", "N": "ᆫ",
    "NG": "ᆼ", "P": "ᆸ", "R": "ᆯ", "S": "ᆺ", "SH": "ᆺ", "T": "ᆺ",
    "TH": "ᆺ", "V": "ᆸ", "W": "ᆼ", "Y": "ᆼ", "Z": "ᆽ", "ZH": "ᆽ",
}

_RECONSTRUCT_PAIRS = [
    ("그W", "ᄀW"), ("흐W", "ᄒW"), ("크W", "ᄏW"), ("ᄂYᅥ", "니어"), ("ᄃYᅥ", "디어"),
    ("ᄅYᅥ", "리어"), ("Yᅵ", "ᅵ"), ("Yᅡ", "ᅣ"), ("Yᅢ", "ᅤ"), ("Yᅥ", "ᅧ"),
    ("Yᅦ", "ᅨ"), ("Yᅩ", "ᅭ"), ("Yᅮ", "ᅲ"), ("Wᅡ", "ᅪ"), ("Wᅢ", "ᅫ"),
    ("Wᅥ", "ᅯ"), ("Wᅩ", "ᅯ"), ("Wᅮ", "ᅮ"), ("Wᅦ", "ᅰ"), ("Wᅵ", "ᅱ"),
    ("ᅳᅵ", "ᅴ"), ("Y", "ᅵ"), ("W", "ᅮ"),
]
# fmt: on


############## English ##############
def adjust(arpabets: list[str]) -> list[str]:
    """Adjust ARPAbet sequences for Korean G2P processing.

    Applies transformations like T+S→TS, D+Z→DZ, AW+ER→AWER, and adjusts
    word-final IR/ER sequences for better Korean transliteration.

    Args:
        arpabets: List of ARPAbet phoneme symbols.

    Returns:
        Modified list of ARPAbet symbols.
    """
    string = " " + " ".join(arpabets) + " $"
    string = _DIGIT_RE.sub("", string)
    string = string.replace(" T S ", " TS ")
    string = string.replace(" D Z ", " DZ ")
    string = string.replace(" AW ER ", " AWER ")
    string = string.replace(" IH R $", " IH ER ")
    string = string.replace(" EH R $", " EH ER ")
    string = string.replace(" $", "")

    return string.strip("$ ").split()


def to_choseong(arpabet: str) -> str:
    """Arpabet to choseong or onset."""
    return _ARPABET_TO_CHOSEONG.get(arpabet, arpabet)


def to_jungseong(arpabet: str) -> str:
    """Convert ARPAbet vowel to jungseong (medial vowel) jamo.

    Args:
        arpabet: ARPAbet vowel symbol (e.g., "AA", "IY", "UW").

    Returns:
        Corresponding jungseong jamo or original symbol if no mapping exists.
    """
    d = {
        "AA": "ᅡ",
        "AE": "ᅢ",
        "AH": "ᅥ",
        "AO": "ᅩ",
        "AW": "ᅡ우",
        "AWER": "ᅡ워",
        "AY": "ᅡ이",
        "EH": "ᅦ",
        "ER": "ᅥ",
        "EY": "ᅦ이",
        "IH": "ᅵ",
        "IY": "ᅵ",
        "OW": "ᅩ",
        "OY": "ᅩ이",
        "UH": "ᅮ",
        "UW": "ᅮ",
    }
    return d.get(arpabet, arpabet)


def to_jongseong(arpabet: str) -> str:
    """Arpabet to jongseong or coda."""
    return _ARPABET_TO_JONGSEONG.get(arpabet, arpabet)


def reconstruct(string: str) -> str:
    """Apply postprocessing to normalize jamo sequences.

    Handles W/Y glide combinations (e.g., Wᅡ→ᅪ, Yᅡ→ᅣ) and normalizes
    special sequences from English-to-Korean conversion.

    Args:
        string: Input string with jamo characters.

    Returns:
        String with postprocessing transformations applied.
    """
    pairs = [
        ("그W", "ᄀW"),
        ("흐W", "ᄒW"),
        ("크W", "ᄏW"),
        ("ᄂYᅥ", "니어"),
        ("ᄃYᅥ", "디어"),
        ("ᄅYᅥ", "리어"),
        ("Yᅵ", "ᅵ"),
        ("Yᅡ", "ᅣ"),
        ("Yᅢ", "ᅤ"),
        ("Yᅥ", "ᅧ"),
        ("Yᅦ", "ᅨ"),
        ("Yᅩ", "ᅭ"),
        ("Yᅮ", "ᅲ"),
        ("Wᅡ", "ᅪ"),
        ("Wᅢ", "ᅫ"),
        ("Wᅥ", "ᅯ"),
        ("Wᅩ", "ᅯ"),
        ("Wᅮ", "ᅮ"),
        ("Wᅦ", "ᅰ"),
        ("Wᅵ", "ᅱ"),
        ("ᅳᅵ", "ᅴ"),
        ("Y", "ᅵ"),
        ("W", "ᅮ"),
    ]
    for str1, str2 in pairs:
        string = string.replace(str1, str2)
    return string


############## Hangul ##############
def parse_table() -> list[tuple[str, str, list[str]]]:
    """Parse the main rule table."""
    with _DATA_PATH.joinpath("table.csv").open(encoding="utf-8") as f:
        lines = f.read().splitlines()
        onsets = lines[0].split(",")
        table = []
        for line in lines[1:]:
            cols = line.split(",")
            coda = cols[0]
            for i, onset in enumerate(onsets):
                cell = cols[i]
                if len(cell) == 0:
                    continue
                if i == 0:
                    continue
                str1 = f"{coda}{onset}"
                if "(" in cell:
                    str2 = cell.split("(")[0]
                    rule_ids = cell.split("(")[1][:-1].split("/")
                else:
                    str2 = cell
                    rule_ids = []

                table.append((str1, str2, rule_ids))

    return table


############## Preprocessing ##############
def annotate(string: str, mecab: Any) -> str:  # noqa: ANN401
    """Add morphological annotations to guide phonological rules.

    Uses MeCab to identify parts of speech and adds tags:
    - /J: josa (particle)
    - /E: ending (verbal/adjectival ending)
    - /P: predicate (verb/adjective stem)
    - /B: bound noun

    Args:
        string: Input Korean text.
        mecab: MeCab Tagger instance.

    Returns:
        String with annotation tags inserted.
    """
    parsed = mecab.parse(string)
    tokens = []
    for line in parsed.split("\n"):
        if line == "EOS":
            break
        parts = line.split("\t")
        tokens.append((parts[0], parts[1].split(",")[0]))
    if string.replace(" ", "") != "".join(token for token, _ in tokens):
        return string
    blanks = [i for i, char in enumerate(string) if char == " "]

    tag_parts = []
    for token, tag in tokens:
        tag = tag.split("+")[-1]
        tag = "B" if tag == "NNBC" else tag[0]  # bound noun
        tag_parts.append("_" * (len(token) - 1) + tag)
    tag_seq = "".join(tag_parts)

    for i in blanks:
        tag_seq = tag_seq[:i] + " " + tag_seq[i:]

    annotated_parts = []
    for char, tag in zip(string, tag_seq, strict=True):
        annotated_parts.append(char)
        if char == "의" and tag == "J":
            annotated_parts.append("/J")
        elif tag == "E":
            if h2j(char)[-1] in "ᆯ":
                annotated_parts.append("/E")
        elif tag == "V":
            if h2j(char)[-1] in "ᆫᆬᆷᆱᆰᆲᆴ":
                annotated_parts.append("/P")
        elif tag == "B":  # bound noun
            annotated_parts.append("/B")

    return "".join(annotated_parts)


############## Postprocessing ##############
def compose(letters: str) -> str:
    """Compose jamo characters into Hangul syllables.

    Inserts ᄋ placeholder for vowel-initial syllables and combines
    choseong (lead), jungseong (vowel), and jongseong (tail) into syllables.

    Args:
        letters: String containing jamo characters.

    Returns:
        String with jamo composed into complete Hangul syllables.
    """
    # insert placeholder
    letters = _VOWEL_PLACEHOLDER_RE.sub(r"\1ᄋ\2", letters)

    string = letters  # assembled characters
    # c+v+c
    syls = set(_CVC_RE.findall(string))
    for syl in syls:
        string = string.replace(syl, j2h(*syl))

    # c+v
    syls = set(_CV_RE.findall(string))
    for syl in syls:
        string = string.replace(syl, j2h(*syl))

    return string


def group(inp: str) -> str:
    """For group_vowels=True.

    Contemporarily, Korean speakers don't distinguish some vowels.
    """
    inp = inp.replace("ᅢ", "ᅦ")
    inp = inp.replace("ᅤ", "ᅨ")
    inp = inp.replace("ᅫ", "ᅬ")
    return inp.replace("ᅰ", "ᅬ")


def _get_examples() -> list[tuple[str, str]]:
    """For internal use."""
    examples = []
    with _DATA_PATH.joinpath("rules.txt").open(encoding="utf-8") as text:
        for line in text:
            if line.startswith("->"):
                examples.extend(_EXAMPLE_RE.findall(line))
    _examples = []
    for inp, gt in examples:
        _examples.extend((inp, each) for each in gt.split("/"))

    return _examples


############## Utilities ##############
def get_rule_id2text() -> dict[str, str]:
    """For verbose=True."""
    with _DATA_PATH.joinpath("rules.txt").open(encoding="utf-8") as f:
        rules = f.read().strip().split("\n\n")
        rule_id2text = {}
        for rule in rules:
            rule_id, texts = rule.splitlines()[0], rule.splitlines()[1:]
            rule_id2text[rule_id.strip()] = "\n".join(texts)
    return rule_id2text


def gloss(verbose: bool, out: str, inp: str, rule: str) -> None:  # noqa: FBT001
    """Display the process and relevant information."""
    if verbose and out != inp and out != _ANNOTATION_TAG_RE.sub("", inp):
        print(compose(inp), "->", compose(out))  # noqa: T201
        print("\033[1;31m", rule, "\033[0m")  # noqa: T201
