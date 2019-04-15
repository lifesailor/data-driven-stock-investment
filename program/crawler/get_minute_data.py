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


base_path = os.path.dirname(os.path.abspath('..'))
data_path = os.path.join(base_path, 'data')
stock_path = os.path.join(data_path, 'stock')
folder_path = os.path.join(stock_path, 'folder')
minute_path = os.path.join(folder_path, '분별매매가격_가상화폐')

code_path = os.path.join(base_path, 'code')
crawler_path = os.path.join(code_path, 'crawler')

make_folder(base_path, data_path, stock_path, folder_path, minute_path, code_path, crawler_path)
logger = set_logger('minute_logger')


def main(code, dates):
    for date in dates:
        tables = []

        for num in range(1, 43):
            page = "https://finance.naver.com/item/sise_time.nhn?code=" + str(code) + "&thistime=2019" + str(date) + "160000&page=" + str(num)
            html = urlopen(page)
            bs_object = BeautifulSoup(html, "html.parser")
            bs_object_table = bs_object.table
            tables.append(bs_object_table)
            sleep(0.1)

        # data frame
        df = merge_all(tables)

        # parse
        df = parse_all(df, date)

        # save
        save_dataframe(df, code, date)
        logger.info("successfully saved " + str(code) + " " + str(date))


def merge_all(tables):
    """
    Merge All tables into a DataFrame

    :param tables:
    :return: DataFrame
    """
    def get_columns(table):
        columns = table.find_all("th")
        columns = [column.get_text() for column in columns]
        return columns

    def make_dataframe(columns, table):
        rows = table.find_all("td")

        del rows[0]
        del rows[-1]
        del rows[35:38]

        times = []
        prices = []
        updowns = []
        sells = []
        buys = []
        cumsum = []
        nums = []

        count = 0

        for i, row in enumerate(rows):
            if i % 7 == 0:
                times.append(row.get_text())
            elif i % 7 == 1:
                prices.append(row.get_text())
            elif i % 7 == 2:
                updowns.append(row.get_text())
            elif i % 7 == 3:
                sells.append(row.get_text())
            elif i % 7 == 4:
                buys.append(row.get_text())
            elif i % 7 == 5:
                cumsum.append(row.get_text())
            elif i % 7 == 6:
                nums.append(row.get_text())

        df = pd.DataFrame({
            columns[0]: times,
            columns[1]: prices,
            columns[2]: updowns,
            columns[3]: sells,
            columns[4]: buys,
            columns[5]: cumsum,
            columns[6]: nums
        })
        return df

    df = None
    columns = get_columns(tables[0])

    for i, table in enumerate(tables):
        new_df = make_dataframe(columns, table)
        df = pd.concat([df, new_df], axis=0)
    df.drop_duplicates(inplace=True)
    df.reset_index(inplace=True, drop=True)
    return df


def parse_all(df, date):
    """
    Parse DataFrame to analyze format.

    :param df: DataFrame
    :param date: Date
    :return:
    """
    def string_to_int(x):
        try:
            x = x.replace(',', '')
            x = int(x)
        except:
            pass
        return x

    def drop_false_row(df):
        if isinstance(df.iloc[-1]['체결가'], int):
            return df
        else:
            return df.drop(len(df) - 1)

    def calc_time(date):
        today_info = datetime.datetime.today()
        today = datetime.datetime(year=today_info.year,
                                  month=today_info.month,
                                  day=today_info.day)
        if date[0] == '0':
            month = int(date[1])
        else:
            month = int(date[:2])
        if date[2] == '0':
            day = int(date[3])
        else:
            day = int(date[2:])

        date = datetime.datetime(year=2019,
                                 month=month,
                                 day=day)

        diff = today - date
        return diff

    for column in df.columns:
        df[column] = df[column].apply(lambda x: string_to_int(x))
    df = drop_false_row(df)
    time = calc_time(date)
    df[df.columns[0]] = df[df.columns[0]].apply(lambda x: pd.to_datetime(x) - time)
    df = df.set_index(df.columns[0])
    df.sort_index(inplace=True)
    return df


def save_dataframe(df, code, date):
    """
    Save DataFrame into a csv file.

    :param df:
    :param code:
    :param date:
    :return:
    """
    save_path = os.path.join(minute_path, code)
    make_folder(save_path)
    df.to_csv(os.path.join(save_path, date + '.csv'))


if __name__ == "__main__":
    dates = ['0401', '0402', '0403', '0404', '0405', '0408']
#    code_list = ['033320', '121800', '057680', '036090', '041190', '021080', '027830', '101140', '100790']
    code_list = ['100790']

    logger.info("Successfully loaded codes")

    counter = Value('i', 0)

    pool = Pool(processes=4)
    pool.starmap(main, zip(code_list, repeat(dates)))
    pool.close()
    pool.join()