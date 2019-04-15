import os
import sys
import datetime
from time import sleep
from multiprocessing import Pool, Value
from itertools import repeat

import pandas as pd
from urllib.request import urlopen
from bs4 import BeautifulSoup
from pykrx import Krx

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.folder import make_folder
from utils.logger import set_logger


base_path = os.path.dirname(os.path.abspath('..'))
data_path = os.path.join(base_path, 'data')
stock_path = os.path.join(data_path, 'stock')
folder_path = os.path.join(stock_path, 'folder')
comment_path = os.path.join(folder_path, '네이버댓글_190414')

code_path = os.path.join(base_path, 'code')
crawler_path = os.path.join(code_path, 'crawler')

make_folder(base_path, data_path, stock_path, folder_path, comment_path, code_path, crawler_path)
logger = set_logger('comment_logger')
krx = Krx()


def get_naver_comment(code):
    comments = []
    views = []
    page = 40

    for num in range(1, page):
        page = "https://finance.naver.com/item/board.nhn?code=" + str(code) + "&page=" + str(num)
        html = urlopen(page)
        soup = BeautifulSoup(html, "html.parser")
        comment = soup.select('span.tah.gray03')

        for i in range(len(comment)):
            if i % 2 == 0:
                comments.append(comment[i].text)
            else:
                views.append(comment[i].text)

    comments = [comment[:10] for comment in comments]
    df = pd.DataFrame({'time': pd.to_datetime(comments), 'views': views})
    df.to_csv(os.path.join(comment_path, code + '.csv'), index=False)
    logger.info("successfully saved " + str(code))


if __name__ == "__main__":
    code_list = krx.get_tickers()
    logger.info("Successfully loaded codes")

    pool = Pool(processes=16)
    pool.map(get_naver_comment, code_list)
    pool.close()
    pool.join()
