# -*- coding: utf-8 -*-
import unittest
from ingwebservice.utils import charfilter, cleanaddress

class FilterTest(unittest.TestCase):
    def test_charfilter_pl(self):
        self.assertEqual(charfilter(u'zażółć gęślą jaźń', allow_polish=True), u'zażółć gęślą jaźń')
        self.assertEqual(charfilter(u'ZAŻÓŁĆ GĘŚLĄ JAŹŃ', allow_polish=True), u'ZAŻÓŁĆ GĘŚLĄ JAŹŃ')
        self.assertEqual(
            charfilter(u'Mon aéroglisseur est plein d\'anguilles', allow_polish=True),
            u'Mon aeroglisseur est plein danguilles')
        self.assertEqual(
            charfilter(u'Det er fullt av ål i luftputebåten min', allow_polish=True),
            u'Det er fullt av al i luftputebaten min')
        self.assertEqual(
            charfilter(u'Τὸ ἐμὸν αερόστρωμνον ἐγχελείων πλῆρές ἐστιν', allow_polish=True),
            u'To emon aerostromnon egkheleion pleres estin')
        self.assertEqual(
            charfilter(u'Copywriting (Computer Protection_Mac_Windows | Quality)', allow_polish=True),
            u'Copywriting (Computer Protection Mac Windows  Quality)')

    def test_charfilter(self):
        self.assertEqual(charfilter(u'zażółć gęślą jaźń'), u'zazolc gesla jazn')
        self.assertEqual(charfilter(u'ZAŻÓŁĆ GĘŚLĄ JAŹŃ'), u'ZAZOLC GESLA JAZN')
        self.assertEqual(
            charfilter(u'Mon aéroglisseur est plein d\'anguilles'),
            u'Mon aeroglisseur est plein danguilles')
        self.assertEqual(
            charfilter(u'Det er fullt av ål i luftputebåten min'),
            u'Det er fullt av al i luftputebaten min')
        self.assertEqual(
            charfilter(u'Τὸ ἐμὸν αερόστρωμνον ἐγχελείων πλῆρές ἐστιν'),
            u'To emon aerostromnon egkheleion pleres estin')
        self.assertEqual(
            charfilter(u'Copywriting (Computer Protection_Mac_Windows | Quality)'),
            u'Copywriting (Computer Protection Mac Windows  Quality)')

    def test_cleanaddress_pl(self):
        self.assertEqual(
            cleanaddress(u'Obrońców Stalingradu 6\\66, (00-666) Pcim.', allow_polish=True),
            u'Obrońców Stalingradu 6/66, (00-666) Pcim.')
        self.assertEqual(
            cleanaddress(u'Großbrücke', allow_polish=True),
            u'Grossbrucke')

    def test_cleanaddress(self):
        self.assertEqual(
            cleanaddress(u'Obrońców Stalingradu 6\\66, (00-666) Pcim.'),
            u'Obroncow Stalingradu 6/66, (00-666) Pcim.')
        self.assertEqual(
            cleanaddress(u'Großbrücke'),
            u'Grossbrucke')
