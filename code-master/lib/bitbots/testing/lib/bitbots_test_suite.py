import unittest


class BitBotsTestSuite(unittest.TestSuite):

    def __init__(self, short_name, description=''):
        super(BitBotsTestSuite, self).__init__()

        self._short_name = short_name
        self._description = description

    @property
    def short_name(self):
        return self._short_name

    @property
    def description(self):
        return self._description