# -*- coding: utf-8 -*-
# borja@libcrack.so
# jue jun 25 20:05:47 CEST 2015

from code import InteractiveConsole
from imp import new_module
import os


class Console(InteractiveConsole):

    """
    Interactive Python interpreter console.
    """

    def __init__(self, names=None):
        names = names or {}
        names['console'] = self
        InteractiveConsole.__init__(self, names)
        self.superspace = new_module('superspace')

    def enter(self, source):
        source = self.preprocess(source)
        self.runcode(source)

    @staticmethod
    def preprocess(source):
        return source

    def test_interact(self,):
        return self.interact()

    def test_execute(self, script='cvss.py'):
        with open(
            os.path.realpath(script), 'r'
        ) as f:
            self.enter(
                ''.join(f.readlines()))
