#include "ThostFtdcMdApi.h"
#include "CTPMd.h"

void main(void)
{
	// ��ʼ��UserApi
	CThostFtdcMdAPI mdApi = CThostFtdcMdApi::CreateFtdcMdApi();
	CTPMdSpi* mdSpi = new CMdSpi();
	pUserApi->RegisterSpi(pUserSpi);						// ע���¼���
	pUserApi->RegisterFront(FRONT_ADDR);					// connect
	pUserApi->Init();
	pUserApi->Join();
	//	pUserApi->Release();
}