#-*- coding:utf-8 -*-
"""
    @Robert 29.04.2014: Currently disabled; Locator is not build regulary
    @Timon 2015-09-2015:
        Ohne den Import vom locator schlagen die Tests hier fehl.
        Daher habe ich eine import exception und etwas magie gebaut.
"""

import unittest
importerror = False
try:
    from bitbots.locator.locator import Matcher, Locator, Transformer
except ImportError:
    importerror = True


def load_tests(loader, tests, pattern):
    suite = unittest.TestSuite()
    if importerror:
        tests = loader.loadTestsFromTestCase(SkipTest)
    else:
        tests = unittest.loader.loadTestsFromTestCase(TestLineMatcher)
    suite.addTests(tests)
    return suite


class SkipTest(unittest.TestCase):
    @unittest.skip("Import from bitbots.locator.locator failed, thus it wont be tested")
    def test_nothing(self):
        pass


class TestLineMatcher(unittest.TestCase):
#class TestLineMatcher(object):

    @classmethod
    def setUpClass(cls):
        print "#### Test LineMatcher ####"

    def setUp(self):
        self.matcher = Matcher()

    def test_get_positions_with_field(self):
        fieldmodel = Locator(Transformer()).get_field_model()
        l = fieldmodel[0]
        c = fieldmodel[1]
        p = fieldmodel[2]
        self.matcher.update(l, c, p)
        positions = self.matcher.get_suggested_positions()
        self.assertTrue(0 < len(positions))
        ((x1, y1), (x2, y2), (x3, y3)) = ((0, 0), (0, 0), (0, 0))
        for idx in range(len(positions)):
            ((x11, y11), (x12, y12), (x13, y13)) = positions[idx]
            if y13 > y3:
                ((x1, y1), (x2, y2), (x3, y3)) = ((x11,
                                                   y11), (x12, y12), (x13, y13))

        self.assertEquals(0, x1)
        self.assertEquals(0, x2)
        self.assertEquals(0, x3)
        self.assertEquals(0, y1)
        self.assertEquals(0, y2)

    def test_get_position_goaly_position(self):
        l = [((0.6, -1.1), (0.6, 1.1), (0, 2.2)), ((0, 1.1), (0.6,
                                                              1.1), (0.6, 0)), ((0, -1.1), (0.6, -1.1), (0.6, 0))]
        # strafraumlinie
        c = []
        p = []
        self.matcher.update(l, c, p)
        positions = self.matcher.get_suggested_positions()
        self.assertTrue(0 < len(positions))
        ((x1, y1), (x2, y2), (x3, y3)) = ((0, 0), (0, 0), (0, 0))
        for idx in range(len(positions)):
            ((x11, y11), (x12, y12), (x13, y13)) = positions[idx]
            if y13 > y3:
                ((x1, y1), (x2, y2), (x3, y3)) = ((x11,
                                                   y11), (x12, y12), (x13, y13))

        self.assertEquals(3, abs(x1))
        self.assertEquals(0, x2)
        self.assertEquals(0, x3)
        self.assertEquals(3, abs(y1))
        self.assertEquals(0, y2)
