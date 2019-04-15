import sys
from PyQt5.QtWidgets import *
from PyQt5.QAxContainer import *
from PyQt5.QtCore import *
import time
import pandas as pd
import sqlite3

TR_REQ_TIME_INTERVAL = 0.2


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

        # 로그인 시 발생하는 이벤트
        self.OnEventConnect.connect(self._event_connect)

        # TR을 받았을 때 발생하는 이벤트
        self.OnReceiveTrData.connect(self._receive_tr_data)

        # 주문이 발생할 떄 발생하는 이벤트
        self.OnReceiveChejanData.connect(self._receive_chejan_data)

    def comm_connect(self):
        """
        로그인

        :return:
        """
        self.dynamicCall("CommConnect()")
        self.login_event_loop = QEventLoop()
        self.login_event_loop.exec_()

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
        TRAN 값을 서버로 전송한다.

        :param rqname:
        :param trcode:
        :param next:
        :param screen_no:
        :return:
        """
        self.dynamicCall("CommRqData(QString, QString, int, QString)", rqname, trcode, next, screen_no)
        self.tr_event_loop = QEventLoop()
        self.tr_event_loop.exec_()

    def _get_comm_data(self, code, real_type, field_name, index, item_name):
        """
        수신 데이터를 반환한다.

        :param code:
        :param real_type:
        :param field_name:
        :param index:
        :param item_name:
        :return:
        """
        ret = self.dynamicCall("GetCommData(QString, QString, int, QString)", code,
                               real_type, field_name, index, item_name)
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
        if next == '2':
            self.remained_data = True
        else:
            self.remained_data = False

        if rqname == "opt10081_req":
            self._opt10081(rqname, trcode)

        try:
            self.tr_event_loop.exit()
        except AttributeError:
            pass

    def _opt10081(self, rqname, trcode):
        """
        요청한 데이터를 반환한다.

        :param rqname:
        :param trcode:
        :return:
        """
        data_cnt = self._get_repeat_cnt(trcode, rqname)

        for i in range(data_cnt):
            date = self._get_comm_data(trcode, rqname, i, "일자")
            open = self._get_comm_data(trcode, rqname, i, "시가")
            high = self._get_comm_data(trcode, rqname, i, "고가")
            low = self._get_comm_data(trcode, rqname, i, "저가")
            close = self._get_comm_data(trcode, rqname, i, "현재가")
            volume = self._get_comm_data(trcode, rqname, i, "거래량")

            self.ohlcv['date'].append(date)
            self.ohlcv['open'].append(int(open))
            self.ohlcv['high'].append(int(high))
            self.ohlcv['low'].append(int(low))
            self.ohlcv['close'].append(int(close))
            self.ohlcv['volume'].append(int(volume))

    def send_order(self, rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no):
        """
        주식 주문 정보를 서버로 전송

        :param rqname:
        :param screen_no:
        :param acc_no:
        :param order_type:
        :param code:
        :param quantity:
        :param price:
        :param hoga:
        :param order_no:
        :return:
        """
        self.dynamicCall("SendOrder(QString, QString, QString, int, QString, int, int, QString, QString)",
                         [rqname, screen_no, acc_no, order_type, code, quantity, price, hoga, order_no])

    def get_chejan_data(self, fid):
        """
        주문이 완료되고 나서 체결 잔고를 요청

        :param fid:
        :return:
        """
        ret = self.dynamicCall("GetChejanData(int)", fid)
        return ret

    def _receive_chejan_data(self, gubun, item_cnt, fid_list):
        """
        OnRecieveChejanData 이벤트 발생 시 이벤트 처리 메서드

        :param gubun:
        :param item_cnt:
        :param fid_list:
        :return:
        """
        print(gubun)
        print(self.get_chejan_data(9203))
        print(self.get_chejan_data(302))
        print(self.get_chejan_data(900))
        print(self.get_chejan_data(901))

    def get_login_info(self, tag):
        """
        계좌 정보 및 로그인 사용자 정보를 얻어오는 메서드

        :param tag:
        :return:
        """
        ret = self.dynamicCall("GetLoginInfo(QString)", tag)
        return ret
