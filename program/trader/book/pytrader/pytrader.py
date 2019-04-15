import time
import sys

from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5 import uic
from Kiwoom import *

form_class = uic.loadUiType("pytrader_v4_smaller.ui")[0]


class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.trade_stocks_done = False

        self.kiwoom = Kiwoom()
        self.kiwoom.comm_connect()

        # Timer1 - 1초에 한 번씩 이벤트가 발생한다.
        self.timer = QTimer(self)
        self.timer.start(1000)
        self.timer.timeout.connect(self.timeout)

        # Account 정보 가져오기
        accounts_num = int(self.kiwoom.get_login_info("ACCOUNT_CNT"))
        accounts = self.kiwoom.get_login_info("ACCNO")
        accounts_list = accounts.split(';')[0:accounts_num]
        self.lineEdit.textChanged.connect(self.code_changed)
        self.comboBox.addItems(accounts_list)
        self.comboBox_2.addItems(['신규주문', '신규매도', '매수취소', '매도취소'])
        self.comboBox_3.addItems(['지정가', '시장가'])

        # Order
        self.pushButton.clicked.connect(self.send_order)

        # Balance
        self.pushButton_2.clicked.connect(self.check_balance)

        # Timer2 - 10초에 한 번씩 이벤트를 발생한다.
        self.timer2 = QTimer(self)
        self.timer2.start(1000*10)
        self.timer2.timeout.connect(self.timeout2)

        # Load Buy and Sell list
        self.load_buy_sell_list()

    def timeout(self):
        """
        TImer

        :return:
        """
        # 장시작 시 주문
        market_start_time = QTime(9, 0, 0)
        market_end_time = QTime(15, 30, 0)
        current_time = QTime.currentTime()

        if market_start_time < current_time < market_end_time:
            if self.trade_stocks_done is False:
                self.trade_stocks()

        text_time = current_time.toString("hh:mm:ss")
        time_msg = "현재시간: " + text_time

        state = self.kiwoom.get_connect_state()
        if state == 1:
            state_msg = "서버 연결 중"
        else:
            state_msg = "서버 미 연결 중"

        self.statusbar.showMessage(state_msg + " | " + time_msg)

    def code_changed(self):
        """
        사용자가 입력한 종목 정보를 얻어온다.

        :return:
        """
        code = self.lineEdit.text()
        name = self.kiwoom.get_master_code_name(code)
        self.lineEdit_2.setText(name)

    def send_order(self):
        order_type_lookup = {'신규매수': 1,
                             '신규매도': 2,
                             '매수취소': 3,
                             '매도취소': 4}
        hoga_lookup = {'지정가': '00', '시장가': '03'}

        account = self.comboBox.currentText()
        order_type = self.comboBox_2.currentText()
        code = self.lineEdit.text()
        hoga = self.comboBox_3.currentText()
        num = self.spinBox.value()
        price = self.spinBox_2.value()

        self.kiwoom.send_order("send_order_req", '0101', account, order_type_lookup[order_type], code, num, price, hoga_lookup[hoga], "")

    def check_balance(self):
        """
        계좌 전체 잔고 및 종목별 수익 현황을 출력

        :return:
        """
        self.kiwoom.reset_opw00018_output()
        account_number = self.kiwoom.get_login_info("ACCNO")
        account_number = account_number.split(';')[0]

        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 0, "2000")

        while self.kiwoom.remained_data:

            # opw00018
            time.sleep(0.2)
            self.kiwoom.set_input_value("계좌번호", account_number)
            self.kiwoom.comm_rq_data("opw00018_req", "opw00018", 2, "2000")

        # opw00001
        self.kiwoom.set_input_value("계좌번호", account_number)
        self.kiwoom.comm_rq_data("opw00001_req", "opw00001", 0, "2000")

        # balance
        item = QTableWidgetItem(self.kiwoom.d2_deposit)
        item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
        self.tableWidget.setItem(0, 0, item)

        for i in range(1, 6):
            item = QTableWidgetItem(self.kiwoom.opw00018_output['single'][i-1])
            item.setTextAlignment(Qt.AlignVCenter | Qt.AlignRight)
            self.tableWidget.setItem(0, i, item)
        self.tableWidget.resizeRowsToContents()

        # Item list
        item_count = len(self.kiwoom.opw00018_output['multi'])
        self.tableWidget_2.setRowCount(item_count)

        for j in range(item_count):
            row = self.kiwoom.opw00018_output['multi'][j]
            for i in range(len(row)):
                item = QTableWidgetItem(row[i])
                item.setTextAlignment(Qt.AlignCenter | Qt.AlignRight)
                self.tableWidget_2.setItem(j, i, item)

        self.tableWidget_2.resizeRowsToContents()

    def timeout2(self):
        """
        실시간 조회 기능 구현

        :return:
        """
        if self.checkBox.isChecked():
            self.check_balance()

    # load buy list
    def load_buy_sell_list(self):
        """
        buy and sell list를 텍스트 파일로부터 불러온다.

        :return:
        """
        f = open('buy_list.txt', 'rt', encoding='UTF8')
        buy_list = f.readlines()
        f.close()

        f = open('sell_list.txt', 'rt', encoding='UTF8')
        sell_list = f.readlines()
        f.close()

        row_count = len(buy_list) + len(sell_list)
        self.tableWidget_3.setRowCount(row_count)

        # buy_list
        for j in range(len(buy_list)):
            row_data = buy_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rsplit())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_3.setItem(j, i, item)

        # sell_list
        for j in range(len(sell_list)):
            row_data = sell_list[j]
            split_row_data = row_data.split(';')
            split_row_data[1] = self.kiwoom.get_master_code_name(split_row_data[1].rstrip())

            for i in range(len(split_row_data)):
                item = QTableWidgetItem(split_row_data[i].rstrip())
                item.setTextAlignment(Qt.AlignVCenter | Qt.AlignCenter)
                self.tableWidget_3.setItem(len(buy_list) + j, i, item)

        self.tableWidget_3.resizeRowsToContents()

    # trade stocks
    def trade_stocks(self):
        """
        stock을 거래한다.

        :return:
        """
        hoga_lookup = {'지정가': '00', '시장가': '03'}

        f = open('buy_list.txt', 'rt', encoding='UTF8')
        buy_list = f.readlines()
        f.close()

        f = open('sell_list.txt', 'rt', encoding='UTF8')
        sell_list = f.readlines()
        f.close()

        # account
        account = self.comboBox.currentText()

        # buy_list
        buy_return_list = [-1] * len(buy_list)
        for i, row_data in enumerate(buy_list):
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == "매수전":
                buy_return = self.kiwoom.send_order("send_order_req", '0101', account, 1, code, num, price, hoga_lookup[hoga], "")

                if buy_return == 0:
                    buy_return_list[i] = 0
            elif split_row_data[-1].rstrip() == "주문완료":
                buy_return_list[i] = 0

        for i, row_data in enumerate(buy_list):
            if buy_return_list[i] == 0:
                buy_list[i] = buy_list[i].replace("매수전", "주문완료")

        # sell_list
        sell_return_list = [-1] * len(sell_list)
        for i, row_data in enumerate(sell_list):
            split_row_data = row_data.split(';')
            hoga = split_row_data[2]
            code = split_row_data[1]
            num = split_row_data[3]
            price = split_row_data[4]

            if split_row_data[-1].rstrip() == "매도전":
                sell_return = self.kiwoom.send_order("send_order_req", '0101', account, 2, code, num, price, hoga_lookup[hoga], "")

                if sell_return == 0:
                    sell_return_list[i] = 0
            elif split_row_data[-1].rstrip() == "주문완료":
                sell_return_list[i] = 0

        for i, row_data in enumerate(sell_list):
            if sell_return_list[i] == 0:
               sell_list[i] = sell_list[i].replace('매도전', '주문완료')

        trade_sum = 0
        for i, row_data in enumerate(buy_list):
            split_row_data = row_data.split(';')
            if split_row_data[-1].rstrip() == '주문완료':
                trade_sum += 1

        for i, row_data in enumerate(sell_list):
            split_row_data = row_data.split(';')
            if split_row_data[-1].rstrip() == '주문완료':
                trade_sum += 1

        print(trade_sum)
        if trade_sum == len(buy_list) + len(sell_list):
            self.trade_stocks_done = True

        # file update
        f = open('buy_list.txt', "wt", encoding='UTF8')
        for row_data in buy_list:
            f.write(row_data)
        f.close()

        # file update
        f = open('sell_list.txt', "wt", encoding='UTF8')
        for row_data in sell_list:
            f.write(row_data)
        f.close()


if __name__== "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    app.exec_()