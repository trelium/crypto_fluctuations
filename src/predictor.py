"""
-----------------------------------------------
---- Cryptocurrency Price Trend Predictor  ----
-----------------------------------------------
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - May 2021.

---- Description----
Script taking care of computing price trend predictions for the 
Cryptocurrency Predictor service. 

Functionalities include:
    * Ingesting time series data for a set of cryptocurrencies
    * Computing bullish/bearish market condition for each crypto 
    * Saving results in an external SQL database  

"""
from sklearn.linear_model import LinearRegression
from database import PricesSQL
#from dotenv import load_dotenv
#import os

#load_dotenv()

#Instatiate database interface 
db = PricesSQL()

#Get list of all coins currently present in db
cryptos = db.get_coins()

for coin in cryptos:
    prices = db.get_prices(coin)

    #fit linear model 
    #reg = LinearRegression().fit(X, y)

    #if value for today is higher than yesterday, put bullish in sql

