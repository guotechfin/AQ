#include "ThostFtdcMdApi.h"
#include "CTPMd.h"

void main(void)
{
	// 初始化UserApi
	CThostFtdcMdAPI mdApi = CThostFtdcMdApi::CreateFtdcMdApi();
	CTPMdSpi* mdSpi = new CMdSpi();
	pUserApi->RegisterSpi(pUserSpi);						// 注册事件类
	pUserApi->RegisterFront(FRONT_ADDR);					// connect
	pUserApi->Init();
	pUserApi->Join();
	//	pUserApi->Release();
}