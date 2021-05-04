import requests
import json


response = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/history?date=30-12-2017")
response=response.json()
print(response)

print('ho modificato il file dalla macchina virtuale')
print('test')
print(len(response))

print('test2221')