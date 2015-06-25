#!/usr/bin/env python
#
# Date: jue dic 22 04:54:06 CET 2011
# Author: borja@libcrack.so

import atexit
import signal
import time
import sys
import os

from Logger import Logger
logger = Logger.logger

class Daemon(object):
    """
    This is a generic daemon class, supporting start,stop,status and pidfile methods.
    To daemonize a class, simply inherits from Daemon and override the run() method.
    """
    def __init__ (self, pidfile='/tmp/pidfile', stdin='/dev/null', stdout='/dev/null', stderr='/dev/null'):
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr
        self.pidfile = pidfile

    def daemonize (self):
        """
        do the UNIX double-fork magic, see Stevens' "Advanced
        Programming in the UNIX Environment" for details (ISBN 0201563177)
        http://www.erlenstar.demon.co.uk/unix/faq_2.html#SEC16
        """
        try:
            pid = os.fork()
            if pid > 0:
                # exit first parent
                sys.exit(0)
        except OSError as e:
            logger.error('fork #1 failed: {0} ({1})'.format(e.errno, e.strerror))
            sys.exit(1)

        # decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # do second fork
        try:
            pid = os.fork()
            if pid > 0:
                # exit from second parent
                sys.exit(0)
        except OSError as e:
            logger.error('fork #2 failed: {0} ({1})'.format(e.errno, e.strerror))
            sys.exit(1)

        # XXX AVOIDED as the Logger class will manage it
        # # redirect standard file descriptors
        # sys.stdout.flush()
        # sys.stderr.flush()
        # if self.stdin is not None:
        #     si = open(self.stdin, 'r')
        #     os.dup2(si.fileno(), sys.stdin.fileno())
        # if self.stdout is not None:
        #     so = open(self.stdout, 'a+')
        #     os.dup2(so.fileno(), sys.stdout.fileno())
        # if self.stderr is not None:
        #     se = open(self.stderr, 'a+', 0)
        #     os.dup2(se.fileno(), sys.stderr.fileno())

        # write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        try:
            f = open(self.pidfile,'w+')
            f.write('%s\n' % pid)
        except IOError as e:
            logger.error('Cannot write pidfile {0}: ({1}): {2}'.format(self.pidfile, e.errno, e.strerror))
        else:
            f.close()
            logger.info('Written pid {0} in file {1}'.format(pid,self.pidfile))


    def delpid (self):
        os.remove(self.pidfile)


    def start (self):
        """
        Start the daemon
        """
        # Check for a pidfile to see if the daemon already runs
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            logger.error('Cannot read pidfile {0}: ({1}): {2}'.format(self.pidfile, e.errno, e.strerror))
            pid = None

        if pid:
            logger.error('pidfile {0} already exist. Daemon already running?'.format(self.pidfile))
            sys.exit(1)

        # Start the daemon
        self.daemonize()
        self.run()


    def stop (self):
        """
        Stop the daemon
        """
        # Get the pid from the pidfile
        try:
            pf = open(self.pidfile,'r')
            pid = int(pf.read().strip())
            pf.close()
        except IOError as e:
            logger.error('Cannot read pidfile: I/O error({0}): {1}'.format(e.errno, e.strerror))
            pid = None

        if not pid:
            logger.error('pidfile {0} does not exist. Daemon not running'.format(self.pidfile))
            return # not an error in a restart

        # Try killing the daemon process
        try:
            while 1:
                    os.kill(pid, signal.SIGTERM)
                    time.sleep(0.1)
        except OSError as err:
            err = str(err)
            if err.find('No such process') > 0:
                if os.path.exists(self.pidfile):
                    os.remove(self.pidfile)
                else:
                    logger.error('{0}'.format(err))
                    sys.exit(1)


    def restart (self):
        """
        Restart the daemon
        """
        self.stop()
        self.start()


    def run (self):
        """
        Override me
        Called after start() or restart() methods
        """

