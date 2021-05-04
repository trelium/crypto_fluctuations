# ! pip install pycoingecko

from pycoingecko import CoinGeckoAPI
cg = CoinGeckoAPI()

currentvalues = cg.get_price(ids=['bitcoin', 'ripple', 'ethereum','Binance Coin','dogecoin' ], vs_currencies='usd')
print(currentvalues)