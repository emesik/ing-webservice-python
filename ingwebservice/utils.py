# -*- coding: utf-8 -*-
from unidecode import unidecode

def purepolish(s):
    chars = []
    for c in s:
        if c not in u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzĄĆĘŁŃÓŚŹŻąćęłńóśźż-\'':
            c = unidecode(c)
        chars.append(c)
    return u''.join(chars)
