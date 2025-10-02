<!--
SPDX-FileCopyrightText: Enno Hermann

SPDX-License-Identifier: Apache-2.0
-->

# Korean Speech Tools

[![PyPI - License](https://img.shields.io/pypi/l/ko-speech-tools)](https://github.com/eginhard/ko-speech-tools/blob/main/LICENSE)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/ko-speech-tools)
[![PyPI - Version](https://img.shields.io/pypi/v/ko-speech-tools)](https://pypi.org/project/ko-speech-tools)

This package contains a variety of tools for Korean speech and language
processing, including:
- Hangul romanization.
- Jamo conversion.
- Grapheme-to-phoneme conversion (G2P).

It is mostly a collection of previously existing libraries that are unmaintained
or include unnecessary dependencies that have been removed here. Refer to the
[Credits](#credits) section below for details.

## Installation

```bash
pip install ko-speech-tools
```

The core part of this package does not have any external dependencies. For G2P,
the [mecab-ko](https://github.com/NoUnique/pymecab-ko) package is required,
which can be installed with:

```bash
pip install ko-speech-tools[g2p]
```

## Usage

Romanization:

```python
>>> from ko_speech_tools import hangul_romanize

>>> hangul_romanize("물엿")
'mul-yeos'

```

Jamo conversion ([documentation](https://python-jamo.readthedocs.io/en/latest/)):

```python
>>> from ko_speech_tools.jamo import h2j, j2hcj, j2h

>>> h2j('한굴')
'한굴'

>>> j2hcj(h2j('한굴'))
'ㅎㅏㄴㄱㅜㄹ'

>>> j2h('ㅇ', 'ㅕ', 'ㅇ')
'영'

```

G2P:

```python
>>> from ko_speech_tools import G2p

>>> g2p = G2p()
>>> g2p("것입니다")
'거심니다'

```

## Credits

This package combines and adapts the following packages:

- `g2pkk`: https://github.com/harmlessman/g2pkk (Apache-2.0), a fork of https://github.com/Kyubyong/g2pK
- `hangul_romanize`: https://github.com/youknowone/hangul-romanize (BSD-2-Clause)
- `jamo`: https://github.com/jdongian/python-jamo (Apache-2.0)

It additionally uses code from https://github.com/keithito/tacotron (MIT) to
read [CMUdict data](https://github.com/cmusphinx/cmudict).

The respective code can be used under the original license, see the individual
files for details. Any new code is made available under Apache-2.0.
