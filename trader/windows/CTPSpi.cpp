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
	std::cout << __FUNCTION__ << std::endl;
}

void MdSpi::OnRspUnSubMarketData(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << __FUNCTION__ << std::endl;
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
	std::cout << __FUNCTION__ << std::endl;
}

void MdSpi::OnRtnForQuoteRsp(CThostFtdcForQuoteRspField * pForQuoteRsp)
{
	std::cout << __FUNCTION__ << std::endl;
}

void MdSpi::OnRspError(CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << "Error ID - " << pRspInfo->ErrorID << std::endl;
	std::cout << "Error Msg - " << pRspInfo->ErrorMsg << std::endl;
}

