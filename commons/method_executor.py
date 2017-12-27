from __future__ import print_function

import logging
import sys

from abstract_controller import AbstractController


class Method_Executor(AbstractController):
    def __init__(self, db):
        AbstractController.__init__(self, db)
        self._actions = self._config_parser.eval(self.__class__.__name__, "actions")

    def execute(self, window_start=None):
        for action_name in self._actions:
            try:
                getattr(self, action_name)()
            except AttributeError as e:
                print('\nError: {0}\n'.format(e.message), file=sys.stderr)
                logging.error('Error: {0}'.format(e.message))
