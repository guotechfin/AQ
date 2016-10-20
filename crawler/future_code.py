#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import csv
from mysql import connector


class FutureCode:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):

        self.aq.log("Start")

        FUTURE_CODE_CSV_PATH = self.aq.WS_PATH + "crawler/future_code.csv"

        # Re-Init Database
        connect = connector.connect(host=self.aq.DB_HOST,
                                    user=self.aq.DB_USR,
                                    password=self.aq.DB_PWD,
                                    database=self.aq.DB_NAME)
        cursor = connect.cursor()

        cursor.execute("""CREATE TABLE IF NOT EXISTS future_code(
                            code VARCHAR(50) NOT NULL,
                            name VARCHAR(50) NOT NULL,
                            exchange VARCHAR(50) NOT NULL, PRIMARY KEY(code));""")
        connect.commit()

        self.aq.log("Create future_code table")

        with open(FUTURE_CODE_CSV_PATH,  encoding='utf-8') as code_csv:
            codes = csv.reader(code_csv)
            next(codes)
            for row in codes:
                cursor.execute("INSERT INTO future_code VALUES(%s, %s, %s) ON DUPLICATE KEY UPDATE code=%s;"
                               , (row[0], row[1], row[2], row[0]))
                self.aq.log("Insert Code (" + row[0] + ", " + row[1] + ")")
            connect.commit()


        cursor.close()
        connect.close()

        self.aq.log("Stop")