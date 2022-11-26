import sqlite3

conn = sqlite3.connect('gaoyao.db')
cursor = conn.cursor()
# create table
# cursor.execute(
#     'create table searchControl (x0url varchar(200),x0file varchar(20),x0downLoad varchar(1),x0search varchar(1))'
# )
# insert record for test
# cursor.execute("insert into searchControl values('1','2','3','4')")
# select record for test
# cursor.execute('select x0url,x0search from searchControl')
# result = cursor.fetchall()
# print(result)
# delete all records
# cursor.execute('delete from searchControl')
# conn.commit()
# cursor.execute('alter table searchControl add column x0keys varchar(500)')
cursor.execute('delete from searchControl')
conn.commit()
# close connection and cursor
cursor.close()
conn.close
