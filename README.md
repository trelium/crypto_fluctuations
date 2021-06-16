# Cryptocurrency Telegram Price Fluctuation Notifier and Predictor 
Developed by Jacopo Mocellin, Riccardo Improta

University of Trento - June 2021

--------

This project constitutes the final deliverable for the Big Data Technologies course at the University of Trento, academic year 2020/2021.

Our paper _Cryptocurrency Price Fluctuation: Notifier and Predictor_ related to this repository is available [here](https://drive.google.com/file/d/1-b_b9m72kj7jU8a2b-01yuguExlbMr-j/view?usp=sharing)

Project objective:
 * Design and implement a big data system for detecting and predicting sudden variations (> X% on a daily basis) for a set of cryptocurrencies. 

--------

##### Table of Contents  
* [Project overview](#overview)  
* [Usage](#usage) 
* [Telegram Bot](#telegram)

<a name="overview"/>

-------

## Project overview
In this project, we developed a near-real-time notification system served via a Telegram bot. The user interacts with it in order to set alert thresholds for different cryptocurrencies. An alert threshold is a percentage price value that refers to a currency's quotation at a given moment in time, with respect to the previous day's closing price. Once thresholds are set, the bot updates the user whenever the price for one of the coins he set thresholds for raises above of falls below the (absolute) threshold value. The sent notificaiton message includes the current price as well as our prediction regarding today's closing, expressed as binary outcome.

Behind the scenes, things go like this:
- Once a day, the service ingests the most recent closing prices for the 50 most popular cryptos. 
  - A model predicts the current day closing price for each given crypto, considering also the newly ingested data.
- The current price of each crypto is ingested every minute:
  - It is compared to the previous day's price to compute the percentage of change.
  - These percentage changes are compared to the user preferences to identify which users need to be currently notified.


### How the code works in detail:

It is recommended to consult the [project wiki](https://github.com/trelium/crypto_fluctuations/wiki/Crypto_fluctuations-wiki) for more informations if the user wants to use or enchance the code.

<a name="usage"/>

------

## Usage

To use this code, it is suggested to rely on the Dockerfile, which is an image that will run all the scripts correctly.
If you want to run the code without relying on the Docker Image, it is suggested to consult The [running the code](https://github.com/trelium/crypto_fluctuations/wiki/Crypto_fluctuations-wiki#running) section of the wiki.

In either case, a working installation of the Eclipse MQTT broker and of the Microsoft ODBC driver are needed to run the code. More details about how to configure these two services are presented in the next two sections. We suggest to consult the official documentation of [MQTT](https://mosquitto.org/download/) and [Microsoft ODBC driver](https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server?view=sql-server-ver15) to correctly install these two services. 
Note that here we assume you have access to a Microsoft SQL server (remotely as Azure SQL database or elsewhere): in case you do not, you'll also need to install the [Microsoft SQL Server](https://docs.microsoft.com/en-us/sql/database-engine/install-windows/install-sql-server?view=sql-server-ver15) software to have a local database to work with. 

Also, a `.env` file is always needed to run the code and should be inserted in the main folder "crypto_fluctuations". This file should be formatted in this way:
```
# Credentials to access SQL instance on 
SQL_SERVER="..."
SQL_DATABASE="..."
SQL_USERNAME="..."
SQL_PASSWORD="..."
SQL_DRIVER="{ODBC Driver 17 for SQL Server}"


# Credentials to access Telegram bot configuration 
KEY = "123456789abcdefghi"

# MQtt broker address
BROKER_ADDRESS="localhost" (or any IP)
```

### MQTT broker
A functioning MQTT broker must be setup on your system to use most of the services.
An environment variable called 'BROKER_ADDRESS' should be present with the IP of the broker.
for example: `BROKER_ADDRESS="localhost"`

It is recommended to edit the `/etc/mosquitto/mosquitto.conf` file by inserting these two changes:
```
allow_anonymous true #(the code will work even without this setting, but it's easier to implement and debug new features while if it allows anonymous)
max_inflight_messages 0 #(otherwise it will not function properly in asynchronous mode)
```

### SQL server
A database in Microsoft SQL server should be present for the project to work.
As for the needed tables, the code in _database.py_ will generate them automatically if they are not already present in the database.
The two tables will be called _pricehistory_ and _users_.



<a name="telegram"/>
	
-------

## Telegram Bot tutorial and examples:
An environment variable called 'KEY' should be present with your API key for telegram bots.
```KEY=123456789abcdefghi```
	
The bot is fairly self-explanatory and should not be difficult for the end user to use.
The users have to input a list of the cryptos they are interested in and the percentage of gains/loss after which they want to be notified. The bot will send a maximum of one notification for crypto per day to not overload the user.


The commands available to the user are:
- *\help* to guide the user to start the bot
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


