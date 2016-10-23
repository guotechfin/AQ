#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import time
import re
import collections
import urllib.request
import zipfile
from html.parser import HTMLParser
from mysql import connector

class StockTrade:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log('Start')

        path = self.aq.WS_PATH + "crawler/data/"
        self.create_path(path)

        url = "http://www.tdx.com.cn/products/data/data/vipdoc/shlday.zip"
        file = path + "sh.zip"
        self.download_file(url, file)
        self.aq.log('Download Shanghai trade file')
        self.unzip_file(path, file)
        self.aq.log('Unzip Shanghai trade file')

        url = "http://www.tdx.com.cn/products/data/data/vipdoc/szlday.zip"
        file = path + "sz.zip"
        self.download_file(url, file)
        self.aq.log('Download Shenzhen trade file')
        self.unzip_file(path, file)
        self.aq.log('Unzip Shenzhen trade file')

        # Create stock trade table
        w_connect = connector.connect(host=self.aq.DB_HOST,
                                      user=self.aq.DB_USR,
                                      password=self.aq.DB_PWD,
                                      database=self.aq.DB_NAME)
        w_cursor = w_connect.cursor()
        w_cursor.execute("""CREATE TABLE IF NOT EXISTS stock_trade(
                            code VARCHAR(50) NOT NULL,
                            datetime DATETIME NOT NULL,
                            open DOUBLE NOT NULL,
                            high DOUBLE NOT NULL,
                            low DOUBLE NOT NULL,
                            close DOUBLE NOT NULL,
                            open_exdr DOUBLE NOT NULL,
                            high_exdr DOUBLE NOT NULL,
                            low_exdr DOUBLE NOT NULL,
                            close_exdr DOUBLE NOT NULL,
                            volume DOUBLE NOT NULL,
                            amount DOUBLE NOT NULL,
                            PRIMARY KEY(code,datetime));""")
        w_connect.commit()

        r_connect = connector.connect(host=self.aq.DB_HOST,
                                      user=self.aq.DB_USR,
                                      password=self.aq.DB_PWD,
                                      database=self.aq.DB_NAME)
        r_cursor = r_connect.cursor()
        r_cursor.execute("SELECT code, type, name FROM aq.stock_code;")
        results = []
        for (code, type, name) in r_cursor:
            results.append((code, type, name))
        r_cursor.close()
        r_connect.close()

        count = 0
        for (code, type, name) in results:
            self.aq.log("Insert stock trade (" + code + ", " + name + ")")

            day_file = open(path + self.get_exchange(code, type) + code + ".day", "rb").read()
            length = len(day_file)
            index = 0
            raw_trades = []
            while index < length:
                d = time.strptime(str(int.from_bytes(day_file[index:index + 4], byteorder='little')), "%Y%m%d")
                if (type == "etf"):
                    o = int.from_bytes(day_file[index + 4:index + 8], byteorder='little') / 1000.00
                    h = int.from_bytes(day_file[index + 8:index + 12], byteorder='little') / 1000.00
                    l = int.from_bytes(day_file[index + 12:index + 16], byteorder='little') / 1000.00
                    c = int.from_bytes(day_file[index + 16:index + 20], byteorder='little') / 1000.00
                else:
                    o = int.from_bytes(day_file[index + 4:index + 8], byteorder='little') / 100.00
                    h = int.from_bytes(day_file[index + 8:index + 12], byteorder='little') / 100.00
                    l = int.from_bytes(day_file[index + 12:index + 16], byteorder='little') / 100.00
                    c = int.from_bytes(day_file[index + 16:index + 20], byteorder='little') / 100.00
                a = int.from_bytes(day_file[index + 20:index + 24], byteorder='little')
                v = int.from_bytes(day_file[index + 24:index + 28], byteorder='little')
                raw_trades = [{"datetime": d,
                               "open": o,
                               "high": h,
                               "low": l,
                               "close": c,
                               "amount": a,
                               "volume": v}] + raw_trades
                index += 32

            # Download html
            html = self.dowload_content("http://money.finance.sina.com.cn/corp/go.php/vISSUE_ShareBonus/stockid/" + code + ".phtml")

            # EXD
            exdr_table = self.parse_html_table(html.decode("gbk"), "id", "sharebonus_1")
            exd = {}
            skip = 0
            for exd_row in exdr_table[0]:
                if skip < 3:
                    skip += 1
                    continue

                if exd_row[0] == "暂时没有数据！":
                    break

                if exd_row[4] == "实施":
                    exd[exd_row[5]] = {"song": exd_row[1], "zhuan": exd_row[2], "xi": exd_row[3]}

            # EXR
            exr_table = self.parse_html_table(html.decode("gbk"), "id", "sharebonus_2")
            exr = {}
            skip = 0
            for exr_row in exr_table[0]:
                if skip < 2:
                    skip += 1
                    continue

                if exr_row[0] == "暂时没有数据！":
                    break

                exr[exr_row[4]] = {"gu": exr_row[1], "jia": exr_row[2]}

            # EXDR
            exd_dates = set(exd.keys())
            exr_dates = set(exr.keys())
            exdr_dates = exd_dates.union(exr_dates)
            exdrs = {}
            for date in exdr_dates:
                (s, z, x, g, j) = (0, 0, 0, 0, 0)
                if date in exd:
                    s = exd[date]["song"]
                    z = exd[date]["zhuan"]
                    x = exd[date]["xi"]
                if date in exr:
                    g = exr[date]["gu"]
                    j = exr[date]["jia"]
                exdrs[date] = {"song": s, "zhuan": z, "xi": x, "gu": g, "jia": j}
            exdrs = collections.OrderedDict(reversed(sorted(exdrs.items())))

            exdr_trades = []
            for trade in raw_trades:
                (o, h, l, c) = self.get_exdr_price(type,
                                                   trade["datetime"],
                                                   (trade["open"], trade["high"], trade["low"], trade["close"]),
                                                   exdrs)
                exdr_trades.append({"datetime": trade["datetime"],
                                    "open_exdr": o,
                                    "high_exdr": h,
                                    "low_exdr": l,
                                    "close_exdr": c})

            is_first = True
            for trade in reversed(exdr_trades):
                if is_first:
                    (op, hp, lp, cp) = (0, 0, 0, 0)
                    preo = trade["open_exdr"]
                    preh = trade["high_exdr"]
                    prel = trade["low_exdr"]
                    prec = trade["close_exdr"]
                    is_first = False
                else:
                    op = 0 if preo == 0 else (trade["open_exdr"] - preo) / preo
                    hp = 0 if preh == 0 else (trade["high_exdr"] - preh) / preh
                    lp = 0 if prel == 0 else (trade["low_exdr"] - prel) / prel
                    cp = 0 if prec == 0 else (trade["close_exdr"] - prec) / prec
                    preo = trade["open_exdr"]
                    preh = trade["high_exdr"]
                    prel = trade["low_exdr"]
                    prec = trade["close_exdr"]

            if len(raw_trades) != len(exdr_trades):
                raise ValueError("Raw trade length and EXDR trade length are mismatch")

            for index, trade in enumerate(raw_trades):
                param = []
                param.append(code)
                param.append(trade["datetime"])
                param.append(trade["open"])
                param.append(trade["high"])
                param.append(trade["low"])
                param.append(trade["close"])
                param.append(exdr_trades[index]["open_exdr"])
                param.append(exdr_trades[index]["high_exdr"])
                param.append(exdr_trades[index]["low_exdr"])
                param.append(exdr_trades[index]["close_exdr"])
                param.append(trade["volume"])
                param.append(trade["amount"])
                param.append(code)
                param.append(trade["datetime"])
                w_cursor.execute("""INSERT INTO stock_trade VALUES
                                 (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ON DUPLICATE KEY UPDATE
                                 code=%s,datetime=%s;""", tuple(param))
                w_connect.commit()

            count += 1

        w_cursor.close()
        w_connect.close()

        self.aq.log('Stop')

    def create_path(self, path):
        if os.path.isdir(path) == False:
            os.mkdir(path)

    def download_file(self, url, file):
        attempts = 3
        while attempts >= 0:
            try:
                urllib.request.urlretrieve(url, file)
                break
            except urllib.error.URLError:
                attempts -= 1

    def dowload_content(self, url):
        attempts = 3
        while attempts >= 0:
            try:
                content = urllib.request.urlopen(url).read()
                break
            except urllib.error.URLError:
                attempts -= 1
        return content

    def unzip_file(self, path, file):
        zipfile.ZipFile(file).extractall(path)

    def parse_html_table(self, html, name, value):
        htp = HTMLTableParser(name, value)
        htp.feed(html)
        htp.close()
        return htp.getTables()

    def get_exdr_price(self, type, date, price, exdrs):
        (o, h, l, c) = (price[0], price[1], price[2], price[3])

        if (type != 'stock'):
            return (o, h, l, c)

        for key in exdrs:
            if (key == "--"):
                break
            exdrDate = time.strptime(key, "%Y-%m-%d")
            if (date < exdrDate):
                s = float(exdrs[key]["song"])/10
                z = float(exdrs[key]["zhuan"])/10
                x = float(exdrs[key]["xi"])/10
                g = float(exdrs[key]["gu"])/10
                j = float(exdrs[key]["jia"])
                o = ((o-x) + j*g)/(1.0 + s + z + g);
                h = ((h-x) + j*g)/(1.0 + s + z + g);
                l = ((l-x) + j*g)/(1.0 + s + z + g);
                c = ((c-x) + j*g)/(1.0 + s + z + g);
            else:
                break
        return (o, h, l, c)

    def get_exchange(self, id, type):
        if type == "index":
            if re.compile("^00").match(id) or re.compile("^99").match(id):
                return "sh"
            elif re.compile("^39").match(id):
                return "sz"
            else:
                raise ValueError("index id isn't correct - " + id)
        elif type == "etf":
            if re.compile("^51").match(id):
                return "sh"
            elif re.compile("^15").match(id):
                return "sz"
            else:
                raise ValueError("etf id isn't correct - " + id)
        elif type == "stock":
            if re.compile("^60").match(id):
                return "sh"
            elif re.compile("^00").match(id) or re.compile("^30").match(id):
                return "sz"
            else:
                raise ValueError("stock id isn't correct - " + id)
        else:
            raise ValueError("type isn't correct - " + type)

class HTMLTableParser(HTMLParser):
    def __init__(self, name = None, value = None):
        HTMLParser.__init__(self)
        self._data_separator = ' '
        self._name = name
        self._value = value
        self._in_table = False
        self._in_td = False
        self._in_th = False
        self._current_table = []
        self._current_row = []
        self._current_cell = []
        self.tables = []

    def getTables(self):
        return self.tables

    def handle_starttag(self, tag, attrs):
        if tag == 'table':
            if self._name != None and self._value != None:
                for (name, value) in attrs:
                    if name == self._name and value == self._value:
                        self._in_table = True
                        break
            else:
                self._in_table = True

        if tag == 'td':
            if self._in_table == True:
                self._in_td = True
        if tag == 'th':
            if self._in_table == True:
                self._in_th = True

    def handle_data(self, data):
        if self._in_td or self._in_th:
            self._current_cell.append(data.strip())

    def handle_endtag(self, tag):
        if self._in_table:
            if tag in ['td', 'th']:
                final_cell = self._data_separator.join(self._current_cell).strip()
                self._current_row.append(final_cell)
                self._current_cell = []
            elif tag == 'tr':
                self._current_table.append(self._current_row)
                self._current_row = []
            elif tag == 'table':
                self.tables.append(self._current_table)
                self._current_table = []

        if tag == 'td':
            self._in_td = False
        elif tag == 'th':
            self._in_th = False
        elif tag == 'table':
            self._in_table = False
