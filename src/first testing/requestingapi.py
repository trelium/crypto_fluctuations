import requests
import json


response = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin")
response=response.json()
print(response)
a=3+2
#fdsafdsaf
print(len(response))
