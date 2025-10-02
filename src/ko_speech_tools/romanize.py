# SPDX-FileCopyrightText: 2015 Jeong YunWon <jeong+hangul-romanize@youknowone.org>
#
# SPDX-License-Identifier: BSD-2-Clause

"""Hangul romanization tool.

Source:
https://github.com/youknowone/hangul-romanize"""

REVISED_INITIALS = 'g', 'kk', 'n', 'd', 'tt', 'l', 'm', 'b', 'pp', 's', 'ss', '', 'j', 'jj', 'ch', 'k', 't', 'p', 'h'
REVISED_VOWELS = 'a', 'ae', 'ya', 'yae', 'eo', 'e', 'yeo', 'ye', 'o', 'wa', 'wae', 'oe', 'yo', 'u', 'wo', 'we', 'wi', 'yu', 'eu', 'ui', 'i'
REVISED_FINALS = '', 'g', 'kk', 'gs', 'n', 'nj', 'nh', 'd', 'l', 'lg', 'lm', 'lb', 'ls', 'lt', 'lp', 'lh', 'm', 'b', 'bs', 's', 'ss', 'ng', 'j', 'ch', 'k', 't', 'p', 'h'


def academic_ambiguous_patterns():
    import itertools
    result = set()
    for final, initial in itertools.product(REVISED_FINALS, REVISED_INITIALS):
        check = False
        combined = final + initial
        for i in range(len(combined)):
            head, tail = combined[:i], combined[i:]
            if head in REVISED_FINALS and tail in REVISED_INITIALS:
                if not check:
                    check = True
                else:
                    result.add(combined)
                    break
    return result


ACADEMIC_AMBIGUOUS_PATTERNS = academic_ambiguous_patterns()


def academic(now, pre, **options):
    """Rule for academic translition."""
    c, s = now
    if not s:
        return c

    ps = pre[1] if pre else None

    marker = False
    if ps:
        if s.initial == 11:
            marker = True
        elif ps and (REVISED_FINALS[ps.final] + REVISED_INITIALS[s.initial]) in ACADEMIC_AMBIGUOUS_PATTERNS:
            marker = True

    r = u''
    if marker:
        r += '-'
    r += REVISED_INITIALS[s.initial] + REVISED_VOWELS[s.vowel] + REVISED_FINALS[s.final]
    return r

try:
    unicode(0)
except NameError:
    # py3
    unicode = str
    unichr = chr


class Syllable(object):
    """Hangul syllable interface"""

    MIN = ord(u'가')
    MAX = ord(u'힣')

    def __init__(self, char=None, code=None):
        if char is None and code is None:
            raise TypeError('__init__ takes char or code as a keyword argument (not given)')
        if char is not None and code is not None:
            raise TypeError('__init__ takes char or code as a keyword argument (both given)')
        if char:
            code = ord(char)
        if not self.MIN <= code <= self.MAX:
            raise TypeError('__init__ expected Hangul syllable but {0} not in [{1}..{2}]'.format(code, self.MIN, self.MAX))
        self.code = code

    @property
    def index(self):
        return self.code - self.MIN

    @property
    def initial(self):
        return self.index // 588

    @property
    def vowel(self):
        return (self.index // 28) % 21

    @property
    def final(self):
        return self.index % 28

    @property
    def char(self):
        return unichr(self.code)

    def __unicode__(self):
        return self.char

    def __repr__(self):
        return u'''<Syllable({}({}),{}({}),{}({}),{}({}))>'''.format(
            self.code, self.char, self.initial, u'', self.vowel, u'', self.final, u'')


class Transliter(object):
    """General transliting interface"""

    def __init__(self, rule):
        self.rule = rule

    def translit(self, text):
        """Translit text to romanized text

        :param text: Unicode string or unicode character iterator
        """
        result = []
        pre = None, None
        now = None, None
        for c in text:
            try:
                post = c, Syllable(c)
            except TypeError:
                post = c, None

            if now[0] is not None:
                out = self.rule(now, pre=pre, post=post)
                if out is not None:
                    result.append(out)

            pre = now
            now = post

        if now is not None:
            out = self.rule(now, pre=pre, post=(None, None))
            if out is not None:
                result.append(out)

        return u''.join(result)
