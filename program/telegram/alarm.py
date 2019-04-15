import os
import sys
import time

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic

import telegram

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from Kiwoom import *


folder_path = os.path.abspath(os.path.dirname(__file__))
form_class = uic.loadUiType(os.path.join(folder_path, "alarm.ui"))[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.token = ""

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

        self.code = '093320'
        self.name = self.kiwoom.get_master_code_name(self.code)
        self.kiwoom.current = {}

        self.past_price = 0
        self.past_ratio = 0
        self.past_amount = 0

        # Timer1 - 1초에 한 번씩 이벤트가 발생한다.
        self.timer = QTimer(self)
        self.timer.start(1000 * 15)
        self.timer.timeout.connect(self.timeout_visualize)

        self.timer = QTimer(self)
        self.timer.start(1000 * 30)
        self.timer.timeout.connect(self.timeout_message)

    def request_data(self, code):
        """
        데이터 요청

        :param code:
        :return:
        """
        self.kiwoom.current = {}
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.comm_rq_data("opt10001_req", 'opt10001', 0, '2000')

    def timeout_visualize(self):
        """
        30초마다 서버로부터 가격, 상승률, 양을 가져온다.

        :return:
        """
        current_time = QTime.currentTime()

        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"

        self.statusbar.showMessage(state_msg + " | " + time_msg)

        self.request_data(self.code)
        self.lineEdit.setText(self.kiwoom.get_master_code_name(self.code))
        self.lineEdit_2.setText(self.kiwoom.current['price'])
        self.lineEdit_3.setText(self.kiwoom.current['ratio'])
        self.lineEdit_4.setText(self.kiwoom.current['amount'])

    def timeout_message(self):
        """
        60초마다 변경 사항이 있을 시 텔레그램 메세지를 보낸다.

        :return:
        """
        bot = telegram.Bot(token=self.token)
        chat_id = bot.getUpdates()[-1].message.chat.id

        price = self.kiwoom.current['price']
        ratio = self.kiwoom.current['ratio']
        amount = self.kiwoom.current['amount']

        if self.past_price != price:
            message = self.name + "\n" + \
                  "현재 가격: " + price + "\n" + \
                  "등락율: " + ratio + "%\n" + \
                  "거래량: " + amount + "\n"
            bot.sendMessage(chat_id=chat_id, text=message)

            self.past_price = price
            self.past_ratio = ratio
            self.past_amount = amount


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()



