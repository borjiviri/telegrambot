#!/usr/bin/env python

from telegrambot import TelegramBot

telegrambot = TelegramBot(config_path='./data/telegrambot.cfg')
telegrambot.run()

