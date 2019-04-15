import pandas as pd
import sqlite3
from pandas import Series, DataFrame

raw_data = {'col0': [1,2,3,4,],
            'col1': [10,20,30,40],
            'col2': [100,200,300,400]}
df = DataFrame(raw_data)

address = "C:\\Users\\lifesailor\\Desktop\\investment\\data-driven-investment\\data\\database\\kospi.db"
con = sqlite3.connect(address)
df.to_sql('test', con)
# df.to_sql('test', con, chunksize=1000)

"""
name	SQL 테이블 이름으로 파이썬 문자열로 형태로 나타낸다.
con	Cursor 객체
flavor	사용한 DBMS를 지정할 수 있는데 'sqlite' 또는 'mysql'을 사용할 수 있다. 기본값은 'sqlite'이다.
schema	Schema를 지정할 수 있는데 기본값은 None이다.
if_exists	데이터베이스에 테이블이 존재할 때 수행 동작을 지정한다. 'fail', 'replace', 'append' 중 하나를 사용할 수 있는데 기본값은 'fail'이다. 'fail'은 데이터베이스에 테이블이 있다면 아무 동작도 수행하지 않는다. 'replace'는 테이블이 존재하면 기존 테이블을 삭제하고 새로 테이블을 생성한 후 데이터를 삽입한다. 'append'는 테이블이 존재하면 데이터만을 추가한다.
index	DataFrame의 index를 데이터베이스에 칼럼으로 추가할지에 대한 여부를 지정한다. 기본값은 True이다.
index_label	인덱스 칼럼에 대한 라벨을 지정할 수 있다. 기본값은 None이다.
chunksize	한 번에 써지는 로우의 크기를 정숫값으로 지정할 수 있다. 기본값은 None으로 DataFrame 내의 모든 로우가 한 번에 써진다.
dtype	칼럼에 대한 SQL 타입을 파이썬 딕셔너리로 넘겨줄 수 있다.
"""


