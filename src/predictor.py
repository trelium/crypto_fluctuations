"""
-----------------------------------------------
---- Cryptocurrency Price Trend Predictor  ----
-----------------------------------------------
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
Script taking care of computing price trend predictions for the 
Cryptocurrency Predictor service. 

Functionalities include:
    * Ingesting time series data for a set of cryptocurrencies
    * Computing bullish/bearish market condition for each crypto
    * Saving results in a local json file

"""

from sklearn.linear_model import LinearRegression
from database import PricesSQL, Predictions
from pprint import pprint
import numpy as np

#from dotenv import load_dotenv
#import os

#load_dotenv()

#Instatiate database interface 
priceshistory = PricesSQL()
predictions = Predictions()

#Get list of all coins currently present in db
cryptos = priceshistory.get_coins()

for coin in cryptos:
    prices = np.asarray([i[0] for i in priceshistory.get_prices(coin, all=True)]) #last is most recent 
    #(-320:-120)first window for training: #[-200:], #[-320:-120], #[-440:-240] ... always -120
    startidx = -320
    endidx = -120
    X, Y = [], []
    while abs(startidx)<len(prices): #make overlapping time windows for training 
        X.append(prices[startidx:endidx])
        Y.append(prices[endidx])
        startidx -= 120
        endidx -= 120
    
    if len(X) == 0: #not enough training data 
        predictions.set_no_pred(coin)
        continue 
    else: #training   
        X = np.array(X) 
        Y = np.array(Y) 
        #fit linear model 
        reg = LinearRegression().fit(X, Y)
        
    #Making prediction for current coin 
    currentprices = np.asarray([i[0] for i in priceshistory.get_prices(coin, all=False)])
    currentprices = np.expand_dims(currentprices, axis=0)
    predprice = reg.predict(currentprices)

    #if value for today is higher than yesterday, write bullish in predictions, else bearish
    if predprice > np.squeeze(currentprices)[-1]:
        predictions.set_bull_pred(coin)
    else:
        predictions.set_bear_pred(coin)
    
#save all predictions to disk 
predictions.save()

