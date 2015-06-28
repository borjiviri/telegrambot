#!/usr/bin/env python

from TelegramBot import TelegramBot

telegrambot = TelegramBot(
            name = 'telegrambot',
            pidfile = './data/telegrambot.pid',
            logfile = './data/telegrambot.log',
            updatefile = './data/last_update_id.telegrambot',
            token_path = './data/telegrambot.token',
            )
telegrambot.run()

