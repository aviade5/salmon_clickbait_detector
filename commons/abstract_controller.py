# Created by aviade      
# Time: 02/05/2016 14:59

import datetime
import logging
from logging import config

from config_class import getConfig


class AbstractController(object):
    def __init__(self, db):
        self._config_parser = getConfig()
        self._db = db

        logging.config.fileConfig(self._config_parser.get("DEFAULT", "logger_conf_file"))
        self.logger = logging.getLogger(self._config_parser.get("DEFAULT", "logger_name"))
        self._start_date = self._config_parser.get(self.__class__.__name__, "start_date")
        self._window_start_query = self._config_parser.get(self.__class__.__name__, "start_date").strip("date('')")
        self._window_size = datetime.timedelta(seconds=int(self._config_parser.get(self.__class__.__name__, "window_analyze_size_in_sec")))
        self.keep_results_for = datetime.timedelta(seconds=self._config_parser.getint(self.__class__.__name__, "keep_results_for"))
        self._window_start = self._config_parser.eval(self.__class__.__name__, "start_date")
        self._social_network_url = self._config_parser.eval("DEFAULT", 'social_network_url')
        self._domain = unicode(self._config_parser.get(self.__class__.__name__, "domain"))

    @property
    def _window_end(self):
        return self._window_start + self._window_size

    def setUp(self):
        pass

    def execute(self, window_start):
        self._window_start = window_start

    def cleanUp(self, window_start):
        pass

    def canProceedNext(self, window_start):
        return True

    def tearDown(self):
        pass
