"""
조회한 날의 종목에 대한 정보를 가져옴

1) 종목코드
2) 종목명
3) PER
4) PBR
5) ROE
6) 시가총액
7) 상장주식
8) 유통주식
9) 유통비율
10) 외인소진률
"""
import os
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.folder import make_folder


base_path = os.path.dirname(os.path.abspath('..'))
data_path = os.path.join(base_path, 'data')
stock_path = os.path.join(data_path, 'stock')
folder_path = os.path.join(stock_path, 'folder')
info_path = os.path.join(folder_path, '종목별상세정보_20190323')

make_folder(base_path, data_path, stock_path, folder_path, info_path)


class Kiwoom(QAxWidget):
    """
    ActiveX 컨트롤을 하는 Qt CLASS

    """
    def __init__(self):
        super().__init__()
        self._create_kiwoom_instance()
        self._set_signal_slots()

    def _create_kiwoom_instance(self):
        """
        키움증권의 OpenAPI+를 사용하려면 먼저 COM 오브젝트를 생성해야 합니다.
        COM 오브젝트를 생성하려면 "KHOPENAPI.KHOpenAPICtrl.1"이라는
        ProgID를 QAxWidget 클래스의 생성자로 전달하거나 setControl 메서드를 사용하면 됩니다.
        :return:
        """
        self.setControl("KHOPENAPI.KHOpenAPICtrl.1")

    def _set_signal_slots(self):
        """
        Event 발생 시 연결 메소드

        :return:
        """
        self.OnEventConnect.connect(self._event_connect)
        self.OnReceiveTrData.connect(self._receive_tr_data)

    def comm_connect(self):
        """
        로그인

        :return:
        """
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

    def comm_terminate(self):
        """
        종료

        :return:
        """
        self.dynamicCall("CommTerminate()")

    def _event_connect(self, err_code):
        """
        LOGIN 이벤트 처리 메소드

        :param err_code:
        :return:
        """
        if err_code == 0:
            print("connected")
        else:
            print("disconnected")

        self.login_event_loop.exit()

    def get_code_list_by_market(self, market):
        """
        전체 코드 받아오는 메소드

        :param market:
        :return:
        """
        code_list = self.dynamicCall("GetCodeListByMarket(QString)", market)
        code_list = code_list.split(';')
        return code_list[:-1]

    def get_master_code_name(self, code):
        """
        종목 코드의 한글명을 반환하는 메서드

        :param code:
        :return:
        """
        code_name = self.dynamicCall("GetMasterCodeName(QString)", code)
        return code_name

    def get_connect_state(self):
        """
        현재 접속 상태를 반환한다.

        :return:
        """
        ret = self.dynamicCall("GetConnectState()")
        return ret

    def set_input_value(self, id, value):
        """
        TRAN 입력 값을 서버통신 전에 입력한다.

        :param id:
        :param value:
        :return:
        """
        self.dynamicCall("SetInputValue(QString, QString)", id, value)

    def comm_rq_data(self, rqname, trcode, next, screen_no):
        """
        TR 값을 요청한다.

        :param rqname:
        :param trcode:
        :param next:
        :param screen_no:
        :return:
        """
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _get_comm_data(self, code, field_name, index, item_name):
        """
        수신 데이터를 반환한다.

        :param code:
        :param real_type:
        :param field_name:
        :param index:
        :param item_name:
        :return:
        """
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)",
                               code, field_name, index, item_name)
        return ret.strip()

    def _get_repeat_cnt(self, trcode, rqname):
        """
        수신 받은 데이터 반복 개수를 반환한다.

        :param trcode:
        :param rqname:
        :return:
        """
        ret = self.dynamicCall("GetRepeatCnt(QString, QString)", trcode, rqname)
        return ret

    def _receive_tr_data(self, screen_no, rqname, trcode, record_name, next, unused1, unused2, unused3, unused4):
        """
        서버 통신 후 데이터를 받은 시점을 알려준다.

        :param screen_no:
        :param rqname:
        :param trcode:
        :param record_name:
        :param next:
        :param unused1:
        :param unused2:
        :param unused3:
        :param unused4:
        :return:
        """
        if rqname == "opt10001_req":
            self._opt10001(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt10001(self, rqname, trcode):
        """
        요청한 데이터를 반환한다.

        :param rqname:
        :param trcode:
        :return:
        """
        code = self._get_comm_data(trcode, rqname, 0, "종목코드")
        name = self._get_comm_data(trcode, rqname, 0, "종목명")
        per = self._get_comm_data(trcode, rqname, 0, "PER")
        pbr = self._get_comm_data(trcode, rqname, 0, "PBR")
        eps = self._get_comm_data(trcode, rqname, 0, "EPS")
        roe = self._get_comm_data(trcode, rqname, 0, "ROE")
        price = self._get_comm_data(trcode, rqname, 0, "시가총액")
        market = self._get_comm_data(trcode, rqname, 0, "상장주식")
        flow = self._get_comm_data(trcode, rqname, 0, "유통주식")
        flow_ratio = self._get_comm_data(trcode, rqname, 0, "유통비율")
        foreigner = self._get_comm_data(trcode, rqname, 0, "외인소진률")

        self.ohlcv['code'].append(code)
        self.ohlcv['name'].append(name)
        self.ohlcv['per'].append(per)
        self.ohlcv['pbr'].append(pbr)
        self.ohlcv['eps'].append(eps)
        self.ohlcv['roe'].append(roe)
        self.ohlcv['price'].append(price)
        self.ohlcv['market'].append(market)
        self.ohlcv['flow'].append(flow)
        self.ohlcv['flow_ratio'].append(flow_ratio)
        self.ohlcv['foreigner'].append(foreigner)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    kiwoom = Kiwoom()
    kiwoom.comm_connect()
    code_name_df = pd.read_csv(os.path.join(folder_path, 'code_name_list.csv'), index_col=0)
    code_list = code_name_df['code'].values

    for i in range(2000, len(code_list), 100):

        kiwoom.ohlcv = {'code': [],
                        'name': [],
                        'per': [],
                        'pbr': [],
                        'eps': [],
                        'roe': [],
                        'price': [],
                        'current': [],
                        'amount': [],
                        'credit': [],
                        'market': [],
                        'flow': [],
                        'flow_ratio': [],
                        'foreigner': []}

        code_list_sub = code_list[i:i+100]

        for j, code in enumerate(code_list_sub):
            if j % 10 == 0:
                print(j, code)
            time.sleep(1)
            kiwoom.set_input_value("종목코드", code)
            kiwoom.comm_rq_data("opt10001_req", "opt10001", 0, "0101")

        df = pd.DataFrame(kiwoom.ohlcv, columns=['code',
                                                 'name',
                                                 'per',
                                                 'pbr',
                                                 'roe',
                                                 'eps',
                                                 'price',
                                                 'market',
                                                 'flow',
                                                 'flow_ratio',
                                                 'foreigner'])
        df.to_csv(os.path.join(info_path, 'opt10001_' + str(i) + '.csv'), index=False)
