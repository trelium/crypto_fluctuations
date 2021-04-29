import requests
import json


response = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/history?date=30-12-2017")
response=response.json()
print(response)

print(len(response))
