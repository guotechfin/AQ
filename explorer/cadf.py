#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from mysql import connector
import numpy as np
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

import pprint
import statsmodels.tsa.stattools as ts

class CADF:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")

        self.aq.log("Stop")