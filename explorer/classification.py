#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mysql import connector
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn import svm

class Classification:
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
        y = y.apply(lambda x: x >= 0)
        return y

    def cross_validate(self, code, type, model, k_fold):
        self.aq.log("Model: %s" % model)
        data = self.get_data(code, type)
        X = self.get_X(data, 3)
        y = self.get_y(data, 3)
        scores = cross_val_score(model, X, y, cv=k_fold)
        self.aq.log("Scores Mean: %s\n" % scores.mean())

    def long_short_validate(self, code, type, model, lag, train_len, test_len):
        self.aq.log("Model: %s" % model)

        data = self.get_data(code, type)
        X = self.get_X(data, lag)
        y = self.get_y(data, lag)

        total = 0
        start = 0
        stop = train_len + test_len
        y_len = len(y)
        while (stop < y_len):
            self.aq.log("Start:%s, Stop:%s" % (start, stop))
            X_train = X.iloc[start:(start + train_len)]
            y_train = y.iloc[start:(start + train_len)]
            model.fit(X_train, y_train)
            X_test = X.iloc[(stop - test_len):stop]
            y_test = y.iloc[(stop - test_len):stop]
            for idx in range(len(y_test)):
                if (model.predict(X_test.iloc[idx].reshape(-1, lag * 3)) == y_test.iloc[idx]):
                    total = total + abs(X_test.iloc[idx][lag - 1])
                    self.aq.log("Right Prediction, close_diff=%s, total=%s" % (X_test.iloc[idx][lag - 1], total))
                else:
                    total = total - abs(X_test.iloc[idx][lag - 1])
                    self.aq.log("Wrong Prediction, close_diff=%s, total=%s" % (X_test.iloc[idx][lag - 1], total))
            start = start + test_len
            stop = stop + test_len

    def execute(self):
        self.aq.log("Start")

        code = "I"
        type = "5"
        self.long_short_validate(code, type, LogisticRegression(), 3, 5000, 100)

        self.aq.log("Stop")