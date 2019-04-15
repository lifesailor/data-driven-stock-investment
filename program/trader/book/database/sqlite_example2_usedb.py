import sqlite3

address = "C:\\Users\\lifesailor\\Desktop\\investment\\data-driven-investment\\data\\database\\kospi.db"
con = sqlite3.connect(address)
cursor = con.cursor()
cursor.execute("SELECT * FROM kakao")

cursor.fetchone()
cursor.fetchone()
cursor.fetchall()

kakao = cursor.fetchall()
kakao[0][1]