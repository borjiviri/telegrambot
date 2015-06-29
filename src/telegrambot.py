# -*- coding: utf-8 -*-
# borja@libcrack.so
# jue jun 25 20:05:47 CEST 2015

import requests
import logging
import signal
import time
import json
import sys
import os
import io
import re

from twisted.internet import reactor
from twisted.internet import task

from daemon import daemon
from daemon import pidfile

from . import console
from . import command
from . logger import Logger

logger = Logger.logger


class TelegramBot(daemon.DaemonContext):

    """
    Telegram Bot
    """

    def __init__(self, config_path=None):
        """
        TelegramBot class constructor

        Args:
            config_path (str): configuration file path (mandatory)
            debug (bool): value to enable debug options
        Raises:
            ValueError: if config_path is not especified
        """
        if config_path is None:
            raise ValueError('required config_path={0}'.format(config_path))

        Logger.set_verbose('debug')

        self.token = ''
        self.username = ''
        self.first_name = ''
        self.pidfile = ''
        self.loglevel = ''
        self.logfile = ''
        self.botmasters = []
        self.apiurl = ''
        self.working_directory = ''
        self.sleep_time = -1
        self.update_id = -1
        self.config = {}
        self.config_path = config_path

        # reads and sets all the above object attributes
        self._read_config()

        logger.info('Starting Telegram bot (token={0})'.format(self.token))

        # get self.username & self.first_name performing a getMe API call
        self.get_me()

        # twisted task object
        self.task = task.LoopingCall(self.get_updates)

        # python-daemon context
        self.context = daemon.DaemonContext(
            working_directory=self.working_directory,
            umask=0o002,
            pidfile=pidfile.PIDLockFile(self.pidfile),
            #files_preserve=[h.stream for h in logger.handlers],
            files_preserve=[h.stream for h in Logger.logger.handlers],
            signal_map={
                signal.SIGTERM: self.program_cleanup,
                signal.SIGHUP: 'terminate',
                signal.SIGUSR1: self.reload_program_config,
            },
        )

    def _handle_command(self, message):
        """
        Handler for commands sent to the bot in the form of "/command arg1 ..."

        Args:
            message (dict): the received JSON message command
        Raises:
            AttributeError: if the message text is not an implemented command
            command.ReturnError: if the command execution failed
        """
        photo = None
        files = None
        text = message['text']
        cmd = text.strip('/')
        if cmd.find('@{0}'.format(self.username)) > 0:
            logger.info('Detected directed command to myself')
            cmd = cmd.split('@')[0]
        chat_id = message['chat']['id']
        user_id = message['from']['id']
        user_name = message['from']['first_name']
        logger.info(
            'Received command from user {0}: {1}'.format(
                user_name,
                cmd))
        text_reply = 'Sorry {0}, I can\'t talk to people'.format(user_name)
        if self.botmasters and user_name not in self.botmasters:
            text_reply = 'Sorry {0}, I can\'t obey you. '.format(user_name)
            text_reply += 'My botmasters are: '.format(
                ', '.join(
                    self.botmasters))
        else:
            try:
                method_to_call = getattr(command, cmd)
                result = method_to_call.execute()
                if isinstance(result, str):
                    text_reply = result
                elif isinstance(result, io.BufferedReader):
                    photo = result
                    text_reply = None
                elif result is None:
                    text_reply = 'Command "{0}" executed successfully'.format(
                        cmd)
                else:
                    raise Command.ReturnError()
            except AttributeError:
                text_reply = 'Command "{0}" not implemented'.format(cmd)
                logger.error(text_reply)
            except Command.ReturnError as e:
                text_reply = 'Failed to execute command "{0}": {1}'.format(
                    cmd,
                    e.message)
                logger.error(text_reply)
        self.send_message(
            chat_id=chat_id,
            text=text_reply,
            files=files,
            photo=photo)

    def _read_config(self):
        """
        Reads and sets the bot's configuration options from self.config_path.

        Raises:
            IOError: if self.config_path does not exists
            ValueError: if self.config_path does not include all mandatory opt
        """
        mandatory_options = [
            'token',
            'logfile',
            'pidfile',
            'sleep_time',
        ]
        avoid = ['no', 'none', 'false', 'null']

        logger.info('Reading config file: {0}'.format(self.config_path))
        try:
            config = open(self.config_path, 'r')
        except IOError as e:
            logger.error(
                'Error opening file {0} : ({1})' %
                (self.config_path, e))
            raise (e)

        pattern = re.compile('^(\S+?)\s*=\s*(.+)\s*$')

        for line in config:
            if not line.startswith('#'):
                result = pattern.match(line)
                if result is not None:
                    (key, value) = result.groups()
                    self.config[key] = value
                    logger.debug('Config option {0}={1}'.format(key, value))
        config.close()

        for item in mandatory_options:
            if item not in self.config.keys():
                logger.error('Missing mandatory config option "{0}" in {1}'.
                             format(item, self.config_path))
                raise ValueError

        if 'loglevel' not in self.config.keys():
            logger.info(
                'loglevel not declared in {0}'.format(
                    self.config_path))
            logger.info('using loglevel = info')
            self.config['loglevel'] = 'info'

        if 'working_directory' not in self.config.keys():
            logger.info(
                'working_directory not declared in {0}'.format(
                    self.config_path))
            logger.info('using working_directory = {0}'.format(os.getcwd()))
            self.config['working_directory'] = os.getcwd()
        elif self.config['working_directory'] in avoid:
            logger.info('using working_directory = {0}'.format(os.getcwd()))
            self.config['working_directory'] = os.getcwd()

        if 'update_id' not in self.config.keys():
            logger.info(
                'update_id not declared in {0}'.format(
                    self.config_path))
            logger.info('using update_id = 0')
            self.config['update_id'] = 0

        if 'botmasters' not in self.config.keys():
            logger.info(
                'botmasters not declared in {0}'.format(
                    self.config_path))
            logger.info('using NO (botmasters = )')
            self.config['botmasters'] = None
            self.botmasters = None
        elif self.config['botmasters'] in avoid:
            logger.info(
                'using NO (botmasters = {0})'.format(
                    self.config['botmasters']))
            self.config['botmasters'] = None
            self.botmasters = None
        else:
            self.botmasters = self.config['botmasters'].split(',')

        self.token = self.config['token']
        self.pidfile = self.config['pidfile']
        self.sleep_time = float(self.config['sleep_time'])
        self.update_id = int(self.config['update_id'])
        self.working_directory = self.config['working_directory']
        self.apiurl = 'https://api.telegram.org/bot' + self.config['token']
        self.loglevel = self.config['loglevel']
        # configured_logfiles = [h.baseFilename for h in logger.handlers
        #         if not isinstance (h,logging.StreamHandler)]
        if self.logfile == '':
            self.logfile = self.config['logfile']
            Logger.add_file_handler(self.logfile)
        elif self.logfile != self.config['logfile']:
            logger.info(
                'Configuring new logfile {0}'.format(
                    self.config['logfile']))
            Logger.remove_file_handler(self.logfile)
            Logger.add_file_handler(self.config['logfile'])
            self.logfile = self.config['logfile']
        else:
            logger.error('Logfile {0} already configured'.format(self.logfile))
        Logger.set_verbose(self.loglevel)

    def _write_update_id(self, update_id):
        """
        Updates the update_id configuration file entry (self.config_path)
        also updates self.config['update_id'] and self.update_id

        Args:
            update_id (int): Telegram last received message id
        """
        logger.info('Writting update_id {0} to file {1}'.
                    format(update_id, self.config_path))
        try:
            f = open(self.config_path, 'r+')
            content = f.read()
            replaced = re.sub(r'update_id\s*=\s*\d+',
                              'update_id = {0}'.format(update_id), content)
            f.seek(0)
            f.write(replaced)
        except IOError as e:
            logger.error('Cannot write update_id to file {0}: ({1}): {2}'.
                         format(self.config_path, e.errno, e.strerror))
        except:
            logger.error('Unexpected error:', sys.exc_info()[0])
        else:
            self.update_id = update_id
            self.config['update_id'] = update_id
            f.close()

    def _request(self, url, data, files=None):
        """
        Issue an HTTP request against the Telegram API JSON endpoint.

        Args:
            url (str): Telegram bot endpoint URL (with token)
            data (dict): JSON data object
            files (dict): JSON files object
        Returns:
            the resulted JSON object
        """
        try:
            req = requests.post(url=url, data=data, files=files)
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
            logger.debug('response: \n{0}'.format(req.text))
        try:
            if req.status_code != 200:
                logger.error('Failed to perfom request to {0}'.format(url))
                logger.debug('Error code: {0}'.format(req.status_code))
                logger.debug('Failed request: \n{0}'.format(req.text))
        except:
            logger.debug('Failed request: none returned')
        else:
            return req.json()

    # START DAEMON IMPLEMENTATION ============================================

    def do_main_program(self):
        """
        Implements daemon's main loop using a twisted task object
        """
        self.task.start(self.sleep_time)
        reactor.run()

    def run(self):
        logger.info('Forking to the backgroud')
        Logger.remove_console_handler()
        with self.context:
            self.do_main_program()

    def program_cleanup(self, signum, frame):
        """
        Exists gracefully when a signal SIGTERM is received.

        Args:
            signum (int): signal number
            frame: signal frame
        """
        logger.info('daemon cleanup: received signum={0}'.format(signum))
        self.task.stop()
        self.context.terminate(signum, frame)

    def reload_program_config(self, signum, frame):
        """
        Reloads the configuration when a signal SIGUSR1 is received.

        Args:
            signum (int): signal number
            frame: signal frame
        """
        logger.info('daemon config reload: received signum={0}'.format(signum))
        self._read_config()

    # END DAEMON IMPLEMENTATION ==============================================

    # START TELEGRAM API IMPLEMENTATION ======================================

    def send_message(self, chat_id, text, files=None, photo=None):
        method = 'sendMessage'
        data = {'chat_id': chat_id, 'text': text}
        if photo is not None:
            method = 'sendPhoto'
            data = {'chat_id': chat_id, 'caption': text}
            files = {'photo': photo}
        url = self.apiurl + '/' + method
        json_data = self._request(url, data, files)
        logger.debug('Message sent to chat {0}'.format(chat_id))
        logger.debug('Message payload: {0}'.format(data))

    def send_picture(self, chat_id, text, photo=None):
        method = 'sendPhoto'
        data = {'chat_id': chat_id, 'caption': text}
        files = {'photo': photo}
        url = self.apiurl + '/' + method
        json_data = self._request(url, data, files)
        logger.debug('Picture sent to chat {0}'.format(chat_id))
        logger.debug('Picture data: {0}'.format(data))

    def get_me(self):
        """
        Implements getMe API call
        Modifies: self.first_name, self.username
        """
        logger.info('Getting my bot info')
        method = 'getMe'
        url = self.apiurl + '/' + method
        json_data = self._request(url, data={}, files=None)
        try:
            self.first_name = json_data['result']['first_name']
            self.username = json_data['result']['username']
        except:
            logger.error('LoL! My info is not contained in the HTTP response')
        else:
            logger.debug('My first_name is "{0}"'.format(self.first_name))
            logger.debug('My username is "{0}"'.format(self.username))

    def get_updates(self):
        logger.info('Getting bot updates')
        method = 'getUpdates'
        url = self.apiurl + '/' + method
        data = {'offset': self.update_id + 1}
        if self.update_id == 0:
            data = None
        json_data = self._request(url, data=data)
        for result in json_data['result']:
            self._write_update_id(result['update_id'])
            if result['message']:
                text = result['message']['text']
                chat_id = result['message']['chat']['id']
                user_id = result['message']['from']['id']
                user_name = result['message']['from']['first_name']
                text_reply = 'Sorry {0}, I can\'t talk to people'.format(
                    user_name)
                try:
                    chat_title = result['message']['chat']['title']
                except:
                    chat_title = 'null'
                logger.debug(
                    'Received message from user {0}: {1}'.format(
                        user_name,
                        text))
                if text.startswith('/'):
                    self._handle_command(result['message'])
                else:
                    self.send_message(chat_id, text_reply)
                    logger.debug(
                        'Replying to user {0}: {1}'.format(
                            user_name,
                            text_reply))

    # END TELEGRAM API IMPLEMENTATION ========================================
