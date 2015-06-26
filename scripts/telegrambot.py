#!/usr/bin/env python

from TelegramBot import TelegramBot

telegrambot = TelegramBot('./telegrambot.token',
        name='telegrambot', pidfile='/tmp/telegrambot.pid')
telegrambot.start()

