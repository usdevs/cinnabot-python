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
            'I am always here to /help you with what you need!',
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    
class About(Command):

    command = 'about'
    help_text = 'Find out more about me!'
    help_full = '/about links you to the repository for our code (:'

    def callback(self, update: Update, context: CallbackContext):
        text = '\n'.join([
            # text := fmt.Sprintf("Cinnabot %v\n", os.Getenv("COMMITHEAD"))
            # text += fmt.Sprintf("Last updated %v\n", os.Getenv("LASTUPDATED"))
            'Follow this link here: https://github.com/usdevs/cinnabot-python'	
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())


class Help(Command):
    
    command = 'help'
    help_text = 'Let me help you!'
    help_full = '/help to find out what I can do. Try using /help <func name> to see what I can _really_ do!'

    def callback(self, update: Update, context: CallbackContext):
        # Default help text 
        help_dict = context.bot_data['help_text']
        help_text = [f'/{function}: {help}' for function, help in help_dict.items()]
        text = '\n'.join([
            'Here are a list of functions to get you started 🤸',
			*help_text,
			'',
			'Try using /help <func name> for more information about the feature',
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