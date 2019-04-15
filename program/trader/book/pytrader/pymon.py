import sys
from PyQt5.QtWidgets import *
import Kiwoom
import time
import datetime

import pandas as pd

MARKET_KOSPI = 0
MARKET_KOSDAQ = 10

class PyMon:
    def __init__(self):
        self.kiwoom = Kiwoom.Kiwoom()
        self.kiwoom.comm_connect()
        self.get_code_list()

    def get_code_list(self):
        self.kospi_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSPI)
        self.kosdaq_codes = self.kiwoom.get_code_list_by_market(MARKET_KOSDAQ)

    def get_ohlcv(self, code, start):
        self.kiwoom.ohlcv = {'date': [], 'open': [], 'high': [], 'low': [], 'close': [], 'volume': []}
        self.kiwoom.set_input_value("종목코드", code)
        self.kiwoom.set_input_value("기준일자", start)
        self.kiwoom.set_input_value("수정주가구분", 1)
        self.kiwoom.comm_rq_data('opt10081_req', 'opt10081', 0, '0101')
        time.sleep(2)

        df = pd.DataFrame(self.kiwoom.ohlcv, columns=['open', 'high', 'low', 'close', 'volume'],
                          index=self.kiwoom.ohlcv['date'])
        return df

    def run(self):
        """
        급등주를 포착하고 저장한다.

        :return:
        """
        buy_list = []
        num = len(self.kosdaq_codes)

        for i, code in enumerate(self.kosdaq_codes):
            print(i, "/", num)
            if self.check_speedy_rising_volume(code):
                print("급등주: ", code)
                buy_list.append(code)

            self.update_buy_list(buy_list)

    def check_speedy_rising_volume(self, code):
        """
        급등주 포착 알고리즘

        :param code:
        :return:
        """
        today = datetime.datetime.today().strftime("%Y%m%d")
        df = self.get_ohlcv(code, today)
        volumes = df['volume']

        if len(volumes) < 21:
            return False

        sum_vol20 = 0
        today_vol = 0

        for i, vol in enumerate(volumes):
            if i == 0:
                today_vol = vol
            elif i <= i <= 20:
                sum_vol20 += vol
            else:
                break

        avg_vol20 = sum_vol20 / 20
        if today_vol > avg_vol20 * 10:
            return True

    def update_buy_list(self, buy_list):
        f = open("buy_list.txt", "wt", encoding='UTF8')
        for code in buy_list:
            f.writelines("매수;" + code + ";시장가;10;0;매수전")
        f.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    pymon = PyMon()
    pymon.run()