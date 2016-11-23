#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mysql import connector
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

class ML:

    def __init__(self, aq):
        self.aq = aq

    def get_y(self, data, rtn_lag, vol_lag):
        y = data.chg[max(rtn_lag, vol_lag):]
        y.index = range(len(y))
        y = y.apply(lambda x: x > 0)
        return y

    def get_X(self, data, rtn_lag, vol_lag):
        X = pd.DataFrame(columns=range(rtn_lag + vol_lag))
        for idx, row in data.iterrows():
            if idx >= rtn_lag and idx >= vol_lag:
                vol = data.iloc[(idx - vol_lag):idx, 1]
                rtn = data.iloc[(idx - rtn_lag):idx, 2]
                xrow = pd.concat([rtn, vol], ignore_index=True)
                X = X.append(xrow, ignore_index=True)
        return X

    def cross_check(self, model, k_fold, X, y):
        hit_rate_sum = 0
        stride = round(len(y) / k_fold)
        for i in range(0, k_fold):
            start = i * stride
            stop = i * stride + stride - 1
            if (i == k_fold - 1):
                stop = len(y)
            X_test = X[start:stop]
            y_test = y[start:stop]
            X_train = pd.concat([X[0:start - 1], X[stop:]])
            y_train = pd.concat([y[0:start - 1], y[stop:]])
            model.fit(X_train, y_train)
            hit_rate = np.sum(model.predict(X_test) == y_test) / (stop-start)
            hit_rate_sum += hit_rate
            self.aq.log("  k_fold=%s, %.2f%s" % (i+1, hit_rate*100 , "%"))

        return hit_rate_sum/k_fold

    def ml(self, code, type):
        mysql_connector = connector.connect(host=self.aq.DB_HOST, database=self.aq.DB_NAME,
                                            user=self.aq.DB_USR, password=self.aq.DB_PWD)

        data = pd.read_sql("""SELECT close, volume FROM future_trade WHERE code='%s' AND type='%s' """ % (code, type),
                              con=mysql_connector)
        data["chg"] = data.close.diff()
        data.iloc[0, 2] = 0

        rtn_lag = 10
        vol_lag = 10
        k_fold = 10

        self.aq.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        model = LogisticRegression()
        self.aq.log("Code = %s" % code)
        self.aq.log("Logistic Regression")
        hit_rate = self.cross_check(model, k_fold, self.get_X(data, rtn_lag, vol_lag), self.get_y(data, rtn_lag, vol_lag))
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))

        self.aq.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        model = GaussianNB()
        self.aq.log("Code = %s" % code)
        self.aq.log("Naive Bayes")
        hit_rate = self.cross_check(model, k_fold, self.get_X(data, rtn_lag, vol_lag), self.get_y(data, rtn_lag, vol_lag))
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))

        self.aq.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        model = KNeighborsClassifier()
        self.aq.log("Code = %s" % code)
        self.aq.log("K Neighbors")
        hit_rate = self.cross_check(model, k_fold, self.get_X(data, rtn_lag, vol_lag), self.get_y(data, rtn_lag, vol_lag))
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))

        self.aq.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        model = DecisionTreeClassifier()
        self.aq.log("Code = %s" % code)
        self.aq.log("Decision Tree")
        hit_rate = self.cross_check(model, k_fold, self.get_X(data, rtn_lag, vol_lag), self.get_y(data, rtn_lag, vol_lag))
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))

        self.aq.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        model = SVC()
        self.aq.log("Code = %s" % code)
        self.aq.log("Support Vector Machine")
        hit_rate = self.cross_check(model, k_fold, self.get_X(data, rtn_lag, vol_lag), self.get_y(data, rtn_lag, vol_lag))
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))

        self.aq.log(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

        mysql_connector.close()

    def execute(self):
        self.aq.log("Start")

        self.ml("P", "d")

        self.aq.log("Stop")