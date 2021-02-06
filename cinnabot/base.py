import logging

from telegram import Update, ParseMode, ReplyKeyboardRemove, replymarkup
from telegram.ext import CallbackContext

from cinnabot import Command


class Start(Command):

    command = 'start'
    help_text = 'to reset me'
    help_full = '/start restarts your session with cinnabot. Useful if I bug out somehow!'
    
    def callback(self, update: Update, context: CallbackContext):
        name = update.message.from_user.first_name
        text = '\n'.join([
            f'Hello there {name}!',
            '',
            'Im Cinnabot🤖. I am made by my owners to serve the residents of Cinnamon college!',
            'Im always here to /help if you need it!',
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    
class About(Command):

    command = 'about'
    help_text = 'to find out more about me'
    help_full = '/about links you to the repository for our code. Pull Requests always appreciated (:'

    def callback(self, update: Update, context: CallbackContext):
        text = '\n'.join([
            # text := fmt.Sprintf("Cinnabot %v\n", os.Getenv("COMMITHEAD"))
            # text += fmt.Sprintf("Last updated %v\n", os.Getenv("LASTUPDATED"))
            'Touch me: https://github.com/usdevs/cinnabot'	
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())


class Help(Command):
    
    command = 'help'
    help_text = 'to find out what I can do'
    help_full = '/help to find out what I can do. Try using /help <func name> to see what I can _really_ do!'

    def callback(self, update: Update, context: CallbackContext):
        # Default help text 
        help_dict = context.bot_data['help_text']
        help_text = [f'/{function}: {help}' for function, help in help_dict.items()]
        text = '\n'.join([
            'Here are a list of functions to get you started 🤸',
			*help_text,
			'',
			'_*My creator actually snuck in a few more functions🕺 *_',
			'Try using /help <func name> to see what I can _really_ do',
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