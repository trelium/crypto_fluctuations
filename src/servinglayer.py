"""
----------------------------------------------------------------
---- Telegram Bot Serving Layer for Cryptocurrency Predictor----
---------------------------------------------------------------- 
Developed by Jacopo Mocellin, Riccardo Improta 
University of Trento - June 2021.

---- Description----
Script taking care of the interaction with the end user for the Cryptocurrency Predictor.
Functionalities include:
    * Acquiring price prediction preferences from the user 
    * Setting persistent states and settings for each user  

"""

from telegram.ext import * 
import re
from database import UsersSQL
from projecttoolbox import sanitizecoininput
from dotenv import load_dotenv
import os

#Get credentials to manage Telegram bot 
load_dotenv()
KEY = os.environ.get("KEY")

#Instantiate database interface 
db = UsersSQL()

def setting_routine(input_text):
    errorcoin = None
    def extract_coinpct (inputpreference, user_dict):
        substr = inputpreference.split('@')
        if ',' not in  substr[1] and re.match('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1].replace(' ','')):
            foundpct = float(re.findall('-{0,1}[0-9]+\.{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%'))
        elif '.' not in  substr[1] and re.match('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[1].replace(' ','')): #changes only a comma from previous regex
            foundpct = float(re.findall('-{0,1}[0-9]+,{0,1}[0-9]*%{0,1}', substr[1]).pop().rstrip('%').replace(',','.'))
        else:
            raise ValueError 
        coinname = substr[0].replace(' ','') #remove trailing whitespace, if any
        try:
            coinname = sanitizecoininput(coinname,dbinstance=db)[0] 
            user_dict[coinname] = foundpct
            return user_dict
        except:
            nonlocal errorcoin
            errorcoin = substr[0]
            raise ValueError
        
    user_preferences = dict()
    user_message = str(input_text).lower()#remove trailing ; , if any


    user_message=user_message.replace(',',';') # Useful if the users puts in ',' instead of ';' 
    # # Converts the word in a list and iterates through it. It then substitutes
    #  ";" with '.' whenever the letter right after the one we are analyzing is numeric.
    list_user_message=list(user_message)
    for index,letter in enumerate(list_user_message): #iterates through the list
        if letter==';':        
            if (index+1)==len(list_user_message):
                continue
            
            #we only convert ";" to "." if the character right after it is numeric 
            if list_user_message[index+1].isnumeric():
                list_user_message[index]='.'
    user_message="".join(list_user_message)   

    user_message=user_message.rstrip(';')#remove trailing, if any
    

    if ';' in user_message: 
        user_message = user_message.split(';')
    else:
        user_message = [user_message]
    for preference in user_message:
        try:
            user_preferences = extract_coinpct(preference,user_preferences)
        except:
            if errorcoin != None:
                return (f'The coin "{errorcoin}" is currently unsupported. No preferences were set, you may issue the /settings command again', {}) 
            else:
                return (f'Please, type your preferences using the correct syntax.', {})
    return ('Preferences correctly imported!', user_preferences)
    

def start_command(update, context):
    user = update.message.from_user
    if not db.is_already_present(chat = str(update.message.chat.id)) or db.get_state(chat = str(update.message.chat.id)) == 'settings': 
        settings_command(update, context)
    elif db.get_state(chat = str(update.message.chat.id)) == False:
        update.message.reply_text('Error starting service. Please contact the admin')
    elif db.get_active(chat = str(update.message.chat.id)) == 1:
        update.message.reply_text('Service already running!')
    elif db.get_active(chat = str(update.message.chat.id)) == 0 and db.get_state(chat = str(update.message.chat.id)) == 'ready':
        db.set_active(chat = str(update.message.chat.id), value = 1)
        update.message.reply_text(u'Service launched \U0001F680')
    else:
        update.message.reply_text('Error starting service(cannot set state to active). Please contact the admin')

def settings_command(update, context): 
    if db.set_state(chat = str(update.message.chat.id), user = str(update.message.chat.username), state = 'settings') != False:
        if db.get_active(chat = str(update.message.chat.id)) == 1:
            stop_command(update, context)
        update.message.reply_text('Please type the percentage of change in price (compared to yesterday\'s closing price in $). The Bot will send you a notification whenever the price goes above or below your desired percentage of change.')
        update.message.reply_text('Please use the following format to specify the coins and percentages you\'re interested in: Coinname1 @ percentage1 , Coinname2 @ percentage2 , ...')
        update.message.reply_text('For example, these different ways of formatting are all accepted: _ bitcoin @2\.2%, eth @ 5,6% , xrp @1% _ ',parse_mode='MarkdownV2')
        update.message.reply_text('To get a list of currently supported coins, issue command /supportedcoins')
        update.message.reply_text('If you want to modify your preferences later, use /settings')
    else:
        update.message.reply_text('Error updating preferences. Please contact the admin') 
  
def stop_command(update, context):
    #set user state to stopped
    if db.set_active(chat = str(update.message.chat.id), value = 0):
        update.message.reply_text('Service stopped. To resume receiving notifications with current settings, enter command /start')
    else:
        update.message.reply_text('Error stopping the service. Please contact the admin')

def help_command(update, context):
    #return message of welcome
    update.message.reply_text('Enter command /start to begin.')

def supported_coins(update,context):
    update.message.reply_text('This is a list of currently supported coins:')
    update.message.reply_text('\n'.join(db.get_coins_in_table()))

def handle_message(update, context):
    text = str(update.message.text).lower() #receive message
    if db.get_state(chat = str(update.message.chat.id)) == 'settings':
        response, dizionario = setting_routine(text) #process it 
        update.message.reply_text(response) #send response 
        if len(dizionario) != 0:
            db.set_preferences(chat = str(update.message.chat.id), preferences = dizionario) 
            #print(update.message.chat.username) #debug only
            db.set_state(chat = str(update.message.chat.id), user = str(update.message.chat.username), state = 'ready')
            update.message.reply_text('You are ready to receive notifications. Issue command /start to activate the service. A maximum of one notification for crypto will be sent each day.') 
    else: 
        update.message.reply_text('To input new preferences, first issue command /settings')

def error(update,context):
    print('Update \n {} \n  caused error: \n {}'.format(update, context.error))

def main(): #Note: conversationHandler 
    print('Bot started')
    updater = Updater(KEY, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler('start', start_command))
    dp.add_handler(CommandHandler('help', help_command))
    dp.add_handler(CommandHandler('stop', stop_command))
    dp.add_handler(CommandHandler('supportedcoins', supported_coins))
    dp.add_handler(CommandHandler('settings', settings_command))
    
    dp.add_handler(MessageHandler(Filters.text, handle_message))#only passes updates to the callback if filtered as text

    dp.add_error_handler(error)

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

