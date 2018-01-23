# -*- coding: utf-8 -*-
import re
from unidecode import unidecode

_VALIDCHAR    = re.compile(u'[A-Za-z0-9,\/()\?\.\ -]')
_VALIDCHAR_PL = re.compile(u'[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9,\/()\?\.\ -]')

def charfilter(s, allow_polish=False):
    validator = _VALIDCHAR_PL if allow_polish else _VALIDCHAR
    chars = []
    for c in s.replace('_', ' '):
        if not validator.match(c):
            c = unidecode(c)
            if not validator.match(c):
                continue
        chars.append(c)
    return u''.join(chars)


def cleanaddress(s, allow_polish=False):
    # replace backslashes with forward slashes (a common mistake in addresses)
    return charfilter(s.replace('\\', '/'), allow_polish=allow_polish)
