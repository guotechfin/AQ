#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mysql import connector
import pandas as pd

class ML:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")
        mysql_connector = connector.connect(host=self.aq.DB_HOST, database=self.aq.DB_NAME,
                                            user=self.aq.DB_USR, password=self.aq.DB_PWD)
        code = pd.read_sql("""SELECT code FROM aq.future_code;""", con=mysql_connector)
        for row in code.itertuples():
            data = pd.read_sql("""SELECT close, volume FROM future_trade
                                  WHERE code='%s' AND type='%s' """ % (row[1], 5), con=mysql_connector)
            lag = 5
            rtn_lag = pd.DataFrame(columns=range(lag))
            vol_lag = pd.DataFrame(columns=range(lag))
            rtn = data["rtn"]
            for idx, row in data.iterrows():
                if idx >= lag:
                    tmp = data.iloc[(idx - lag):idx, 1]
                    tmp.index = range(lag)
                    vol_lag = vol_lag.append(tmp, ignore_index=True)
                    tmp = data.iloc[(idx - lag):idx, 2]
                    tmp.index = range(lag)
                    rtn_lag = rtn_lag.append(tmp, ignore_index=True)
        mysql_connector.close()

        rtn_lag
        vol_lag
        rtn

        self.aq.log("Stop")