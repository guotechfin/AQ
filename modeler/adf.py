#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from mysql import connector
import statsmodels.tsa.stattools as ts

class ADF:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")
        mysql_connector = connector.connect(host=self.aq.DB_HOST, database=self.aq.DB_NAME,
                                            user=self.aq.DB_USR, password=self.aq.DB_PWD)
        code = pd.read_sql("""SELECT code FROM aq.future_code;""", con=mysql_connector)
        for row in code.itertuples():
            data = pd.read_sql("""SELECT datetime, open, high, low, close, volume, oi FROM future_trade
                               WHERE code='%s' AND type='%s' """ % (row[1], 1), con=mysql_connector)
            adf = ts.adfuller((data.close.diff() / data.close.shift(1))[1:], 1)
            self.aq.log("%s: ADF=%f, p-value=%.10f" % (row[1], adf[0], adf[1]))
        mysql_connector.close()

        self.aq.log("Stop")