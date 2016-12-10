#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import inspect
import logging

from crawler.crawler import Crawler
from explorer.explorer import Explorer
from modeler.modeler import Modeler

class AQ:

    # Global constants
    WS_PATH = os.path.abspath("../workspace/") + os.sep
    DB_HOST = "127.0.0.1"
    DB_USR = "root"
    DB_PWD = "!QAZ2wsx#EDC"
    DB_NAME = "aq"

    def __init__(self):
        # Logging
        log_file = self.WS_PATH + os.path.splitext(os.path.basename(__file__))[0] + ".log"
        if (os.path.isfile(log_file)):
            os.remove(log_file)
        self.logger = logging.getLogger("aq")
        self.logger.setLevel(logging.INFO)
        fh = logging.FileHandler(log_file)
        fh.setLevel(logging.INFO)
        ch = logging.StreamHandler()
        ch.setLevel(logging.INFO)
        fmt = logging.Formatter(fmt='[%(asctime)s] %(message)s',datefmt='%Y-%m-%d %H:%M:%S')
        fh.setFormatter(fmt)
        ch.setFormatter(fmt)
        self.logger.addHandler(fh)
        self.logger.addHandler(ch)

    def log(self, msg):
        class_name = inspect.currentframe().f_back.f_locals['self'].__class__.__name__
        func_name = inspect.currentframe().f_back.f_code.co_name
        file_name = inspect.currentframe().f_back.f_code.co_filename
        line_number = inspect.currentframe().f_back.f_code.co_firstlineno
        #self.logger.info((" %s [%s::%s][%s:%i]") % (msg, class_name, func_name, file_name, line_number))
        self.logger.info(" %s" % msg)

    def execute(self):
        self.log("Start")
        if (not True):
            crawler = Crawler(self)
            crawler.execute()
        if (True):
            explorer = Explorer(self)
            explorer.execute()
        self.log("Stop")

if __name__ == '__main__':
    aq = AQ()
    aq.execute()





