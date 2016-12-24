#include "CTPMdSpi.h"
#include <iostream>

CTPMdSpi::CTPMdSpi(CThostFtdcMdApi * pMdApi)
{
	this->pMdApi = pMdApi;
}

void CTPMdSpi::OnFrontConnected()
{
	CThostFtdcReqUserLoginField req;	
	TThostFtdcUserIDType userId;
	TThostFtdcPasswordType passwd;

	memset(&req, 0, sizeof(req));
	strcpy_s(req.BrokerID, "8060");
	std::cout << "usr:"; 
	std::cin >> userId;
	std::cout << "pwd:";
	std::cin >> passwd;
	strcpy_s(req.UserID, userId);
	strcpy_s(req.Password, passwd);
	int iResult = pMdApi->ReqUserLogin(&req, ++requestID);
}

char *ppInstrumentID[] = { "ni1705", "pb1702" };
int iInstrumentID = 2;

void CTPMdSpi::OnHeartBeatWarning(int nTimeLapse)
{
}

void CTPMdSpi::OnRspUserLogin(CThostFtdcRspUserLoginField * pRspUserLogin, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{	
	if (bIsLast && ((pRspInfo!= NULL) && (pRspInfo->ErrorID == 0))) {
		std::cout << "--->>> 获取当前交易日 = " << pMdApi->GetTradingDay() << std::endl;
		int iResult = pMdApi->SubscribeMarketData(ppInstrumentID, iInstrumentID);
	}
}

void CTPMdSpi::OnRspUserLogout(CThostFtdcUserLogoutField * pUserLogout, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
}

void CTPMdSpi::OnRspSubMarketData(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << __FUNCTION__ << std::endl;
}

void CTPMdSpi::OnRspUnSubMarketData(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << __FUNCTION__ << std::endl;
}

void CTPMdSpi::OnRspSubForQuoteRsp(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
}

void CTPMdSpi::OnRspUnSubForQuoteRsp(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
}

void CTPMdSpi::OnRtnDepthMarketData(CThostFtdcDepthMarketDataField * pDepthMarketData)
{
	std::cout << __FUNCTION__ << std::endl;
}

void CTPMdSpi::OnRtnForQuoteRsp(CThostFtdcForQuoteRspField * pForQuoteRsp)
{
}

void CTPMdSpi::OnRspError(CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << __FUNCTION__ << std::endl;
}

void CTPMdSpi::OnFrontDisconnected(int nReason)
{
	std::cout << "Disconnected";
}