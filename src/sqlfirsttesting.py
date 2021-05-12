import pyodbc



class mqtttosql:

    def __init__(self,
    server = 'bdtproject-sqlserver.database.windows.net',
    database = 'BDT-SQL1',
    username = 'jacoccardo',
    password = 'Riccarcopo1',   
    driver= '{ODBC Driver 17 for SQL Server}'
    ):
        
        self.server = server
        self.database = database
        self.username = username
        self.password = password  
        self.driver= driver

        self.cnxn = pyodbc.connect('DRIVER='+driver+';SERVER='+server+';PORT=1433;DATABASE='+database+';UID='+username+';PWD='+ password)
        self.cnxn.setencoding('utf-8')
        self.cursor=self.cnxn.cursor()

test=mqtttosql