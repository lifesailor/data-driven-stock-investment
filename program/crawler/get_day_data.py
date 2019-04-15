"""
분봉 데이터를 가져오는 코드
"""
import os
import sys
import time

from multiprocessing import Pool, Value
from pykrx import Krx
import pandas as pd

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.folder import make_folder
from utils.logger import set_logger


logger = set_logger('day_crawler')
base_path = os.path.dirname(os.path.abspath('..'))
data_path = os.path.join(base_path, 'data')
save_path = os.path.join(data_path, 'stock')
folder_path = os.path.join(save_path, 'folder')
day_path = os.path.join(folder_path, '일별매매가격_190414')

make_folder(base_path, data_path, save_path, folder_path, day_path)
krx = Krx()


def get_day_info(code):
    df = krx.get_market_ohlcv("20100101", "20190414", code)
    df.to_csv(os.path.join(day_path, code + '.csv'))
    logger.info("successfully saved " + str(code))


if __name__ == "__main__":
    code_list = krx.get_tickers()
    # code_list = ['033320', '121800', '057680', '036090', '041190', '021080', '027830', '101140']
    logger.info("Succesfully get code list")

    counter = Value('i', 0)

    pool = Pool(processes=16)
    pool.map(get_day_info, code_list)
    pool.close()
    pool.join()

