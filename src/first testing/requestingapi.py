import requests
import json


response = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/market_chart?vs_currency=usd&days=1")
response=response.json()
print(response['prices'])

print(len(response['prices']))
