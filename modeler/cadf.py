#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pandas as pd
from mysql import connector


class CADF:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")

        code = "P"
        type = "d"
        mysql_connector = connector.connect(host=self.aq.DB_HOST, database=self.aq.DB_NAME,
                                            user=self.aq.DB_USR, password=self.aq.DB_PWD)
        data = pd.read_sql("""SELECT datetime, open, high, low, close, volume, oi FROM future_trade
                            WHERE code='%s' AND type='%s' """ % (code, type), con=mysql_connector)
        mysql_connector.close()

        data["rtn"] = (data.close.diff()/data.close.shift(1))
        he = self.hurst(data.close)


        self.aq.log("Stop")