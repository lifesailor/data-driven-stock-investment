import pandas_datareader.data as web
import datetime
import matplotlib.pyplot as plt
from zipline.api import order, symbol
from zipline.algorithm import TradingAlgorithm

start = datetime.datetime(2010, 1, 1)
end = datetime.datetime(2016, 3, 19)
data = web.DataReader("AAPL", "yahoo", start, end)

plt.plot(data.index, data['Adj Close'])
plt.show()


def initialize(context):
    pass

def handle_data(context, data):
    """
    APPL 한 주를 주문

    :param context:
    :param data:
    :return:
    """
    order(symbol('AAPL'), 1)


