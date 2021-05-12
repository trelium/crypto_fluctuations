# ! pip install pycoingecko
import pyodbc
from pycoingecko import CoinGeckoAPI


class UtentiSQL():
    """
    Class to instantiate a connection to the SQL database containing the preferences expressed
    by the users via the Telegram interface. 
    """
    def __init__(self):
        self.server = 'bdtproject-sqlserver.database.windows.net'
        self.database = 'bdt-SQL1'
        self.username = 'jacoccardo'
        self.password = 'Riccarcopo1'   
        self.driver= '{ODBC Driver 17 for SQL Server}'
        
        #establish connection 
        self.cnxn = pyodbc.connect('DRIVER='+self.driver+';SERVER='+self.server+';PORT=1433;DATABASE='+self.database+';UID='+self.username+';PWD='+ self.password)
        self.cursor = cnxn.cursor()
    
    def get_chats(self, currentvalues): 
        """
        Retrieves the chat_ids relative to the users that need to be notified of a change, given in input the current market values. 
        """
        for currency in currentvalues:
            if currency['usd'] > 0:
                self.cursor.execute("""SELECT chat_id FROM utenti_bot 
                                        WHERE active = 1 
                                        AND {} > {} """.format(currency, currency['usd']))
            else:
                self.cursor.execute("""SELECT chat_id FROM utenti_bot 
                                        WHERE active = 1 
                                        AND {} < {} """.format(currency, currency['usd']))

        return self.cursor.fetchall() #list of tuples

    def set_state(self, user:str(), chat:str(), state:str()): #TODO what if the record for a certain chat already exists? 
        try:
            self.cursor.execute("""INSERT INTO utenti_bot(user_id, chat_id, state) 
                                    VALUES ('{}','{}','{}')""".format(user, chat, state))
            self.cnxn.commit()
            return True
        except: 
            return False 
    
    def get_state(self, chat:str()):
        try:
            self.cursor.execute("""SELECT state FROM utenti_bot
                                    WHERE chat_id = {} """.format(chat))
            found = self.cursor.fetchall()
            if len(found) != 0:
                return str(found[0][0])
            else:
                return ('No state')
        except:
            return False

    def set_active(self,chat:str()):
        try:
            self.cursor.execute("""UPDATE utenti_bot SET active = 1 
                                    WHERE chat_id = '{}' """.format(chat)
            self.cnxn.commit()
            return True
        except: 
            return False 

    def is_already_present(self,chat:str()):
        """
        returns true if a chat is already in the database, false otherwise 
        """
        self.cursor.execute("""SELECT chat_id FROM utenti_bot
                                    WHERE chat_id = {} """.format(chat))
        found = self.cursor.fetchall()
        if len(found) != 0:
            return True 
        else:
            return False

    def get_active(self,chat:str()):
        try:
            self.cursor.execute("""SELECT active FROM utenti_bot
                                    WHERE chat_id = {} """.format(chat))
            found = self.cursor.fetchall()
            if len(found) != 0 and str(found[0][0]) ==  b'\x01':
                return 1
            elif len(found) != 0 and str(found[0][0]) ==  b'\x00':
                return 0
            else: 
                return False
        except:
            return False

    def set_preferences(self, chat:str(), preferences: dict()):
        try:
            if not self.is_already_present(chat):
                    self.cursor.execute("""INSERT INTO utenti_bot(chat_id) 
                                    VALUES '{}' """.format(chat)
                    self.cnxn.commit()                        
            for coin in preferences:
                self.cursor.execute("""UPDATE utenti_bot SET '{}' = {}
                                WHERE chat_id = '{}' """.format(coin, preferences[coin], chat)
                self.cnxn.commit()
                
        except:
            raise ValueError()
            

            
        

cg = CoinGeckoAPI()
db = UtentiSQL()

currentvalues = cg.get_price(ids=['bitcoin', 'ripple', 'ethereum','Binance Coin','dogecoin' ], vs_currencies='usd')
db.get_chats(currentvalues)
