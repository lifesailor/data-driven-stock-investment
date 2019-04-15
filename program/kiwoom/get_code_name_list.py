"""
전체 종목과 이름을 가져오는 코드
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

save = True

base_path = os.path.dirname(os.path.abspath('..'))
data_path = os.path.join(base_path, 'data')
stock_path = os.path.join(data_path, 'stock')
folder_path = os.path.join(stock_path, 'folder')
make_folder(base_path, data_path, stock_path, folder_path)


class MyWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        self.kiwoom.dynamicCall("CommConnect()")

        self.setWindowTitle("종목 코드")
        self.setGeometry(300, 300, 300, 150)

        btn1 = QPushButton("종목코드 얻기", self)
        btn1.move(190, 10)
        btn1.clicked.connect(self.btn1_clicked)

        self.listWidget = QListWidget(self)
        self.listWidget.setGeometry(10, 10, 170, 130)

    def btn1_clicked(self):
        kospi_ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["0"])
        kospi_code_list = kospi_ret.split(';')

        kosdaq_ret = self.kiwoom.dynamicCall("GetCodeListByMarket(QString)", ["10"])
        kosdaq_code_list = kosdaq_ret.split(';')

        kospi_code_list.extend(kosdaq_code_list)
        code_list = kospi_code_list

        code_name_list = []
        name_list = []

        for x in code_list:
            name = self.kiwoom.dynamicCall("GetMasterCodeName(QString)", [x])
            code_name_list.append(x + " : " + name)
            name_list.append(name)

        self.listWidget.addItems(code_name_list)

        if save:
            df = pd.DataFrame({'code': code_list,
                               'name': name_list})
            df.to_csv(os.path.join(folder_path, 'code_name_list.csv'), index=False)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWindow = MyWindow()
    myWindow.show()
    sys.exit(app.exec_())