library(RMySQL)
library(xts)
library("CADFtest")

pair1 = c("RB", "I")
pair2 = c("M", "RM")
pair3 = c("Y", "P")

################################################################################

rm(list=ls())
connect <- dbConnect(MySQL(), host="127.0.0.1", port=3306, dbname = "aq", username="root", password="!QAZ2wsx#EDC")
d <- dbGetQuery(connect, paste0("SELECT d1.datetime as dt, d1.close as d1_c, d2.close as d2_c FROM
                                 (SELECT code, datetime, close FROM future_trade WHERE code='Y' AND type='5') d1, 
                                 (SELECT code, datetime, close FROM future_trade WHERE code='P' AND type='5') d2 
                                 WHERE d1.datetime=d2.datetime"))
dbDisconnect(connect)

################################################################################
d$dt <- as.POSIXlt(d$dt)
d$d1_rtn <- c(0, diff(d$d1_c))/d$d1_c
d$d2_rtn <- c(0, diff(d$d2_c))/d$d2_c
d$d1_c <- NULL
d$d2_c <- NULL
d <- xts(d[,-1], order.by=d[,1])
plot(d, plot.type="single", lty=1:ncol(d))

cadftest <- CADFtest(c(d$d1_rtn, d$d2_rtn))
print(summary(cadftest))
################################################################################