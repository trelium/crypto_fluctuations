import requests
import json


response = requests.get("https://api.coingecko.com/api/v3/coins/bitcoin/history?date=30-12-2017")
response=response.json()
print(response)

print('ho modificato il file dalla macchina virtuale')
print(len(response))

#at every update, check for each user that has user[state]=started what are the assiciated preferences and, if needed, push a message.

#come si manda un messaggio ad un utente specifico senza che sia questo a utente a richiedere qualcosa? con il chat_id
import telegram 
bot = telegram.Bot(token=token)
bot.sendMessage(chat_id=chat_id, text=msg)

#chat_id, user_id, state, preference 