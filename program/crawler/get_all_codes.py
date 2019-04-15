"""
모든 종목 코드를 가져오는 코드
"""
import os
import sys
import time

from pykrx import Krx
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.folder import make_folder


if __name__ == "__main__":
    krx = Krx()
    code_list = krx.get_tickers()

    base_path = os.path.dirname(os.path.abspath('..'))
    data_path = os.path.join(base_path, 'data')
    stock_path = os.path.join(data_path, 'stock')
    folder_path = os.path.join(stock_path, 'folder')

    make_folder(stock_path)
    make_folder(folder_path)

    df = pd.DataFrame({'code': code_list})
    df.to_csv(os.path.join(folder_path, 'code_list.csv'), index=False)