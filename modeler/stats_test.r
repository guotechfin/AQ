library(RMySQL)
library(xts)
library(tseries)

rm(list=ls())

################################################################################

connect <- dbConnect(MySQL(), host="127.0.0.1", port=3306, dbname = "aq", username="root", password="!QAZ2wsx#EDC")
codes <- dbGetQuery(connect, paste0("SELECT code FROM future_code"))

################################################################################

print("Augmented Dickey¨CFuller Test")
for (code in codes$code) {
  data <- dbGetQuery(connect, paste0("SELECT datetime, open, high, low, close, volume, oi FROM future_trade WHERE code='", code, "' AND type=1"))
  data$datetime <- as.POSIXlt(data$datetime)
  data$rtn <- c(0, diff(data$c))/data$c
  data <- xts(data[,-1], order.by=data[,1])
  test <- adf.test(data$close)
  if (test$p.value < 0.02) {
    print(paste0(code, ": ", test$p.value))
  }
}

################################################################################

dbDisconnect(connect)

################################################################################