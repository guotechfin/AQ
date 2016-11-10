#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from mysql import connector
from numpy import cumsum, log, polyfit, sqrt, std, subtract
import statsmodels.tsa.stattools as ts

class StatsTest:

    def __init__(self, aq):
        self.aq = aq

    def hurst(self, ts):
        """Returns the Hurst Exponent of the time series vector ts"""
        # Create the range of lag values
        lags = range(2, 100)
        # Calculate the array of the variances of the lagged differences
        tau = []
        for lag in lags:
            s1 = subtract(ts[lag:], ts[:-lag])
            s2 = std(s1)
            s3 = sqrt(s2)
            tau.append(s3)
        # Use a linear fit to estimate the Hurst Exponent
        poly = polyfit(log(lags), log(tau), 1)
        # Return the Hurst exponent from the polyfit output
        return poly[0] * 2.0

    def execute(self):
        self.aq.log("Start")

        code = "P"
        type = "5"
        mysql_connector = connector.connect(host=self.aq.DB_HOST, database=self.aq.DB_NAME,
                                            user=self.aq.DB_USR, password=self.aq.DB_PWD)
        data = pd.read_sql("""SELECT datetime, open, high, low, close, volume, oi FROM future_trade
                            WHERE code='%s' AND type='%s' """ % (code, type), con=mysql_connector)
        mysql_connector.close()

        close_rtn = (data.close.diff()/data.close.shift(1))[1:]
        print(ts.adfuller(close_rtn, 1))
        print(ts.adfuller(data.volume, 1))

        print(self.hurst(log(close_rtn.values.tolist())))

        self.aq.log("Stop")