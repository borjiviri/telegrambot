# -*- coding: utf-8 -*-
# borja@libcrack.so
# vie jun 26 01:50:53 CEST 2015

import os
import sys
import inspect


def botcommand(*args, **kwargs):
    """
    Class decorator for bot commands
    """
    def class_decorate(func, hidden=False, name=None, thread=False):
        def __getattribute__(self, attr_name):
            obj = super(BaseCommand, self).__getattribute__(attr_name)
            if hasattr(obj, '__call__') and attr_name in method_names:
                setattr(obj, '_telegrambot_command', True)
                setattr(obj, '_telegrambot_command_name', name or func.__name__)
                setattr(obj, '_telegrambot_command_hidden', hidden)
                setattr(obj, '_telegrambot_command_thread', thread)
            return obj
        return class_decorate

    if len(args):
        return decorate(args[0], **kwargs)
    else:
        return lambda func: decorate(func, **kwargs)


class ReturnError(Exception):

    """
    Exception throwed by the bot commands when failing to
    sucessfully perform actions
    """

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


@botcommand
class help(BaseCommand):
    description = 'Commands help'

    @staticmethod
    def execute(*kwc, **kwz):
        # Method 1:
        classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        command_list = [
            getattr(c, _telegrambot_command_name) for c in classes
                if getattr(c, _telegrambot_command)
                ]
        # ----------------------------------------------------------------
        # Method 2:
        # for name, value in inspect.getmembers(sys.modules[__name__], inspect.isclass):
        #     if getattr(value, '_telegrambot_command', False):
        #         command_list.append(getattr(value, _telegrambot_command_name))
        # ----------------------------------------------------------------
        # Method 3:
        # classes = inspect.getmembers(sys.modules[__name__], inspect.isclass)
        # command_list = [c for c in classes
        #                 if c[0] not in hidden
        #                 and not c[0].startswith('__')
        #                 and isinstance(c[1], type(BaseCommand))]
        # and isinstance(c[1], BaseCommand)]
        # ----------------------------------------------------------------
        text = 'Available commands:\n'
        for cmd in command_list:
            text += '- /{0}: {1}\n'.format(cmd[0], cmd[1].description)
        return text


@botcommand
class w0w0w0(BaseCommand):
    description = 'Dummy command'

    @staticmethod
    def execute():
        text = 'Command executed "w0w0w0"'
        return text


@botcommand
class magic(BaseCommand):
    description = 'Sends a magic picture'

    @staticmethod
    def execute(*kwc, **kwz):
        try:
            photo = open(os.path.abspath(
                'magic.gif'), 'rb')
        except IOError as e:
            return 'Cannot open picture: {0}'.format(e.message)
        else:
            return photo
        # with open(os.path.abspath(
        #    './data/magic.gif'),'rb') as photo:
        #    return photo
