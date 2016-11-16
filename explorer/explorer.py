#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from explorer.adf import ADF
from explorer.cadf import CADF
from explorer.ml import ML

class Explorer:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")

        ADF(self.aq).execute()
        CADF(self.aq).execute()
        ML(self.aq).execute()

        self.aq.log("Stop")