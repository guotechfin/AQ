#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import math
import struct
from functools import partial
from mysql import connector

class FutureTrade:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):

        self.aq.log('Start')

        w_connect = connector.connect(host=self.aq.DB_HOST,
                                    user=self.aq.DB_USR,
                                    password=self.aq.DB_PWD,
                                    database=self.aq.DB_NAME)
        w_cursor = w_connect.cursor()
        w_cursor.execute("""CREATE TABLE IF NOT EXISTS future_trade(
                            code VARCHAR(50) NOT NULL,
                            type VARCHAR(50) NOT NULL,
                            datetime DATETIME NOT NULL,
                            open DOUBLE NOT NULL,
                            high DOUBLE NOT NULL,
                            low DOUBLE NOT NULL,
                            close DOUBLE NOT NULL,
                            volume DOUBLE NOT NULL,
                            oi DOUBLE NOT NULL,
                            sp DOUBLE NOT NULL,
                            PRIMARY KEY(code,datetime));""")
        w_connect.commit()
        w_cursor.close()
        w_connect.close()

        self.aq.log("Create future_trade table")

        r_connect = connector.connect(host=self.aq.DB_HOST,
                                    user=self.aq.DB_USR,
                                    password=self.aq.DB_PWD,
                                    database=self.aq.DB_NAME)
        r_cursor = r_connect.cursor()
        r_cursor.execute("SELECT code, name FROM aq.future_code;")
        results = []
        for (code, name) in r_cursor:
            results.append((code, name))
        r_cursor.close()
        r_connect.close()

        TDX_DAY_PATH = 'C:/zd_zszq/vipdoc/ds/lday/'
        TDX_LC5_PATH = 'C:/zd_zszq/vipdoc/ds/fzline/'
        TDX_LC1_PATH = 'C:/zd_zszq/vipdoc/ds/minline/'

        day_files = [day_file for day_file in os.listdir(TDX_DAY_PATH)
                     if os.path.isfile(os.path.join(TDX_DAY_PATH, day_file))]
        lc5_files = [lc5_file for lc5_file in os.listdir(TDX_LC5_PATH) if
                     os.path.isfile(os.path.join(TDX_LC5_PATH, lc5_file))]
        lc1_files = [lc1_file for lc1_file in os.listdir(TDX_LC1_PATH) if
                     os.path.isfile(os.path.join(TDX_LC1_PATH, lc1_file))]

        for (code, name) in results:
            day_file = self._find_tdx_file(code, "L8.day", day_files)
            self._day_to_db(code, "d", TDX_DAY_PATH + day_file)
            self.aq.log("Insert day trade (" + code + ", " + name + ")")

            lc5_file = self._find_tdx_file(code, "L8.lc5", lc5_files)
            self._lc_to_db(code, "5", TDX_LC5_PATH + lc5_file)
            self.aq.log("Insert 5m trade (" + code + ", " + name + ")")

            #lc1_file = self._find_tdx_file(code, "L8.lc1", lc1_files)
            #self._lc_to_db(code, "1", TDX_LC1_PATH + lc1_file)
            #self.aq.log("Insert 1m trade (" + code + ", " + name + ")")

        self.aq.log('Stop')

    def _find_tdx_file(self, code, suffix, files):
        for file in files:
            if file.endswith("#" + code + suffix):
                return file

    # 通达信期货日数据格式：
    # 每32个字节为一个数据，每字段内低字节在前
    # 00 ~ 01 字节：日期，整型
    #               设其值为num则日期计算方法为：
    #               year=floor(num/2048)+2004
    #               month=floor(mod(num,2048)/100)
    #               day=mod(mod(num,2048),100);
    # 02 ~ 03 字节：从0点开始至目前的分钟数，整型
    # 04 ~ 07 字节：开盘价，浮点型
    # 08 ~ 11 字节：最高价，浮点型
    # 12 ~ 15 字节：最低价，浮点型
    # 16 ~ 19 字节：收盘价，浮点型
    # 20 ~ 23 字节：成交量，整形
    # 24 ~ 27 字节：持仓量，整型
    # 28 ~ 31 字节：结算价，浮点型
    def _day_to_db(self, code, type, day_file):
        w_connect = connector.connect(host=self.aq.DB_HOST,
                                      user=self.aq.DB_USR,
                                      password=self.aq.DB_PWD,
                                      database=self.aq.DB_NAME)
        w_cursor = w_connect.cursor()

        with open(day_file, 'rb') as day:
            records = iter(partial(day.read, 32), b'')
            for r in records:
                data = struct.unpack("<iffffiif", r)
                date = str(data[0])
                year = date[0:4]
                month = date[4:6]
                day = date[6:8]
                datetime = year + "-" + month + "-" + day
                o = data[1]
                h = data[2]
                l = data[3]
                c = data[4]
                v = data[6]
                oi = data[5]
                sp = data[7]
                w_cursor.execute("""INSERT INTO future_trade VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE code=%s, datetime=%s;""",
                                 (code, type, datetime, o, h, l, c, v, oi, sp, code, datetime))

        w_connect.commit()
        w_cursor.close()
        w_connect.close()

    # 通达信期货分钟数据格式：
    # 每32个字节为一个数据，每字段内低字节在前
    # 00 ~ 01 字节：日期（年月日），整型
    # 02 ~ 03 字节：开盘价，浮点型
    # 04 ~ 07 字节：最高价，浮点型
    # 08 ~ 11 字节：最低价，浮点型
    # 12 ~ 15 字节：收盘价，浮点型
    # 16 ~ 19 字节：成交量，整形
    # 20 ~ 23 字节：持仓量，整型
    # 24 ~ 27 字节：结算价，浮点型
    # 28 ~ 31 字节：保留
    def _lc_to_db(self, code, type, lc_file):
        w_connect = connector.connect(host=self.aq.DB_HOST,
                                      user=self.aq.DB_USR,
                                      password=self.aq.DB_PWD,
                                      database=self.aq.DB_NAME)
        w_cursor = w_connect.cursor()

        with open(lc_file, 'rb') as lc:
            records = iter(partial(lc.read, 32), b'')
            for r in records:
                data = struct.unpack("<hhffffiif", r)
                year = "%d" % (math.floor(data[0] / 2048) + 2004)
                year = year.zfill(4)
                month = "%d" % (math.floor((data[0] % 2048) / 100))
                month = month.zfill(2)
                day = "%d" % ((data[0] % 2048) % 100)
                day = day.zfill(2)
                hour = "%d" % (data[1] / 60)
                hour = hour.zfill(2)
                minute = "%d" % (data[1] % 60)
                minute = minute.zfill(2)
                datetime = "%s-%-s-%s %s:%s" % (year, month, day, hour, minute)
                o = data[2]
                h = data[3]
                l = data[4]
                c = data[5]
                v = data[7]
                oi = data[6]
                sp = data[8]
                w_cursor.execute("""INSERT INTO future_trade VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                                    ON DUPLICATE KEY UPDATE code=%s, datetime=%s;""",
                                 (code, type, datetime, o, h, l, c, v, oi, sp, code, datetime))
        w_connect.commit()
        w_cursor.close()
        w_connect.close()
