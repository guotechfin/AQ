#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from mysql import connector
import numpy as np
import pandas as pd
from sklearn import preprocessing
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.svm import SVC

class ML:

    def __init__(self, aq):
        self.aq = aq

    def get_data(self, code, type):
        mysql_connector = connector.connect(host="127.0.0.1", database="aq", user="root", password="!QAZ2wsx#EDC")
        data = pd.read_sql("""SELECT close, high-low as hl, close-open as oc FROM future_trade
                            WHERE code='%s' AND type='%s' """ % (code, type), con=mysql_connector)
        data_1 = data.close.diff()
        data_1[0] = 0
        data_2 = data.hl
        data_3 = data.oc
        data = pd.DataFrame({"data_1": data_1, "data_2": data_2, "data_3": data_3})
        data = pd.DataFrame(preprocessing.normalize(data), columns=["data_1", "data_2", "data_3"])
        mysql_connector.close()
        return data

    def get_Y(self, data, lag_1, lag_2, lag_3):
        Y = data.data_1[max(lag_1, lag_2, lag_3):]
        Y.index = range(len(Y))
        Y = Y.apply(lambda x: x >= 0)
        return Y

    def get_X(self, data, lag_1, lag_2, lag_3):
        X = pd.DataFrame(columns=range(lag_1 + lag_2 + lag_3))
        for idx, row in data.iterrows():
            if idx >= lag_1 and idx >= lag_2 and idx >= lag_3:
                data_1 = data.iloc[(idx - lag_1):idx, 0]
                data_2 = data.iloc[(idx - lag_2):idx, 1]
                data_3 = data.iloc[(idx - lag_3):idx, 2]
                xrow = pd.concat([data_1, data_2, data_3], ignore_index=True)
                X = X.append(xrow, ignore_index=True)
        return X

    def cross_check(self, model, k_fold, X, Y):
        hit_rate_sum = 0
        stride = round(len(Y) / k_fold)
        for i in range(0, k_fold):
            start = i * stride
            stop = i * stride + stride - 1
            if (i == k_fold - 1):
                stop = len(Y)
            X_test = X[start:stop]
            Y_test = Y[start:stop]
            if (i == 0):
                X_train = X[stop:]
                Y_train = Y[stop:]
            else:
                X_train = pd.concat([X[0:start], X[stop:]])
                Y_train = pd.concat([Y[0:start], Y[stop:]])
            model.fit(X_train, Y_train)
            hit_rate = np.sum(model.predict(X_test) == Y_test) / (stop - start)
            hit_rate_sum += hit_rate
            self.aq.log("  k_fold=%s, %.2f%s, start=%d, stop=%d, test_len=%d, train_len=%d" %
                           (i+1, hit_rate*100 , "%", start, stop, len(Y_test), len(Y_train)))
        return hit_rate_sum / k_fold

    def ml(self, code, type, lags, k_fold):
        self.aq.log("Code=%s, Type=%s, lags=%s, k_fold=%s" % (code, type, lags, k_fold))

        mysql_connector = connector.connect(host=self.aq.DB_HOST, database=self.aq.DB_NAME,
                                            user=self.aq.DB_USR, password=self.aq.DB_PWD)

        data = self.get_data(code, type)

        lag_1 = lags[0]
        lag_2 = lags[1]
        lag_3 = lags[2]

        X = self.get_X(data, lag_1, lag_2, lag_3)
        Y = self.get_Y(data, lag_1, lag_2, lag_3)

        model = ExtraTreesClassifier()
        model.fit(X, Y)
        self.aq.log(model.feature_importances_)
        self.aq.log("")

        self.aq.log("Logistic Regression")
        model = LogisticRegression()
        hit_rate = self.cross_check(model, k_fold, X, Y)
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))
        self.aq.log(" ")

        self.aq.log("Naive Bayes")
        model = GaussianNB()
        hit_rate = self.cross_check(model, k_fold, X, Y)
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))
        self.aq.log("")

        self.aq.log("K Neighbors")
        model = KNeighborsClassifier()
        hit_rate = self.cross_check(model, k_fold, X, Y)
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))
        self.aq.log("")

        self.aq.log("Decision Tree")
        model = DecisionTreeClassifier()
        hit_rate = self.cross_check(model, k_fold, X, Y)
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))
        self.aq.log("")

        self.aq.log("Support Vector Machine")
        model = SVC()
        hit_rate = self.cross_check(model, k_fold, X, Y)
        self.aq.log("Average Hit Rate = %g%s" % (hit_rate * 100, "%"))
        self.aq.log("")

        mysql_connector.close()

    def execute(self):
        self.aq.log("Start")

        self.ml("I", "1", [2, 2, 2], 20)
        self.ml("I", "1", [3, 3, 3], 20)
        self.ml("I", "1", [4, 4, 4], 20)
        self.ml("I", "1", [5, 5, 5], 20)

        self.aq.log("Stop")