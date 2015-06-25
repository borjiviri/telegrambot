# -*- coding: utf-8 -*-
# borja@libcrack.so
# jue jun 25 20:05:47 CEST 2015

import requests
import json
import time
import sys
import os

from Daemon import Daemon
from Logger import Logger

logger = Logger.logger

class TelegramBot(Daemon):

    def __init__(self, token_path=None, *argz, **kwz):
        self.token_path = token_path
        self.token = None
        try:
            f = open(self.token_path,'r')
            self.token = f.readline().strip()
        except IOError as e:
            logger.error('Cannot read token file {0}: ({1}) {2}'.format(self.token_path,e.errno, e.strerror))

        self.apiurl = 'https://api.telegram.org/bot' + self.token
        self.last_update_id = 0
        self.last_update_id_file = os.path.abspath('last_update_id')
        self.implemented_commands = ['/help', '/settings', '/start']
        self.botmasters = ['Borjiviri',]
        self.logfile = 'telegrambot.log'
        self.logfile_path = os.path.join(os.getcwd(),self.logfile)
        Logger.add_file_handler(self.logfile_path)
        Logger.set_verbose('info')
        super(TelegramBot, self).__init__(*argz, **kwz)

    def run(self):
        sleep_time = 10
        logger.info('Starting Telegram bot')
        logger.info('Using bot token %s' % self.token)
        logger.info('Forking to the background')
        Logger.remove_console_handler()
        self._read_last_update_id()
        while True:
            self.get_updates()
            logger.info('Sleeping {0} secs'.format(sleep_time))
            time.sleep(sleep_time)

    def _handle_command(self, message):
        text = message['text']
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        user_name = message['from']['first_name']
        text_reply = 'Sorry {0}, I can\'t talk to people'.format(user_name)
        logger.info('Received command from user {0}: {1}'.format(user_name,message['text']))
        if user_name not in self.botmasters:
            text_reply = 'Sorry {0}, I can\'t obey you'.format(user_name)
        else:
            if text not in self.implemented_commands:
                logger.error('Command not implemented: {0}'.format(message['text']))
                text_reply = 'Command not implemented - Fuck off {0}!'.format(user_name)
        self.send_message(chat_id, text_reply)
        logger.debug('Replying to user {0}: {1}'.format(user_id,text_reply))

    def _read_last_update_id(self):
        # with open(self.last_update_id_file, 'r') as f:
        #     s = f.readline()
        #     self.last_update_id = int(s.strip())
        #     f.close()
        #     logger.info('Read update_id from file {0}: {1}'.format(self.last_update_id_file,self.last_update_id))
        try:
            f = open(self.last_update_id_file, 'r')
            s = f.readline()
            self.last_update_id = int(s.strip())
        except IOError as e:
            logger.error('Cannot read last_update_id from {0}: ({1}) {2}'.format(self.last_update_id_file,e.errno, e.strerror))
        except ValueError:
            logger.error('Could not convert last_id data to an integer.')
        except:
            logger.error('Unexpected error:', sys.exc_info()[0])
        else:
            f.close()
            logger.info('Obtained update_id from file {0}: {1}'.format(self.last_update_id_file, self.last_update_id))

    def _request(self, url, params):
        headers = {'content-type': 'application/json'}
        try:
            req = requests.post(url, params=params, headers=headers, timeout=5.0)
        except requests.ConnectionError:
            logger.error('Connection error')
        except requests.HTTPError:
            logger.error('Invalid HTTP response')
        except requests.Timeout:
            logger.error('Connection timeout')
        except requests.TooManyRedirects:
            logger.error('Too many redirects')
        else:
            logger.debug('Request sent url:'.format(url))
            logger.debug('Request sent params: {0}'.format(params))
        return req

    def send_message(self, chat_id, text):
        method = 'sendMessage'
        params = {'chat_id': chat_id, 'text': text}
        url = self.apiurl + '/' + method
        req = self._request(url, params)
        logger.debug('Message sent to chat {0}'.format(chat_id))
        logger.debug('Message text: {0}'.format(text))
        if req.status_code != 200:
            logger.error('Failed to send message to chat {0}'.format(chat_id))
            logger.debug('Message text: {0}'.format(text))

    def write_update_last_id(self, last_update_id):
        self.last_update_id = last_update_id
        logger.info('Writting last_id {0} to file {1}'.format(last_update_id, self.last_update_id_file))
        try:
            f = open(self.last_update_id_file, 'w')
            f.write('{0}'.format(self.last_update_id))
        except IOError as e:
            logger.error('Cannot write last_id to file {0}: ({1}): {2}'.format(self.last_update_id_file,e.errno, e.strerror))
        except:
            logger.error('Unexpected error:', sys.exc_info()[0])
        else:
            f.close()

    def get_updates(self):
        logger.info('Getting bot updates')
        method = 'getUpdates'
        params = {'offset': self.last_update_id + 1}
        url = self.apiurl + '/' + method
        req = self._request(url, params)
        data = req.json()
        for result in data['result']:
            self.write_update_last_id(result['update_id'])
            if result['message']:
                text = result['message']['text']
                chat_id = result['message']['chat']['id']
                user_id = result['message']['from']['id']
                user_name = result['message']['from']['first_name']
                text_reply = 'Sorry {0}, I can\'t talk to people'.format(user_name)
                try:
                    chat_title = result['message']['chat']['title']
                except:
                    chat_title = 'null'
                logger.debug('Received message from user {0}: {1}'.format(user_name,text))
                if text.startswith('/'):
                    self._handle_command(result['message'])
                else:
                    self.send_message(chat_id, text_reply)
                    logger.debug('Replying to user {0}: {1}'.format(user_id,text_reply))

