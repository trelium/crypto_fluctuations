import requests

response= requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false")
response=response.json()

print(test.get_preferences())

lista_monete_supportate=[i['id'] for i in response]
print(lista_monete_supportate)

"""
#generate column names to be placed in a query SQL
with open('quryfile.txt',mode='w') as file:
    for i in range(1,1001):
        file.write(f'coin_{i} VARCHAR(300), \n pct_{i} FLOAT,\n')
"""