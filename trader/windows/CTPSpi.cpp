#include "CTPSpi.h"

MdSpi::MdSpi(CThostFtdcMdApi *pMdApi, TThostFtdcBrokerIDType brokerID, TThostFtdcUserIDType userID, TThostFtdcPasswordType passwd)
{
	this->pMdApi = pMdApi;
	strcpy_s(this->brokerID, brokerID);
	strcpy_s(this->userID, userID);
	strcpy_s(this->passwd, passwd);
}

void MdSpi::OnFrontConnected()
{
	CThostFtdcReqUserLoginField req;
	memset(&req, 0, sizeof(req));
	strcpy_s(req.BrokerID, brokerID);
	strcpy_s(req.UserID, userID);
	strcpy_s(req.Password, passwd);
	int iResult = pMdApi->ReqUserLogin(&req, ++requestID);
}

void MdSpi::OnFrontDisconnected(int nReason)
{
	std::cout << __FUNCTION__ << std::endl;
}

char *ppInstrumentID[] = { "ni1705", "pb1702" };
int iInstrumentID = 2;

void MdSpi::OnHeartBeatWarning(int nTimeLapse)
{
	std::cout << __FUNCTION__ << std::endl;
}

void MdSpi::OnRspUserLogin(CThostFtdcRspUserLoginField * pRspUserLogin, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	if (bIsLast && ((pRspInfo != NULL) && (pRspInfo->ErrorID == 0))) {
		std::cout << "--->>> 获取当前交易日 = " << pMdApi->GetTradingDay() << std::endl;
		int iResult = pMdApi->SubscribeMarketData(ppInstrumentID, iInstrumentID);
	}
}

void MdSpi::OnRspUserLogout(CThostFtdcUserLogoutField * pUserLogout, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << __FUNCTION__ << std::endl;
}

void MdSpi::OnRspSubMarketData(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	// 合约代码
	std::cout << "InstrumentID: " << pSpecificInstrument->InstrumentID << std::endl;

	// 合约代码
	std::cout << "InstrumentID: " << pSpecificInstrument->InstrumentID << std::endl;

	if (pRspInfo->ErrorID != 0) {
		// 错误代码
		std::cout << "ErrorID: " << pRspInfo->ErrorID << std::endl;
		///错误信息
		std::cout << "ErrorMsg: " << pRspInfo->ErrorMsg << std::endl;
	}

	std::cout << "nRequestID: " << nRequestID << std::endl;
	std::cout << "bIsLast: " << bIsLast << std::endl;
}

void MdSpi::OnRspUnSubMarketData(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	// 合约代码
	std::cout << "InstrumentID: " << pSpecificInstrument->InstrumentID << std::endl;

	if (pRspInfo->ErrorID != 0) {
		// 错误代码
		std::cout << "ErrorID: " << pRspInfo->ErrorID << std::endl;
		///错误信息
		std::cout << "ErrorMsg: " << pRspInfo->ErrorMsg << std::endl;
	}

	std::cout << "nRequestID: " << nRequestID << std::endl;
	std::cout << "bIsLast: " << bIsLast << std::endl;
}

void MdSpi::OnRspSubForQuoteRsp(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << __FUNCTION__ << std::endl;
}

void MdSpi::OnRspUnSubForQuoteRsp(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << __FUNCTION__ << std::endl;
}

void MdSpi::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField * pDepthMarketData)
{
	std::cout << "============================================================" << std::endl;
	//交易日	
	std::cout << "TradingDay: " << pDepthMarketData->TradingDay << std::endl;
	//合约代码
	std::cout << "InstrumentID: " << pDepthMarketData->InstrumentID << std::endl;
	//交易所代码	
	std::cout << "ExchangeID: " << pDepthMarketData->ExchangeID << std::endl;
	//合约在交易所的代码	
	std::cout << "ExchangeInstID: " << pDepthMarketData->ExchangeInstID << std::endl;
	//最新价
	std::cout << "LastPrice: " << pDepthMarketData->LastPrice << std::endl;
	//上次结算价
	std::cout << "PreSettlementPrice: " << pDepthMarketData->PreSettlementPrice << std::endl;
	//昨收盘
	std::cout << "PreClosePrice: " << pDepthMarketData->PreClosePrice << std::endl;
	//昨持仓量
	std::cout << "PreOpenInterest: " << pDepthMarketData->PreOpenInterest << std::endl;
	//今开盘
	std::cout << "OpenPrice: " << pDepthMarketData->OpenPrice << std::endl;
	//最高价
	std::cout << "HighestPrice: " << pDepthMarketData->HighestPrice << std::endl;
	//最低价
	std::cout << "LowestPrice: " << pDepthMarketData->LowestPrice << std::endl;
	//数量
	std::cout << "Volume: " << pDepthMarketData->Volume << std::endl;
	//成交金额	
	std::cout << "Turnover: " << pDepthMarketData->Turnover << std::endl;
	//持仓量	
	std::cout << "OpenInterest: " << pDepthMarketData->OpenInterest << std::endl;
	//今收盘
	std::cout << "ClosePrice: " << pDepthMarketData->ClosePrice << std::endl;
	//本次结算价
	std::cout << "SettlementPrice: " << pDepthMarketData->SettlementPrice << std::endl;
	//涨停板价
	std::cout << "UpperLimitPrice: " << pDepthMarketData->UpperLimitPrice << std::endl;
	//跌停板价
	std::cout << "LowerLimitPrice: " << pDepthMarketData->LowerLimitPrice << std::endl;
	//昨虚实度
	std::cout << "PreDelta: " << pDepthMarketData->PreDelta << std::endl;
	//今虚实度
	std::cout << "CurrDelta: " << pDepthMarketData->CurrDelta << std::endl;
	//最后修改时间
	std::cout << "UpdateTime: " << pDepthMarketData->UpdateTime << std::endl;
	//最后修改毫秒
	std::cout << "UpdateMillisec: " << pDepthMarketData->UpdateMillisec << std::endl;
	//申买价一	
	std::cout << "BidPrice1: " << pDepthMarketData->BidPrice1 << std::endl;
	//申买量一
	std::cout << "BidVolume1: " << pDepthMarketData->BidVolume1 << std::endl;
	//申卖价一
	std::cout << "AskPrice1: " << pDepthMarketData->AskPrice1 << std::endl;
	//申卖量一
	std::cout << "AskVolume1: " << pDepthMarketData->AskVolume1 << std::endl;
	//当日均价
	std::cout << "AveragePrice: " << pDepthMarketData->AveragePrice << std::endl;
	//业务日期
	std::cout << "ActionDay: " << pDepthMarketData->ActionDay << std::endl;
}

void MdSpi::OnRtnForQuoteRsp(CThostFtdcForQuoteRspField * pForQuoteRsp)
{
	//交易日
	std::cout << "TradingDay" << pForQuoteRsp->TradingDay << std::endl;
	//合约代码
	std::cout << "InstrumentID" << pForQuoteRsp->InstrumentID << std::endl;	
	//询价编号
	std::cout << "ForQuoteSysID" << pForQuoteRsp->ForQuoteSysID << std::endl;
	//询价时间
	std::cout << "ForQuoteTime" << pForQuoteRsp->ForQuoteTime << std::endl;
	//业务日期
	std::cout << "ActionDay" << pForQuoteRsp->ActionDay << std::endl;
	//交易所代码
	std::cout << "ExchangeID" << pForQuoteRsp->ExchangeID << std::endl;
}

void MdSpi::OnRspError(CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << "Error ID - " << pRspInfo->ErrorID << std::endl;
	std::cout << "Error Msg - " << pRspInfo->ErrorMsg << std::endl;
}

