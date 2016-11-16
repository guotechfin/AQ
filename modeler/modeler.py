#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class Modeler:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")


        # CADF(self.aq).execute()

        self.aq.log("Stop")