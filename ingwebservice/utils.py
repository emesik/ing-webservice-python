# -*- coding: utf-8 -*-
import re
from unidecode import unidecode

_VALIDCHAR=re.compile(u'[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9,/()\?\.\ -]')

def purepolish(s):
    chars = []
    for c in s:
        if not _VALIDCHAR.match(c):
            c = unidecode(c)
        chars.append(c)
    return u''.join(chars)

def cleanaddress(s):
    # replace backslashes with forward slashes (a common mistake in addresses)
    return purepolish(s.replace('\\', '/'))
