"""
요약 재무재표 정보를 크롤링한다.
"""
import os
import sys
import datetime
from time import sleep
from multiprocessing import Pool, Value
from itertools import repeat

import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from utils.folder import make_folder
from utils.logger import set_logger

logger = set_logger('basic_finance_crawler')

base_path = os.path.dirname(os.path.abspath('..'))
data_path = os.path.join(base_path, 'data')
stock_path = os.path.join(data_path, 'stock')
folder_path = os.path.join(stock_path, 'folder')
summary_path = os.path.join(folder_path, '재무제표_20190331')

make_folder(base_path, data_path, stock_path, folder_path, summary_path)


def get_summary_finance(code):
    url = 'http://media.kisline.com/highlight/mainHighlight.nice?nav=1&paper_stock=' + str(code)

    try:
        tables = pd.read_html(url)

        df = None
        for i in range(4, 4 + 4):
            df = pd.concat([df, tables[i]], axis=1)

        df.columns = df.columns.get_level_values(1)
        change_column_name(df)
        df.set_index(df.columns[0], inplace=True)
        df = df.T
        df.reset_index(inplace=True)
        df = df[df['index'].str.contains("연결")]
        df.reset_index(inplace=True, drop=True)
        df.to_csv(os.path.join(summary_path, code + '.csv'), index=False)
        logger.info("successfully saved " + str(code))
    except:
        pass


def change_column_name(data):
    columns = data.columns
    new_columns = []
    half_len = len(columns) // 2
    total_len = len(columns)

    for i in range(half_len):
        new_columns.append('개별_' + data.columns[i])

    for i in range(half_len, total_len):
        new_columns.append('연결_' + data.columns[i])

    data.columns = new_columns
    del data[data.columns[half_len]]


if __name__ == "__main__":
    code_list = ['187790', '119650', '044340', '045060',
                 '045520', '065950', '080470', '012690',
                 '083550', '071460', '066130', '121800']
    logger.info("Succesfully get code list")
    counter = Value('i', 0)

    pool = Pool(processes=4)
    pool.map(get_summary_finance, code_list)
    pool.close()
    pool.join()

