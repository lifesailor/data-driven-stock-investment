import os
import sys
import time

import pandas as pd
import numpy as np
from matplotlib import pyplot as plt

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
from utils.folder import make_folder
from utils.logger import set_logger

logger = set_logger("trend")
base_path = os.path.dirname(os.path.abspath('..'))
data_path = os.path.join(base_path, 'data')
save_path = os.path.join(data_path, 'stock')
folder_path = os.path.join(save_path, 'folder')
day_path = os.path.join(folder_path, '일봉_20190323')

invest_path = os.path.join(base_path, 'invest')
trend_path = os.path.join(invest_path, '3.추세주')
result_path = os.path.join(trend_path, 'result')

make_folder(invest_path, trend_path, result_path)


def load_day_data(files, code_list, standard_day):
    df_list = []

    for i, file in enumerate(files):
        try:
            new_df = pd.read_csv(os.path.join(day_path, file), engine='python', encoding='utf-8')
            new_df['code'] = file.split('.')[0]
            df_list.append(new_df.copy())
        except:
            pass

        if i % 100 == 0:
            print(i, '/', len(files))
    df = pd.concat(df_list, axis=0)
    df['날짜'] = pd.to_datetime(df['날짜'], format='%Y%m%d')
    df = df[df['날짜'] > pd.to_datetime(standard_day, format='%Y%m%d')]
    df = pd.merge(df, code_list, on='code', how='left')
    return df


def get_top_codes(df, code_list, standard_day, top_start=0, top_end=100):
    trend_codes = []
    trend_ratio = []

    codes = df['code'].unique()
    time_df = df[df['날짜'] >= standard_day]
    time_df = time_df[time_df['날짜'] <= standard_day + pd.DateOffset(days=7)]

    for i, code in enumerate(codes):
        df_code = time_df[time_df['code'] == code]
        df_code = df_code[df_code['날짜'] >= standard_day]
        df_code = df_code[df_code['날짜'] <= standard_day + pd.DateOffset(days=7)]

        try:
            first_price = df_code['시가'].iloc[0]
            final_price = df_code['종가'].iloc[-1]

            trend_codes.append(code)
            trend_ratio.append(final_price / first_price)
        except:
            pass

    trend_df = pd.DataFrame({'code': trend_codes, 'ratio': trend_ratio})
    trend_code_df = pd.merge(trend_df, code_list, on='code')
    trend_code_df.sort_values('ratio', ascending=False, inplace=True)
    return trend_code_df['code'][top_start:top_end].values


def buy_top_n_codes(df, top_n_codes, standard_day):
    codes = []
    ratio = []

    for i, code in enumerate(top_n_codes):
        df_code = df[df['code'] == code]
        df_code = df_code[df_code['날짜'] >= standard_day]
        df_code = df_code[df_code['날짜'] <= standard_day + pd.DateOffset(days=7)]

        try:
            first_price = df_code['시가'].iloc[0]
            final_price = df_code['종가'].iloc[-1]

            codes.append(code)
            ratio.append(final_price / first_price)
        except:
            pass

        top_n_df = pd.DataFrame({'code': codes, 'ratio': ratio})
    return top_n_df


if __name__ == "__main__":
    logger.info("Load code and name")
    code_list = pd.read_csv(os.path.join(folder_path, 'code_name_list.csv'), index_col=0)

    logger.info("Load day data")
    files = os.listdir(day_path)

    # day
    standard_day = '20150104'
    df = load_day_data(files, code_list, standard_day)

    start_time = time.time()
    start_end_tuple = [(0, 5), (0, 10), (0, 30), (0, 50), (10, 20),
                       (10, 30), (20, 30), (30, 50), (30, 100), (50, 100)]

    logger.info("Test Start")
    for start, end in start_end_tuple:
        earning_ratio_list = []
        day_list = []

        standard_day = '20150104'
        standard_day = pd.to_datetime(standard_day, format='%Y%m%d')
        total_days = pd.to_datetime('20190323') - standard_day
        total_weeks = total_days.days // 7
        logger.info("start: " + str(start) + " " + "end: " + str(end))

        for i in range(total_weeks):
            top_n_codes = get_top_codes(df, code_list, standard_day=standard_day, top_start=start, top_end=end)
            standard_day += pd.DateOffset(days=7)
            top_df = df[df['code'].isin(top_n_codes)]

            if i >= total_weeks - 4:
                save_week_name = "to_" + str(standard_day).replace(':', '-') + '.csv'
                top_df.to_csv(os.path.join(result_path, save_week_name))

            if top_df.shape[0] > 0:
                top_n_df = buy_top_n_codes(top_df, top_n_codes=top_n_codes, standard_day=standard_day)
                earning_ratio = np.mean(top_n_df['ratio'])
                earning_ratio_list.append(earning_ratio)
                day_list.append(standard_day)

            if i % 10 == 0:
                logger.info(str(i) + "/" + str(total_weeks))

        earning_ratio_df = pd.DataFrame({'ratio': earning_ratio_list[:-1], 'day': day_list[:-1]})
        save_name = "weekly_trend_" + str(start) + "_" + str(end) + ".csv"

        earning_ratio_df.to_csv(os.path.join(result_path, save_name), index=False)
        logger.info("Saved " + save_name)

