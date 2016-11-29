#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mysql import connector
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LinearRegression

class Regression:
    def __init__(self, aq):
        self.aq = aq

    def get_data(self, code, type):
        mysql_connector = connector.connect(host=self.aq.DB_HOST, database=self.aq.DB_NAME,
                                            user=self.aq.DB_USR, password=self.aq.DB_PWD)
        data = pd.read_sql(
            """SELECT close, high-low as hl, close-open as oc FROM future_trade WHERE code='%s' AND type='%s' """ % (
            code, type),
            con=mysql_connector)
        data_1 = data.close.diff()
        data_1[0] = 0
        data_2 = data.hl
        data_3 = data.oc
        data = pd.DataFrame({"data_1": data_1, "data_2": data_2, "data_3": data_3})
        data = pd.DataFrame(preprocessing.normalize(data), columns=["data_1", "data_2", "data_3"])
        mysql_connector.close()
        return data

    def get_X(self, data, lag):
        X = pd.DataFrame(columns=range(lag * 3))
        for idx, row in data.iterrows():
            if idx >= lag:
                data_1 = data.iloc[(idx - lag):idx, 0]
                data_2 = data.iloc[(idx - lag):idx, 1]
                data_3 = data.iloc[(idx - lag):idx, 2]
                xrow = pd.concat([data_1, data_2, data_3], ignore_index=True)
                X = X.append(xrow, ignore_index=True)
        return X

    def get_y(self, data, lag):
        y = data.data_1[lag:]
        y.index = range(len(y))
        return y

    def cross_validate(self, code, type, model, k_fold):
        self.aq.log("Model: %s" % model)
        data = self.get_data(code, type)
        X = self.get_X(data, 3)
        y = self.get_y(data, 3)
        scores = cross_val_score(model, X, y, cv=k_fold)
        self.aq.log("Scores Mean: %s\n" % scores.mean())

    def execute(self):
        self.aq.log("Start")

        code = "I"
        type = "d"
        self.cross_validate(code, type, LinearRegression(), 10)

        self.aq.log("Stop")