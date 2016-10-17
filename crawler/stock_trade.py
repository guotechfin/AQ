#!/usr/bin/env python3
# -*- coding: utf-8 -*-

class StockTrade:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log.info('AQ/Crawler/StockTrade Start')

        self.aq.log.info('AQ/Crawler/StockTrade Stop')

    def run(self):
        path = self.config.getValue("dataPath")

        if (self.config.getValue("dataDownload")):
            # Download and unzip Shanghai trade data
            url = self.config.getValue("dataSHTradeLink")
            file = path + os.sep + self.config.getValue("dataSHTradeFile")
            Util().downloadFile(url, file)
            Util().unzipFile(path, file)

            # Download and unzip Shenzhen trade data
            url = self.config.getValue("dataSZTradeLink")
            file = path + os.sep + self.config.getValue("dataSZTradeFile")
            Util().downloadFile(url, file)
            Util().unzipFile(path, file)

        # Initialize table
        wConnect = connector.connect(user=self.gconfig.getValue("dbUsr"), password=self.gconfig.getValue("dbPwd"), host=self.gconfig.getValue("dbHost"), database=self.gconfig.getValue("dbDatabase"))
        wCursor = wConnect.cursor()
        if (self.config.getValue("dbInit")):
            wCursor.execute(self.config.getValue("dbInitTableDrop"))
        wCursor.execute(self.config.getValue("dbInitTableCreate"))
        wCursor.execute(self.config.getValue("dbInitTableStruct"))
        wConnect.commit()

        rConnect = connector.connect(user=self.gconfig.getValue("dbUsr"), password=self.gconfig.getValue("dbPwd"), host=self.gconfig.getValue("dbHost"), database=self.gconfig.getValue("dbDatabase"))
        rCursor = rConnect.cursor()
        rCursor.execute(self.config.getValue("dbReadID"))
        results = []
        for (id, type, name) in rCursor:
            results.append({"id":id, "type":type, "name":name})
        rCursor.close()
        rConnect.close()

        count = 0
        for result in results:
            id = result["id"]
            type = result["type"]
            name = result["name"]

            self.log.printInfo("Trade Start " + id + " " + name)
            # Load trade data
            dayFile = open(self.config.getValue("dataPath") + os.sep + self.getExchange(id, type) + id + ".day", "rb").read()
            length = len(dayFile)
            index = 0
            rawTrades = []
            while index < length:
                d = time.strptime(str(int.from_bytes(dayFile[index:index+4], byteorder='little')), "%Y%m%d")
                if (type == "etf"):
                    o = int.from_bytes(dayFile[index+4:index+8], byteorder='little')/1000.00
                    h = int.from_bytes(dayFile[index+8:index+12], byteorder='little')/1000.00
                    l = int.from_bytes(dayFile[index+12:index+16], byteorder='little')/1000.00
                    c = int.from_bytes(dayFile[index+16:index+20], byteorder='little')/1000.00
                else:
                    o = int.from_bytes(dayFile[index+4:index+8], byteorder='little')/100.00
                    h = int.from_bytes(dayFile[index+8:index+12], byteorder='little')/100.00
                    l = int.from_bytes(dayFile[index+12:index+16], byteorder='little')/100.00
                    c = int.from_bytes(dayFile[index+16:index+20], byteorder='little')/100.00
                a = int.from_bytes(dayFile[index+20:index+24], byteorder='little')
                v = int.from_bytes(dayFile[index+24:index+28], byteorder='little')
                rawTrades = [{ "date":d, "open":o, "high":h, "low":l, "close":c, "amount":a, "volume":v }] + rawTrades
                index += 32

            # Download html
            html = Util().dowloadFileContent(self.config.getValue("dataEXDRPref") + id + self.config.getValue("dataEXDRSuff"))

            # EXD
            exdTable = Util().parseHTMLTable(html.decode("gbk"), "id", self.config.getValue("dataEXDTableID"))
            exd = {}
            skip = 0
            for exdRow in exdTable[0]:
                if skip < 3:
                    skip += 1
                    continue

                if exdRow[0] == self.config.getValue("dataEXDRTableSkip"):
                    break

                if exdRow[4] == self.config.getValue("dataEXDTableValid"):
                    exd[exdRow[5]] = {"song":exdRow[1], "zhuan":exdRow[2], "xi":exdRow[3]}

            #EXR
            exrTable = Util().parseHTMLTable(html.decode("gbk"), "id", self.config.getValue("dataEXRTableID"))
            exr = {}
            skip = 0
            for exrRow in exrTable[0]:
                if skip < 2:
                    skip += 1
                    continue

                if exrRow[0] == self.config.getValue("dataEXDRTableSkip"):
                    break

                exr[exrRow[4]] = {"gu":exrRow[1], "jia":exrRow[2]}

            # EXDR
            exdDates = set(exd.keys())
            exrDates = set(exr.keys())
            exdrDates = exdDates.union(exrDates)
            exdrs = {}
            for date in exdrDates:
                (s, z, x, g, j) = (0, 0, 0, 0, 0)
                if date in exd:
                    s = exd[date]["song"]
                    z = exd[date]["zhuan"]
                    x = exd[date]["xi"]
                if date in exr:
                    g = exr[date]["gu"]
                    j = exr[date]["jia"]
                exdrs[date] = {"song":s, "zhuan":z, "xi":x, "gu":g, "jia":j}
            exdrs = collections.OrderedDict(reversed(sorted(exdrs.items())))

            exdrTrades = []
            for trade in rawTrades:
                (o, h, l, c) = self.getEXDRPrice(type, trade["date"], (trade["open"], trade["high"], trade["low"], trade["close"]), exdrs)
                exdrTrades.append({ "date":trade["date"], "exdr_open":o, "exdr_high":h, "exdr_low":l, "exdr_close":c })

            exdrPercent = []
            isFirst = True
            for trade in reversed(exdrTrades):
                if isFirst:
                    (op, hp, lp, cp) = (0, 0, 0, 0)
                    preo = trade["exdr_open"]
                    preh = trade["exdr_high"]
                    prel = trade["exdr_low"]
                    prec = trade["exdr_close"]
                    exdrPercent = [{ "date":d, "exdr_open_percent":op, "exdr_high_percent":hp, "exdr_low_percent":lp, "exdr_close_percent":cp }] + exdrPercent
                    isFirst = False
                else:
                    op = 0 if preo == 0 else (trade["exdr_open"]-preo)/preo
                    hp = 0 if preh == 0 else (trade["exdr_high"]-preh)/preh
                    lp = 0 if prel == 0 else (trade["exdr_low"]-prel)/prel
                    cp = 0 if prec == 0 else (trade["exdr_close"]-prec)/prec
                    preo = trade["exdr_open"]
                    preh = trade["exdr_high"]
                    prel = trade["exdr_low"]
                    prec = trade["exdr_close"]
                    exdrPercent = [{ "date":d, "exdr_open_percent":op, "exdr_high_percent":hp, "exdr_low_percent":lp, "exdr_close_percent":cp }] + exdrPercent

            if len(rawTrades) != len(exdrTrades):
                raise ValueError("Raw trade length and EXDR trade length are mismatch")

            if len(rawTrades) != len(exdrPercent):
                raise ValueError("Raw trade length and EXDR percent length are mismatch")

            for index, trade in enumerate(rawTrades):
                param = []
                param.append(id)
                param.append(trade["date"])
                param.append(trade["open"])
                param.append(trade["high"])
                param.append(trade["low"])
                param.append(trade["close"])
                param.append(trade["volume"])
                param.append(trade["amount"])
                param.append(exdrTrades[index]["exdr_open"])
                param.append(exdrTrades[index]["exdr_high"])
                param.append(exdrTrades[index]["exdr_low"])
                param.append(exdrTrades[index]["exdr_close"])
                param.append(exdrPercent[index]["exdr_open_percent"])
                param.append(exdrPercent[index]["exdr_high_percent"])
                param.append(exdrPercent[index]["exdr_low_percent"])
                param.append(exdrPercent[index]["exdr_close_percent"])
                param.append(id)
                param.append(trade["date"])
                wCursor.execute(self.config.getValue("dbWrite"), tuple(param))
                wConnect.commit()

            count += 1
            self.log.printInfo("Trade Stop " + id + " " + name + " (Count=" + str(count) + ")")

        wCursor.close()
        wConnect.close()


    def getEXDRPrice(self, type, date, price, exdrs):
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

    def getExchange(self, id, type):
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