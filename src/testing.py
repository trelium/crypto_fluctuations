import requests
from database import UsersSQL
import re
"""
response= requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false")
response=response.json()

supported_coins=[i['id'] for i in response]

#generate column names to be placed in a query SQL
with open('quryfile.txt',mode='w') as file:
    for i in supported_coins:
        file.write(f'{i} FLOAT, \n latest_update_{i} BIGINT,\n')
"""

substr = 'bigfij@56,78%'.split('@')
if ',' not in  substr[1] and re.match('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1].replace(' ','')):
    foundpct = float(re.findall('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%'))
elif '.' not in  substr[1] and re.match('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[1].replace(' ','')): #changes only a comma from previous regex
    foundpct = float(re.findall('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%').replace(',','.'))

print(foundpct)