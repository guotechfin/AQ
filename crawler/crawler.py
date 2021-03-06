#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from crawler.future_code import FutureCode
from crawler.future_trade import FutureTrade
from crawler.stock_code import StockCode
from crawler.stock_trade import StockTrade

class Crawler:

    def __init__(self, aq):
        self.aq = aq

    def execute(self):
        self.aq.log("Start")
        FutureCode(self.aq).execute()
        FutureTrade(self.aq).execute()
        StockCode(self.aq).execute()
        StockTrade(self.aq).execute()
        self.aq.log("Stop")
