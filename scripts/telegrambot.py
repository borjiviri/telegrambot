#!/usr/bin/env python

import argparse
from telegrambot import TelegramBot

if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='Telegram bot',
        add_help=True
    )

    parser.add_argument('-c', '--config', action='store', dest='config',
                        required=True, type=str, help='configuration file')
    args = parser.parse_args()

    telegrambot = TelegramBot(config_path=args.config)
    telegrambot.run()
