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
		std::cout << "--->>> ��ȡ��ǰ������ = " << pMdApi->GetTradingDay() << std::endl;
		int iResult = pMdApi->SubscribeMarketData(ppInstrumentID, iInstrumentID);
	}
}

void MdSpi::OnRspUserLogout(CThostFtdcUserLogoutField * pUserLogout, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << __FUNCTION__ << std::endl;
}

void MdSpi::OnRspSubMarketData(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	// ��Լ����
	std::cout << "InstrumentID: " << pSpecificInstrument->InstrumentID << std::endl;

	// ��Լ����
	std::cout << "InstrumentID: " << pSpecificInstrument->InstrumentID << std::endl;

	if (pRspInfo->ErrorID != 0) {
		// �������
		std::cout << "ErrorID: " << pRspInfo->ErrorID << std::endl;
		///������Ϣ
		std::cout << "ErrorMsg: " << pRspInfo->ErrorMsg << std::endl;
	}

	std::cout << "nRequestID: " << nRequestID << std::endl;
	std::cout << "bIsLast: " << bIsLast << std::endl;
}

void MdSpi::OnRspUnSubMarketData(CThostFtdcSpecificInstrumentField * pSpecificInstrument, CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	// ��Լ����
	std::cout << "InstrumentID: " << pSpecificInstrument->InstrumentID << std::endl;

	if (pRspInfo->ErrorID != 0) {
		// �������
		std::cout << "ErrorID: " << pRspInfo->ErrorID << std::endl;
		///������Ϣ
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
	//������	
	std::cout << "TradingDay: " << pDepthMarketData->TradingDay << std::endl;
	//��Լ����
	std::cout << "InstrumentID: " << pDepthMarketData->InstrumentID << std::endl;
	//����������	
	std::cout << "ExchangeID: " << pDepthMarketData->ExchangeID << std::endl;
	//��Լ�ڽ������Ĵ���	
	std::cout << "ExchangeInstID: " << pDepthMarketData->ExchangeInstID << std::endl;
	//���¼�
	std::cout << "LastPrice: " << pDepthMarketData->LastPrice << std::endl;
	//�ϴν����
	std::cout << "PreSettlementPrice: " << pDepthMarketData->PreSettlementPrice << std::endl;
	//������
	std::cout << "PreClosePrice: " << pDepthMarketData->PreClosePrice << std::endl;
	//��ֲ���
	std::cout << "PreOpenInterest: " << pDepthMarketData->PreOpenInterest << std::endl;
	//����
	std::cout << "OpenPrice: " << pDepthMarketData->OpenPrice << std::endl;
	//��߼�
	std::cout << "HighestPrice: " << pDepthMarketData->HighestPrice << std::endl;
	//��ͼ�
	std::cout << "LowestPrice: " << pDepthMarketData->LowestPrice << std::endl;
	//����
	std::cout << "Volume: " << pDepthMarketData->Volume << std::endl;
	//�ɽ����	
	std::cout << "Turnover: " << pDepthMarketData->Turnover << std::endl;
	//�ֲ���	
	std::cout << "OpenInterest: " << pDepthMarketData->OpenInterest << std::endl;
	//������
	std::cout << "ClosePrice: " << pDepthMarketData->ClosePrice << std::endl;
	//���ν����
	std::cout << "SettlementPrice: " << pDepthMarketData->SettlementPrice << std::endl;
	//��ͣ���
	std::cout << "UpperLimitPrice: " << pDepthMarketData->UpperLimitPrice << std::endl;
	//��ͣ���
	std::cout << "LowerLimitPrice: " << pDepthMarketData->LowerLimitPrice << std::endl;
	//����ʵ��
	std::cout << "PreDelta: " << pDepthMarketData->PreDelta << std::endl;
	//����ʵ��
	std::cout << "CurrDelta: " << pDepthMarketData->CurrDelta << std::endl;
	//����޸�ʱ��
	std::cout << "UpdateTime: " << pDepthMarketData->UpdateTime << std::endl;
	//����޸ĺ���
	std::cout << "UpdateMillisec: " << pDepthMarketData->UpdateMillisec << std::endl;
	//�����һ	
	std::cout << "BidPrice1: " << pDepthMarketData->BidPrice1 << std::endl;
	//������һ
	std::cout << "BidVolume1: " << pDepthMarketData->BidVolume1 << std::endl;
	//������һ
	std::cout << "AskPrice1: " << pDepthMarketData->AskPrice1 << std::endl;
	//������һ
	std::cout << "AskVolume1: " << pDepthMarketData->AskVolume1 << std::endl;
	//���վ���
	std::cout << "AveragePrice: " << pDepthMarketData->AveragePrice << std::endl;
	//ҵ������
	std::cout << "ActionDay: " << pDepthMarketData->ActionDay << std::endl;
}

void MdSpi::OnRtnForQuoteRsp(CThostFtdcForQuoteRspField * pForQuoteRsp)
{
	//������
	std::cout << "TradingDay" << pForQuoteRsp->TradingDay << std::endl;
	//��Լ����
	std::cout << "InstrumentID" << pForQuoteRsp->InstrumentID << std::endl;	
	//ѯ�۱��
	std::cout << "ForQuoteSysID" << pForQuoteRsp->ForQuoteSysID << std::endl;
	//ѯ��ʱ��
	std::cout << "ForQuoteTime" << pForQuoteRsp->ForQuoteTime << std::endl;
	//ҵ������
	std::cout << "ActionDay" << pForQuoteRsp->ActionDay << std::endl;
	//����������
	std::cout << "ExchangeID" << pForQuoteRsp->ExchangeID << std::endl;
}

void MdSpi::OnRspError(CThostFtdcRspInfoField * pRspInfo, int nRequestID, bool bIsLast)
{
	std::cout << "Error ID - " << pRspInfo->ErrorID << std::endl;
	std::cout << "Error Msg - " << pRspInfo->ErrorMsg << std::endl;
}

