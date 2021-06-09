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
from dotenv import load_dotenv
import os

load_dotenv()


#For each coin 
#take last 200 values
#fit linear model 
#if value for today is higher than yesterday, put bullish in sql

