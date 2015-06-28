# -*- coding: utf-8 -*-
# borja@libcrack.so
# vie jun 26 01:50:53 CEST 2015

import os
import sys
import inspect

hidden = ['BaseCommand', 'ReturnError']
__all__ = ['help', 'w0w0w0', 'magic']


class ReturnError(Exception):

    def __init__(self, message=None, *args):
        if message is None:
            self.message = 'Command.execute did not \
                    return None, str nor io.BufferedReader'
        else:
            self.message = message
        super(self.__class__.__name__,
              self).__init__(message, *args)


class BaseCommand(object):
    name = 'Unnamed command'
    description = 'No description'

    @staticmethod
    def execute(*kwc, **kwz):
        pass

    @staticmethod
    def help():
        return __class__.description


class help(BaseCommand):
    description = 'Commands help'

    @staticmethod
    def execute(*kwc, **kwz):
        classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        command_list = [c for c in classes
                        if c[0] not in hidden
                        and not c[0].startswith('__')
                        and isinstance(c[1], type(BaseCommand))]
        # and isinstance(c[1], BaseCommand)]
        text = 'Available commands:\n'
        for cmd in command_list:
            text += '- /{0}: {1}\n'.format(cmd[0], cmd[1].description)
        return text


class w0w0w0(BaseCommand):
    description = 'Dummy command'

    @staticmethod
    def execute():
        text = 'Command executed "w0w0w0"'
        return text


class magic(BaseCommand):
    description = 'Sends a magic picture'

    @staticmethod
    def execute(*kwc, **kwz):
        try:
            photo = open(os.path.abspath(
                './data/magic.gif'), 'rb')
        except IOError as e:
            return 'Cannot open picture: {0}'.format(e.message)
        else:
            return photo
        # with open(os.path.abspath(
        #    './data/magic.gif'),'rb') as photo:
        #    return photo
