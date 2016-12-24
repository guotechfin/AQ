#include "ThostFtdcMdApi.h"
#include "CTPSpi.h"

void main(void)
{
	char front[256];
	TThostFtdcBrokerIDType brokerID;
	TThostFtdcUserIDType userID;
	TThostFtdcPasswordType passwd;

	std::ifstream in("./CTPMain.conf");
	std::string line;
	if (in) {
		getline(in, line);
		strcpy_s(front, line.c_str());
		getline(in, line);
		strcpy_s(brokerID, line.c_str());
		getline(in, line);
		strcpy_s(userID, line.c_str());
		getline(in, line);
		strcpy_s(passwd, line.c_str());
	} else {
		std::cout << "No Config File" << std::endl;
	}

	CThostFtdcMdApi *pMdApi = CThostFtdcMdApi::CreateFtdcMdApi();
	MdSpi *pMdSpi = new MdSpi(pMdApi, brokerID, userID, passwd);
	pMdApi->RegisterSpi(pMdSpi);
	pMdApi->RegisterFront(front);
	pMdApi->Init();
	pMdApi->Join();
	pMdApi->Release();
	delete pMdSpi;
}