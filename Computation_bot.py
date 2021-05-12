from datetime import datetime
from telegram.ext import * 
import re
import mysql.connector
from Requester import UtentiSQL

"""
Need in input:
    update every minute of current price 
Requirements:
    need to dispatch the alert based on the value in input 
    need to store multiple users' preferences 
"""

#keys need to be stored out of code: solution 1 is to encrypt the strings and save the encrypted version in a file. The python script needs to have a key for decoding. 
#solution 2 is to simpy create a file where they are written clear-text. store your passwords unencrypted on disk, protected only by filesystem permissions. If this is not an acceptable security tradeoff,
#solution 3 is using keyring
KEY = '1768128147:AAEHVzQup7zLKoEAQPOv7F1sMC-uOO8eeuw'

db = UtentiSQL()

def setting_routine(input_text):
    def extract_coinpct (inputpreference, user_dict):
        allowedcoins = set('bitcoin', 'ripple', 'ethereum','binancecoin','dogecoin')
        substr = inputpreference.split('@')
        if re.match('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1].replace(' ','')):
            foundpct = float(re.findall('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%'))
            coinname = substr[0].replace(' ','')
            if coinname in allowedcoins:
                user_dict[coinname] = foundpct
            else:
                return ValueError
        elif re.match('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[1].replace(' ','')): #changes only a comma from previous regex
            foundpct = float(re.findall('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%'))
            coinname = substr[0].replace(' ','')
            if coinname in allowedcoins:
                user_dict[coinname] = foundpct
            else:
                return ValueError
        else:
            return ValueError 
        return user_dict

    user_preferences = dict()
    user_message = str(input_text).lower()

    if ';' in user_message: 
        user_message = user_message.split(';')
        for preference in user_message:
            try:
                user_preferences = extract_coinpct(preference,user_preferences)
            except:
                return ('Please start over. Type your preferences with the correct syntax', {})
        return ('Preferences correctly imported!', user_preferences)
    else:
        try:
            user_preferences = extract_coinpct(preference,user_preferences)
        except:
            return ('Please start over. Type your preferences with the correct syntax', {})
        return ('Preferences correctly imported!', user_preferences)


def start_command(update, context):
    user = update.message.from_user
    if db.get_state(chat = str(update.message.chat.id)) == 'No state':
        settings_command(update, context)
    elif db.get_state(chat = str(update.message.chat.id)) == False:
        update.message.reply_text('Error starting service. Please contact the admin')
    elif db.get_active(chat = str(update.message.chat.id)) == 1:
        update.message.reply_text('Service already running!')
    elif db.get_active(chat = str(update.message.chat.id)) == 0:
        db.set_active(chat = str(update.message.chat.id))
    else:
        update.message.reply_text('Error starting service(cannot set state to active). Please contact the admin')


def settings_command(update, context): #proper way to do this would be to use a conversationHandler 
    if db.set_state(chat = str(update.message.chat.id), user = str(update.message.from_user), state = 'settings'):
        update.message.reply_text('Please type the percentage of change in price (compared to yesterday\'s closing price in $) above which (or below which, prepend - sign) you want a notification to be pushed')
        update.message.reply_text('This application currently supports five cryptocurrencies: Bitcoin, Ethereum, Ripple, Dogecoin and Binance coin.')
        update.message.reply_text('Please use the following format to specify the coins and percentages you\'re interested in: Coinname1 @ percentage1 ; Coinname2 @ percentage2')
    else:
        update.message.reply_text('Error updating preferences. Please contact the admin')    
    

def stop_command(update, context):
    #set user state to stopped
    if db.set_state(chat = str(update.message.chat.id), user = str(update.message.from_user), state = 'stopped'): #TODO should edit the active field instead
        update.message.reply_text('Service stopped. To resume receiving notifications with current settings, enter command \start')
    else:
        update.message.reply_text('Error stopping the service. Please contact the admin')

def help_command(update, context):
    #return message of welcome
    update.message.reply_text('Enter command \start to begin.')

def handle_message(update, context):
    text = str(update.message.text).lower() #receive message
    if db.get_state(chat = str(update.message.chat.id)) == 'setting':
        response, dizionario = setting_routine(text) #process it 
        update.message.reply_text(response) #send response 
        if len(dizionario) != 0:
            db.set_preferences(chat = str(update.message.chat.id), preferences = dizionario)
    else: 
        update.message.reply_text('To input new preferences, first issue command \settings')

def error(update,context):
    print('Update \n {} \n  caused error: \n {}'.format(update, context.error))

def main():
    print('Bot started')
    updater = Updater(KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('stop', stop_command))
    dp.add_handler(CommandHandler('settings', settings_command))
    
    dp.add_handler(MessageHandler(Filters.text, handle_message))#only passes updates to the callback if filtered as text

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()



#now = datetime.now()
#'Buongiorno! è {} e ho trovato la percentuale {}'.format(now.strftime('%d/%m/%y, %H:%M:%S'),foundpct)

