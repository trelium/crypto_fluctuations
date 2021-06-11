import requests

response= requests.get("https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1&sparkline=false")
response=response.json()

lista_monete_supportate=[i['id'] for i in response]
print(lista_monete_supportate)