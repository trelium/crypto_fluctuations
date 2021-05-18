# from multiprocessing import Process
# import sys

# rocket = 0

# def func1():
#     global rocket
#     print ('start func1')
#     while rocket < 300000:
#         rocket += 1
#     print ('end func1')

# def func2():
#     global rocket
#     print ('start func2')
#     while rocket < 30000:
#         rocket += 1
#     print ('end func2')

# if __name__=='__main__':
#     p1 = Process(target = func1)
#     p1.start()
#     p2 = Process(target = func2)
#     p2.start()

# ###
# from multiprocessing import Process
# def func1:
#      #does something

# def func2:
#      #does something

# if __name__=='__main__':
#      p1 = Process(target = func1)
#      p1.start()
#      p2 = Process(target = func2)
#      p2.start()

import pyodbc
server = 'bdtproject.database.windows.net'
database = 'BDT-sql2'
username = 'jacoccardo'
password = 'Riccarcopo1'
driver= '{ODBC Driver 17 for SQL Server}'

#SQL connector
cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
cnxn.setencoding('utf-8')
cursor=cnxn.cursor()
cursor.execute("INSERT INTO dbo.pricedata VALUES('blallo','12',0.4,0);")
cursor.commit()
