import logging

from telegram import Update, ParseMode, ReplyKeyboardRemove, replymarkup
from telegram.ext import CallbackContext

from cinnabot import Command


class Start(Command):

    command = 'start'
    help_text = 'Reset me!'
    help_full = '/start restarts your session with cinnabot. Useful if I bug out somehow!'
    
    def callback(self, update: Update, context: CallbackContext):
        name = update.message.from_user.first_name
        text = '\n'.join([
            f'Hello there {name}!',
            '',
            'I am Cinnabot🤖, made by my owners to serve the residents of Cinnamon College!',
            'Let me /help you with what you need!',
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    
class About(Command):

    command = 'about'
    help_text = 'Links about USP and NUS!'
    help_full = '/about links you to the repository for our code (:'

    def callback(self, update: Update, context: CallbackContext):
        text = '\n'.join([
            # text := fmt.Sprintf("Cinnabot %v\n", os.Getenv("COMMITHEAD"))
            # text += fmt.Sprintf("Last updated %v\n", os.Getenv("LASTUPDATED"))
            '🤖: Here are the relevant links you need:',
            '',
            'Repository: https://github.com/usdevs/cinnabot-python', 
            'USC Website: https://nususc.com/',
            'Luminus: https://luminus.nus.edu.sg/',
            'EduRec: https://myedurec.nus.edu.sg/',
            'NUSMods: https://nususc.com/',
            'uNivUS: ',
            'Google Play - https://play.google.com/store/apps/details?id=sg.edu.nus.univus',
            'App Store - https://apps.apple.com/us/app/univus/id1508660612',
            'NUS Hostel Dining: ',
            'Google Play - https://play.google.com/store/apps/details?id=com.neseapl.nus.dining.system',
            'App Store - https://apps.apple.com/gb/app/nus-hostel-dining/id1519951130',
            'NUS NextBus: ',
            'Google Play - https://play.google.com/store/apps/details?id=nus.ais.mobile.android.shuttlebus',
            'App Store - https://apps.apple.com/sg/app/nus-nextbus/id542131822',
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())


class Help(Command):
    
    command = 'help'
    help_text = 'Let me help you!'
    help_full = 'Use /help <feature name> for more information!'

    def callback(self, update: Update, context: CallbackContext):
        # Default help text 
        help_dict = context.bot_data['help_text']
        help_text = [f'/{function}: {help}' for function, help in help_dict.items()]
        text = '\n'.join([
            'Here are a list of functions to get you started 🤸',
			*help_text,
			'',
			'Use /help <feature name> for more information!',
        ])

        # Return full user guide if user wants help for a specific function
        if len(context.args) > 0:
            func_name = context.args[0]
            help_dict = context.bot_data['help_full']
            
            # Overwrite reply text with specific help text
            if func_name in help_dict:
                text = help_dict[func_name]
            
            # Add an error message before the default help text
            else:
                text = '\n'.join([
                    f'{func_name} is not a cinnabot function!',
                    '',
                    text,
                ])
        
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.MARKDOWN)