# Cryptocurrency Telegram Price Fluctuation Notifier and Predictor 

 * Design and implement a big data system for detecting and predicting sudden variations (> X% on a daily basis) for a set of cryptocurrencies. 

## Project overview
- This project scrapes the closing price history of all the most used cryptos. 
- The prices are then processed in different ways:
  - A model is used to predict the current day closing price for each given crypto.
  - The current price of each crypto is scraped every minute, compared to the previous day price and a percentage of change in price is calculated for each crypto.
- Particular care has been given to the serving layer: a fully-functioning telegram bot that is capable of storing the user preferences and sends notifications based on those preferences.


### How the code works in detail:

It is recommended to consult the [project wiki](https://github.com/trelium/crypto_fluctuations/wiki) for more informations if the user wants to use or enchance the code.


## Usage

### Environment

This project requires Python 3.


### Requirements

The libraries defined in the `requirements.txt` file should be installed.

```bash
pip install -r requirements.txt
```
