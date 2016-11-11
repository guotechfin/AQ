#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from modeler.statstest import StatsTest

class Modeler:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")

        StatsTest(self.aq).execute()

        self.aq.log("Stop")