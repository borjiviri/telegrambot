# -*- coding: utf-8 -*-
# borja@libcrack.so
# jue jun 25 20:05:47 CEST 2015

import requests
#import logging
import daemon
import sched
import json
import time
import sys
import io
import os


from daemon import daemon
from daemon import runner

from spam import (
    initial_program_setup,
    do_main_program,
    program_cleanup,
    reload_program_config,
    )

from Logger import Logger
import command

logger = Logger.logger

class TelegramBot(daemon):
    '''
    Telegram Bot
    '''

    def __init__(self, token_path=None, name='telegrambot', botmasters=None, *argz, **kwz):
        self.name = name
        self.token_path = token_path
        self.botmasters = botmasters
        self.token = None
        try:
            f = open(self.token_path,'r')
            self.token = f.readline().strip()
        except IOError as e:
            logger.error('Cannot read token file {0}: ({1}) {2}'.
                    format(self.token_path, e.errno, e.strerror))
        else: f.close()
        self.apiurl = 'https://api.telegram.org/bot' + self.token
        self.last_update_id = 0
        self.last_update_id_file = os.path.abspath('last_update_id.{0}'.format(self.name))
        self.implemented_commands = ['/help', '/settings', '/start', '/magic']

        self.logfile = '{0}.log'.format(self.name)
        self.logfile_path = os.path.join(os.getcwd(),self.logfile)
        Logger.add_file_handler(self.logfile_path)
        Logger.set_verbose('debug')

        # any subclass of StreamHandler should provide the ‘stream’ attribute.
        # if using import logging
        # lh = logging.handlers.TimedRotatingFileHandler("/var/log/foo.log",)
        # or ...
        # logger = logging.getLogger("DaemonLog")
        # logger.setLevel(logging.INFO)
        # formatter = logging.Formatter(
        #     "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        # lh = logging.FileHandler("log.file")
        # logger.addHandler(handler)


        if not os.path.isfile(self.last_update_id_file):
            logger.error('Creating {0}'.format(self.last_update_id_file))
            self.write_update_last_id('0')

        ## daemon stuff

        important_file = open('spam.data', 'w')
        interesting_file = open('eggs.data', 'w')

        self.context = daemon.DaemonContext(
            working_directory='/var/lib/foo',
            umask=0o002,
            pidfile=lockfile.FileLock('/var/run/spam.pid'),
            #pidfile=daemon.pidlockfile.TimeoutPIDLockFile('/var/run/daemon.pid', 10)
            files_preserve = [
               important_file,
               interesting_file,
               lh.stream
               ],
           signal_map = {
                signal.SIGTERM: program_cleanup,
                signal.SIGHUP: 'terminate',
                signal.SIGUSR1: reload_program_config,
                }
            )
        initial_program_setup()

        # super(TelegramBot, self).__init__(*argz, **kwz)

    def _handle_command(self, message):
        '''
        Handler for commands sent to the bot in the form of "/command arg1 arg2 ..."
        '''
        photo = None
        files = None
        text = message['text']
        command = text.strip('/')
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        user_name = message['from']['first_name']
        logger.info('Received command from user {0}: {1}'.format(user_name,command))
        text_reply = 'Sorry {0}, I can\'t talk to people'.format(user_name)
        if self.botmasters is not None and user_name not in self.botmasters:
            text_reply = 'Sorry {0}, I can\'t obey you'.format(user_name)
        else:
            try:
                method_to_call = getattr(Command,command)
                result = method_to_call.execute()
                if isinstance(result, str):
                    text_reply = result
                elif isinstance(result, io.BufferedReader):
                    photo = result
                    text_reply = None
                elif result is None:
                    text_reply = 'Command "{0}" executed successfully'.format(command)
                else:
                    raise Command.ReturnError()
            except AttributeError:
                text_reply = 'Command "{0}" not implemented'.format(command)
                logger.error(text_reply)
            except Command.ReturnError as e:
                text_reply = 'Failed to execute command "{0}": {1}'.format(command,e.message)
                logger.error(text_reply)
        self.send_message(chat_id=chat_id, text=text_reply, photo=photo)

    def _read_last_update_id(self):
        '''
        Reads the last received update_id integer from the file pointed
        by self.last_update_id_file
        '''
        try:
            f = open(self.last_update_id_file, 'r')
            s = f.readline()
            self.last_update_id = int(s.strip())
        except IOError as e:
            logger.error('Cannot read last_update_id from {0}: ({1}) {2}'.
                    format(self.last_update_id_file,e.errno, e.strerror))
        except ValueError:
            logger.error('Could not convert last_id data to an integer.')
        except:
            logger.error('Unexpected error:', sys.exc_info()[0])
        else:
            f.close()
            logger.info('Obtained update_id from file {0}: {1}'.
                    format(self.last_update_id_file, self.last_update_id))

    def _request(self, url, data, files=None):
        '''
        Issue an HTTP request
        '''
        # headers = {'content-type': 'application/json'}
        try:
            # req = requests.post(url, data=data, headers=headers, timeout=5.0)
            req = requests.post(url=url, data=data, files=files)
            #if files is None:
            #    req = requests.post(url, data=data, headers=headers, timeout=5.0)
            #else:
            #if files is not None:
            #  # headers = {'content-type': 'multipart/form-data'}
            #  # req = requests.post(url, data=data, headers=headers, files=files, timeout=60.0)
            #  req = requests.post(url, data=data, files=files)
        except requests.ConnectionError:
            logger.error('Connection error')
        except requests.HTTPError:
            logger.error('Invalid HTTP response')
        except requests.Timeout:
            logger.error('Connection timeout')
        except requests.TooManyRedirects:
            logger.error('Too many redirects')
        else:
            logger.debug('Request URL: {0}'.format(url))
            logger.debug('Request data: {0}'.format(data))
        return req

    def run(self):
        '''
        Implements daemon
        '''
        sleep_time = 10
        priority = 1
        logger.info('Starting Telegram bot')
        logger.info('Using bot token %s' % self.token)
        logger.info('Forking to the background')
        Logger.remove_console_handler()
        self._read_last_update_id()

        # scheduler = sched.scheduler(time.time, time.sleep)
        # # scheduler.enter(sleep_time, priority, self.get_updates, kwargs={'a': 'keyword'})
        # scheduler.enter(sleep_time, priority, self.get_updates)
        # scheduler.run()
        # # scheduler.cancel(event)   # remove element from queue

        while True:
            self.get_updates()
            logger.info('Sleeping {0} secs'.format(sleep_time))
            time.sleep(sleep_time)

        with self.context:
            #self.start()
            do_main_program()

    def send_message(self, chat_id, text, files=None, photo=None):
        method = 'sendMessage'
        data = {'chat_id': chat_id, 'text': text}
        if photo is not None:
            method = 'sendPhoto'
            # data = {'chat_id': chat_id, 'photo': photo, 'caption': text}
            data = {'chat_id': chat_id, 'caption': text}
            files = {'photo': photo}
        url = self.apiurl + '/' + method
        req = self._request(url, data, files)
        logger.debug('Message sent to chat {0}'.format(chat_id))
        logger.debug('Message payload: {0}'.format(data))
        try:
            if req.status_code != 200:
                logger.error('Failed to send message to chat {0}'.format(chat_id))
                logger.debug('Error code: {0}'.format(req.status_code))
                logger.debug('Failed request: \n{0}'.format(req.text))
        except:
            logger.debug('Failed request: none returned')


    def write_update_last_id(self, last_update_id):
        self.last_update_id = last_update_id
        logger.info('Writting last_id {0} to file {1}'.
                format(last_update_id, self.last_update_id_file))
        try:
            f = open(self.last_update_id_file, 'w')
            f.write('{0}'.format(self.last_update_id))
        except IOError as e:
            logger.error('Cannot write last_id to file {0}: ({1}): {2}'.
                    format(self.last_update_id_file,e.errno, e.strerror))
        except:
            logger.error('Unexpected error:', sys.exc_info()[0])
        else:
            f.close()

    def get_updates(self):
        logger.info('Getting bot updates')
        method = 'getUpdates'
        data = {'offset': self.last_update_id + 1}
        url = self.apiurl + '/' + method
        req = self._request(url, data)
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
                    logger.debug('Replying to user {0}: {1}'.format(user_name,text_reply))

