library(RMySQL)
library(xts)

rm(list=ls())

connect <- dbConnect(MySQL(), host="127.0.0.1", port=3306, dbname = "aq", username="root", password="!QAZ2wsx#EDC")

code = "P"
type = "5"
data <- dbGetQuery(connect, paste0("SELECT datetime, open, high, low, close, volume, oi FROM future_trade WHERE code='", code, "' AND type='", type, "'"))
data$datetime <- as.POSIXlt(data$datetime)
data <- xts(data[,-1], order.by=data[,1])

dbDisconnect(connect)