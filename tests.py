# -*- coding: utf-8 -*-
import unittest
from ingwebservice.utils import purepolish, cleanaddress

class FilterTest(unittest.TestCase):
    def test_purepolish(self):
        self.assertEqual(purepolish(u'zażółć gęślą jaźń'), u'zażółć gęślą jaźń')
        self.assertEqual(purepolish(u'ZAŻÓŁĆ GĘŚLĄ JAŹŃ'), u'ZAŻÓŁĆ GĘŚLĄ JAŹŃ')
        self.assertEqual(
            purepolish(u'Mon aéroglisseur est plein d\'anguilles'),
            u'Mon aeroglisseur est plein d\'anguilles')
        self.assertEqual(
            purepolish(u'Det er fullt av ål i luftputebåten min'),
            u'Det er fullt av al i luftputebaten min')
        self.assertEqual(
            purepolish(u'Τὸ ἐμὸν αερόστρωμνον ἐγχελείων πλῆρές ἐστιν'),
            u'To emon aerostromnon egkheleion pleres estin')

    def test_cleanaddress(self):
        self.assertEqual(
            cleanaddress(u'Obrońców Stalingradu 6\\66, Pcim'),
            u'Obrońców Stalingradu 6/66, Pcim')
        self.assertEqual(
            cleanaddress(u'Großbrücke'),
            u'Grossbrucke')
