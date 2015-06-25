# -*- coding: UTF-8 -*-
#
# Author: borja@libcrack.so
# Date: jue oct 27 01:31:02 CEST 2011

import os
import shutil
import subprocess
import sys
import re

import xml.dom.minidom
import xml.parsers.expat

import xml.sax
import xml.sax.handler

from Logger import Logger
logger = Logger.logger

# ====================================================================================

class Config(object):
    '''
        The config class is a handler for setup.conf configuration file
        This class maps the configuration into a dict.

        If you want to inherit from Config, just overwrite the methods for
        _read_config and _write_config for custom configuration file parsing


    '''

    # --------------------------------------------------------------------------------

    def __init__ (self,config_file=None):

        # config path
        self._config_file = None
        # conf dict
        self._conf = {}

        # read config now
        if config_file:
            self._config_file = config_file
            self._read_config()

    # --------------------------------------------------------------------------------

    def __setitem__ (self, key, item) :
        self._conf[key] = item

    # --------------------------------------------------------------------------------

    def __getitem__ (self, key) :
        if key == 'passwd':
            return self._conf.get('pass', None)
        else:
            return self._conf.get(key, None)

    # --------------------------------------------------------------------------------

    def __repr__ (self):
        string = []
        for key,value in self._conf.items():
            string.append('%s\t: %s\n' % (key, value))
        return ''.join(string)

    # --------------------------------------------------------------------------------

    def _read_config (self):

        try:
            logger.info ('Reading config file: %s' % self._config_file)
            config = open(self._config_file)
        except IOError as e:
            logger.error ('Error opening file %s : (%s)' % (self._config_file,e))
            raise (e)

        pattern = re.compile('^(\S+)\s*=\s*(.+)')

        for line in config:
            result = pattern.match(line)
            if result is not None:
                (key, value) = result.groups()
                self._conf[key] = value

        config.close()

    # --------------------------------------------------------------------------------

    def _write_config (self):
        '''
            Writes the current object values to the configuration file DESTROYING the previos content
        '''
        try:
            logger.info ('Opening config file %s for writing' % self._config_file)
            config_fd = open(self._config_file,'r')
        except IOError as e:
            msg = 'Error opening file %s : (%s)' % (self._config_file,e)
            logger.error(msg)
            raise Exception (msg)

        tmp_name = self._config_file + '.reconf'

        try:
            tmp_fd = open(tmp_name, 'w')
        except IOError as e:
            msg = 'ERROR al abrir %s : %s' % (tmp_name,e)
            logger.error(msg)
            raise Exception (msg)

        # merge the two files
        for line in config_fd.readlines():
            new_line = line
            for k,v in self._conf.items():
                pattern = re.compile('^%s\s*=\s*(\S+)' % k)
                if pattern.match(line):
                    new_line = '%s=%s\n' % (k,v)
            tmp_fd.write(new_line)

        # close descriptors
        config_fd.close()
        tmp_fd.close()

        # rename original and remove tmp file
        try:
            os.rename(tmp_name,self._config_file)
        except os.error as e:
            raise Exception (e)


    # --------------------------------------------------------------------------------

    def read (self,config_path=None):
        '''
            Reads the file configuration. If config_path if provided, this method
            sets the internal file pointer to config_path.
        '''

        if config_path:
            self._config_file = config_path

        if not self._config_file:
            raise Exception ('You must provide a valid path for the config file')

        self._read_config()

    # --------------------------------------------------------------------------------

    def write (self,config_path=None):
        '''
            Writes the file configuration. If config_path if provided, this method
            sets the internal file pointer to config_path.
        '''

        if config_path:
            self._config_file = config_path

        if not self._config_file:
            raise Exception ('You must provide a valid path for the config file')

        self._write_config()


    # --------------------------------------------------------------------------------

    def backup (self):
        '''
            Backup config file (copies foo.cfg to foo.cfg.tmp)
        '''
        if not self._config_file:
            raise Exception ('You must provide a valid path for the config file backup')
        try:
            tmp_file = self._config_file + '.tmp'
            shutil.copy(self._config_file, tmp_file)
        except shutil.Error as exception:
            raise Exception (exception)

    # --------------------------------------------------------------------------------

    def restore (self):
        '''
            Restore config file (rename foo.cfg.tmp to foo.cfg)
        '''
        if not self._config_file:
            raise Exception ('You must provide a valid path for the config file')
        try:
            tmp_file = self._config_file + '.tmp'
            shutil.move(tmp_file, self._config_file)
        except shutil.Error as excepcion:
            raise Exception (exception)

    # --------------------------------------------------------------------------------

    def reload_config (self):
        '''
            Reload the proccess,so new configuration can be read
        '''
        try:
            proceso = subprocess.check_call(self._init_script_path,
                    len(self._init_script_path), None, None, None, shell=False)
        except (subprocess.CalledProcessError,OSError) as excepcion:
            logger.error ('reload error: %s ' % str(excepcion))

    # --------------------------------------------------------------------------------

    def sed (search_for, replace_with):
        '''
        Replace strings in a text file (aka sed -e s/oldtext/newtext/g)
        '''

        temp = self._config_file + '.tmp.sed'

        try:
            fi = open(self._config_file)
            fo = open(temp, 'w')
        except IOError as e:
            logger.error('%s' % e)
            raise e

        for line in fi.readlines():
            fo.write(string.replace(line, search_for, replace_with))

        fi.close()
        fo.close()

        # rename original
        os.rename(file, back)
        os.rename(temp, file)

        # remove temp file
        try:
            os.remove(temp)
        except os.error:
            pass

# ====================================================================================

class ServerConfig (Config):
    '''
    The ServerConfig class contais the server configuration. It inherits from
    Config overwriting the following inherited attributes from class Config:

        - __init__constructor
        - __repr__ XML representation of conf

        - read  (server.xml conf)
        - write (server.xml conf)

    '''

    # --------------------------------------------------------------------------------

    def __init__ (self,config_file=None):
        '''
        The constructor of ServerConfig add the _config_file attrib to store
        the path for the XML config file of the server. It also keeps the
        config_files param to perform the backup and restore config ops.
        '''

        self._config_file = None
        self._init_script_path = None

        if config_file:
            self._config_file = config_file
            self.read(config_file)


    # --------------------------------------------------------------------------------

    def __repr__ (self):
        '''
        The __repr__ attribute prints the internal XML of the DOM object
        contained in self._dom
        '''
        #return self._dom.toprettyxml()
        return self._dom.toxml()

    # --------------------------------------------------------------------------------

    def write(self, xmlfile=None):
        '''
        This method writes the current DOM structure contained in self._dom to
        an external XML file pointed by xmlfile parameter (filepath)
        If xmlfile parameter is missing, the self._config_file attr will be used
        as filename for writing the XML file.
        '''
        filename = None
        fd = None

        if xmlfile:
            self._config_file = xmlfile
            filename = xmlfile

        # control indent and format
        # self._dom.writexml(fd,addindent='  ',newl='\n',encoding='utf-8')

        try:
            fd = open(self._config_file,'w+')
            self._dom.writexml(fd,encoding='utf-8')
            fd.close()

        except IOError as excepcion:
            raise Exception (excepcion)

    # --------------------------------------------------------------------------------

    def read(self,xmlfile=None):
        '''
        The _read_config reads the XML config file especified by the __init__
        class constructor. It stores the DOM readed from XML config file into
        the object's private attribute self._dom
        '''
        if xmlfile:
            self._config_file = xmlfile

        fd = None

        try:
            # w+ trunk
            fd = open(self._config_file,'r')
        except IOError as excepcion:
            raise Exception (excepcion)

        try:
            # prepare xml doc
            self._dom = xml.dom.minidom.parse(fd)

            # nodes sons's of config (main node)
            nodos = self._dom.childNodes

            log = self._dom.getElementsByTagName('log')[0]
            log_filename = log.getAttribute('filename')

            framework = self._dom.getElementsByTagName('framework')[0]
            framework_name = framework.getAttribute('name')
            framework_ip = framework.getAttribute('ip')
            framework_port = framework.getAttribute('port')

            directive = self._dom.getElementsByTagName('directive')[0]
            directive_filename = directive.getAttribute('filename')

            cvss = self._dom.getElementsByTagName('cvss')[0]
            cvss_filename = cvss.getAttribute('filename')

            scheduler = self._dom.getElementsByTagName('scheduler')[0]
            scheduler_interval = scheduler.getAttribute('interval')

            server = self._dom.getElementsByTagName('server')[0]
            server_name = server.getAttribute('name')
            server_ip = server.getAttribute('ip')
            server_port = server.getAttribute('port')

            logs = self._dom.getElementsByTagName('logs')[0]
            logs_path = logs.getAttribute('path')

            tag_init = self._dom.getElementsByTagName('datasources')[0]
            datasources = tag_init.getElementsByTagName('datasource')

            for datasource in datasources:
                    name = datasource.getAttribute('name')
                    provider = datasource.getAttribute('provider')
                    dsn = datasource.getAttribute('dsn')

            fd.close()

        except xml.parsers.expat.ExpatError as e:
            logger.error ('Syntax Error: %s -- %s' % (self._config_file,e))
            raise Exception (e)

    # --------------------------------------------------------------------------------

    def test(self):
        '''
        Class test method
        '''
        test = Config()
        test.read('../data/setup.conf')
        test.backup()
        print (test)
        test.write()
        test.restore()

        # test = ServerConfig()
        # test.read('../data/server_config.xml')
        # test.backup()
        # print test
        # test.write()
        # test.restore()

