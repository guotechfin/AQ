#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from modeler.adf import ADF
from modeler.cadf import CADF

class Modeler:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")

        ADF(self.aq).execute()
        # CADF(self.aq).execute()

        self.aq.log("Stop")