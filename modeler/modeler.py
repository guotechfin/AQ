#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from modeler.st_adf import ST_ADF

class Modeler:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")
        ST_ADF(self.aq).execute()
        self.aq.log("Stop")