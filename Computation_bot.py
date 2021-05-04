from datetime import datetime
from telegram.ext import * 
import re

"""
Need in input:
    update every minute of current price 
Requirements:
    need to dispatch the alert based on the value in input 
    need to store multiple user's preferences 
"""

KEY = '1768128147:AAEHVzQup7zLKoEAQPOv7F1sMC-uOO8eeuw'

def sample_responses(input_text):
    
    def extract_coinpct (inputpreference, user_dict):
        substr = inputpreference.split('@')
        if re.match('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[2]):
            foundpct = float(re.findall('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr).pop().rstrip('%'))
            user_dict[substr[0]] = foundpct
        elif re.match('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[2]): #changes only a comma from previous 
            foundpct = float(re.findall('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr).pop().rstrip('%'))
            user_dict[substr[0]] = foundpct
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
                return ('Please start over. Type your preferences with the correct syntax')
        return ('Preferences correctly imported!')
    else:
        try:
            user_preferences = extract_coinpct(preference,user_preferences)
        except:
            return ('Please start over. Type your preferences with the correct syntax')
        return ('Preferences correctly imported!')

    return ('What you just wrote is beyond the scope of our interaction. Be disciplined, use \start and do what I tell you.')


#now = datetime.now()
#'Buongiorno! è {} e ho trovato la percentuale {}'.format(now.strftime('%d/%m/%y, %H:%M:%S'),foundpct)


def start_command(update, context):
    update.message.reply_text('Hello. Please type the percentage of change in price (compared to yesterday\'s closing price in $) above which you want a notification to be pushed')
    update.message.reply_text('This application currently supports five cryptocurrencies: Bitcoin, Ethereum, Ripple, Dogecoin and Binance coin.')
    update.message.reply_text('Please use the following format to specify the coins and percentages you\'re interested in: Coinname1 @ percentage1 ; Coinname2 @ percentage2')

def help_command(update, context):
    update.message.reply_text('Enter command \start to begin.')

def handle_message(update, context):
    text = str(update.message.text).lower() #receive message
    response = sample_responses(text) #process it 
    update.message.reply_text(response) #send response 

def error(update,context):
    print('Update \n {} caused error: \n {}'.format(update, context.error))

def main():
    updater = Updater(KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))
    
    dp.add_handler(MessageHandler(Filters.text, handle_message))

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

main()

print('Bot started')



