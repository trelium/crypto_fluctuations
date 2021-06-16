"""
----------------------------------------------------------------
----- First price history scraper to populate the SQL    -------
---------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
This script relies on apihistoricprices.py and it is advisable to refer to that script to enhance the code.
This script should be run before (or together with) historicingestion.py to load the scraped data in the SQL.

Core features:
    * Extract the last 400 days for each supported crypto. This only done to first populate the SQL to ensure
    the functioning of the prediction.
    * The prediction needs 320 data points at minimum to operate.
    * It is suggested to not overly increase the number of days that are being scraped because the coingecko API does
    not support complete history of many of the less used coins. Take into consideration that the code below is optimized
    for daily scraping of a large quantity of coins and the ingestion of more than 1k days of data per coin might result in long execution time.
"""

from apihistoricprices import *

if __name__ == "__main__":
    print('First ingestion started: ', datetime.now()) # <- used for debugging
    mainscraper=PriceScraper(analyzeddays=400)
    mainscraper.scrapepricedata()