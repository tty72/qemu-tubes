import os
path = os.path
import signal
import subprocess

class PathConfig(object):
    def configure(self, settings):
        """ Set various path configuration values
        settings -- dictionary containing path settings (see development.ini)
        """
        self._settings = settings
        
    @property
    def settings(self):
        try:
            return self._settings
        except AttributeError:
            return None

class Launchable(object):
    """ Mix-in for launchable models """
    def flatten(self, lst):
        """ Flatten a shallow iterable of iterables """
        return [i for subi in lst for i in subi]

    def launch(self):
        """ Launch this instance if not already running """
        if self.running:
            #FIXME: LOG or raise exception here?
            return (-254, 'Already running')
        args = self.flatten(self.args)
        try:
            subprocess.check_output(args, stderr=subprocess.STDOUT, 
                                    close_fds=True)
        except subprocess.CalledProcessError, e:
            return (e.returncode, e.output)
        return (0, 'Success')
        
    @property
    def pidfile(self):
        """ Return the PID file path - child classes must provide this """
        raise NotImplementedError

    @property
    def pid(self):
        """ Return PID for this launchable, if PID file exists else None """
        try:
            with open(self.pidfile) as f:
                return int(f.read().strip())
        except IOError:
            return None

    @property
    def running(self):
        """ Return True if we think the process for this launchable is
            currently active
        """
        if not self.pid: # Should be okay, PID should never be 0
            return False
        try:
            os.kill(self.pid, 0)
        except OSError:
            #FIXME: Unlink any stale PID file here?
            return False
        return True

    def kill(self, term=True):
        """ Kill this process 
            term - Set False to kill with extreme prejudice """
        sig = signal.SIGTERM if term else signal.SIGKILL
        if self.pid:
            os.kill(self.pid, sig)

