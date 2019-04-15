import pandas as pd
from pandas import Series, DataFrame
import sqlite3

address = "C:\\Users\\lifesailor\\Desktop\\investment\\data-driven-investment\\data\\database\\kospi.db"
con = sqlite3.connect(address)
df = pd.read_sql("SELECT * FROM kakao", con, index_col=None)
