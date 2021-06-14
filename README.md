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
A functioning MQTT broker must be setup to use most of the services.
An environment variable called 'BROKER_ADDRESS' should be present with the IP of the broker.
for example: `BROKER_ADDRESS="localhost"`

It is recommended to edit the `/etc/mosquitto/mosquitto.conf` file by inserting these two changes:
```
allow_anonymous true #(the code will work even without this setting, but it's easier to implement and debug new features while if it allows anonymous)
max_inflight_messages 0 #(otherwise it will not function properly in asynchronous mode)
```

### SQL server
A database in Microsoft SQL server should be present for the project to work.
Various environment variables should be present for the code to work flawlessly:
```
# Credentials to access SQL instance on 
SQL_SERVER="<name>.database.windows.net"
SQL_DATABASE=
SQL_USERNAME=
SQL_PASSWORD=
SQL_DRIVER="{ODBC Driver 17 for SQL Server}"
```

As for the needed tables: the code in _database.py_ will generate them automatically if they are not already present in the database.
The two tables will be called _pricehistory_ and _users_.

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
An environment variable called 'KEY' should be present with your API key for telegram bots.
```KEY=123456789abcdefghi```
	
The bot is fairly self-explanatory and should not be difficult for the end user to use.
The users have to input a list of the cryptos they are interested in and the percentage of gains/loss after which they want to be notified. The bot will send a maximum of one notification for crypto for day to not overload the user.


The commands available to the user are:
- *\help* to guide the user to guide the bot
- *\start* to start the bot
- *\stop* to stop the bot
- *\settings* for updating the user preferences
- *\supportedcoins* to know which coins are supported by the bot
	
### Example of how the bot works :
	
Here the user starts the bot.

<img src="https://raw.githubusercontent.com/trelium/crypto_fluctuations/main/data/Telegram%20screenshots/1.jpg" width="20%" height="20%" />

---

The user then states his/her preferences and activates the notification service. 

<img src="https://raw.githubusercontent.com/trelium/crypto_fluctuations/main/data/Telegram%20screenshots/2.jpg" width="20%" height="20%" />

---

After a few minutes, the user receives his/her notifications and after that he/she stops the service to not receive more notifications the day after.

<img src="https://raw.githubusercontent.com/trelium/crypto_fluctuations/main/data/Telegram%20screenshots/3.jpg" width="20%" height="20%" />
