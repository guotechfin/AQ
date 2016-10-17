#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
from mysql import connector

class StockCode:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log('Start')

        STOCK_CODE_CSV_PATH = self.aq.WS_PATH + "crawler/stock_code.csv"
        STOCK_ETF_CSV_PATH = self.aq.WS_PATH + "crawler/stock_etf.csv"
        STOCK_IDX_CSV_PATH = self.aq.WS_PATH + "crawler/stock_idx.csv"

        # Re-Init Database
        connect = connector.connect(host=self.aq.DB_HOST,
                                    user=self.aq.DB_USR,
                                    password=self.aq.DB_PWD,
                                    database=self.aq.DB_NAME)
        cursor = connect.cursor()

        cursor.execute("CREATE TABLE IF NOT EXISTS stock_code(\
                        code VARCHAR(50) NOT NULL, \
                        type VARCHAR(50) NOT NULL, \
                        name VARCHAR(50) NOT NULL,\
                        industry VARCHAR(50) NOT NULL,\
                        region VARCHAR(50) NOT NULL,\
                        PRIMARY KEY(code));")
        connect.commit()

        self.aq.log("Create stock_code table")

        # Stock Code
        with open(STOCK_CODE_CSV_PATH, encoding='utf-8') as code_csv:
            codes = csv.reader(code_csv)
            next(codes)
            for row in codes:
                cursor.execute("INSERT INTO stock_code VALUES(%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE code=%s;",
                               (row[0], "stock", row[1], row[2], row[3], row[0]))
                self.aq.log("Insert Stock Code (" + row[0] + ", " + row[1] + ")")
            connect.commit()

        # ETF Code
        with open(STOCK_ETF_CSV_PATH, encoding='utf-8') as code_csv:
            codes = csv.reader(code_csv)
            next(codes)
            for row in codes:
                cursor.execute("INSERT INTO stock_code VALUES(%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE code=%s;",
                               (row[0], "etf", row[1], "", "", row[0]))
                self.aq.log("Insert ETF Code (" + row[0] + ", " + row[1] + ")")
            connect.commit()

        # Index
        with open(STOCK_IDX_CSV_PATH, encoding='utf-8') as code_csv:
            codes = csv.reader(code_csv)
            next(codes)
            for row in codes:
                cursor.execute("INSERT INTO stock_code VALUES(%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE code=%s;",
                               (row[0], "idx", row[1], "", "", row[0]))
                self.aq.log("Insert Index Code (" + row[0] + ", " + row[1] + ")")
                connect.commit()

        cursor.close()
        connect.close()

        self.aq.log('Stop')