# -*- coding: utf-8 -*-
import re
from unidecode import unidecode

def purepolish(s):
    chars = []
    for c in s:
        if c not in u'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyzĄĆĘŁŃÓŚŹŻąćęłńóśźż-\' ':
            c = unidecode(c)
        chars.append(c)
    return u''.join(chars)

def cleanaddress(s):
    return u''.join(
        re.findall(
            u'[A-Za-zĄĆĘŁŃÓŚŹŻąćęłńóśźż0-9,/\s]',
            purepolish(s.replace('\\', '/'))))
