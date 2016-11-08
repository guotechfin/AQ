library(RMySQL)
library(xts)

rm(list=ls())

code = "P"
type = "5"

connect <- dbConnect(MySQL(), host="127.0.0.1", port=3306, dbname = "aq", username="root", password="!QAZ2wsx#EDC")
d <- dbGetQuery(connect, paste0("SELECT datetime, open, high, low, close, volume, oi FROM future_trade WHERE code='", code, "' AND type='", type, "'"))
d$datetime <- as.POSIXlt(d$datetime)
d <- xts(d[,-1], order.by=d[,1])
dbDisconnect(connect)