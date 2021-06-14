# Cryptocurrency Telegram Price Fluctuation Notifier and Predictor 

 * Design and implement a big data system for detecting and predicting sudden variations (> X% on a daily basis) for a set of cryptocurrencies. 


##### Table of Contents  
* [Project overview](#overview)  
* [Usage](#usage) 
* [Running the code](#running)
* [Telegram Bot](#telegram)

<a name="overview"/>

-------

## Project overview
- This project scrapes the closing price history of all the most used cryptos. 
- The prices are then processed in different ways:
  - A model is used to predict the current day closing price for each given crypto.
  - The current price of each crypto is scraped every minute, compared to the previous day price and a percentage of change in price is calculated for each crypto.
- Particular care has been given to the serving layer: a fully-functioning telegram bot that is capable of storing the user preferences and sends notifications based on those preferences.


### How the code works in detail:

It is recommended to consult the [project wiki](https://github.com/trelium/crypto_fluctuations/wiki) for more informations if the user wants to use or enchance the code.

<a name="usage"/>

------

## Usage

# TODO: Sta roba va modificata dopo il docker

### Environment

This project requires Python 3.


### Requirements

The libraries defined in the `requirements.txt` file should be installed.

```bash
pip install -r requirements.txt
```

### Questi due non credo serva dockerizzarli:

### MQTT broker
serve un mqtt

### SQL server
serve un microsoft sql server

--------

<a name="running"/>


## Running the code

This project offers different services that can be run separately:
* These two services should be run once a day:
	* _apihistoricprices.py_ is used to scrape the price histories and publishes the in a customized 	scraper/<name of the crypto> topic
	* _historicingestion.py_ subscribes to the aforementioned topics and loads the data in a Microsoft SQL 	Server table

* These three services will run until manually stopped:
	* _apicurrentpercentages.py_ calculates the daily price percentage change of each crypto and sends them in 	a 	"percentagechange" MQTT Topic
	* _notifier.py_ subscribes to the "percentagechange" topic, filters which user should be notified and 	sends the notifications.
	* _servinglayer.py_ is used to start the telegram bot.

The MQTT services run at QOS 1, as such they can be run synchronously or asynchronously.

The other services, _predictor.py_,_projecttoolbox.py_ and _database.py_ , manage some back-end processes and as such it is not necessary for the user to run them.
The 

<a name="telegram"/>
	
-------

## Telegram Bot tutorial and examples:
