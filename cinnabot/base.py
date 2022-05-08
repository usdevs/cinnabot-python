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
        help_dict = context.bot_data['help_text']
        help_text = [f'/{function}: {help}' for function, help in help_dict.items()]
        text = '\n'.join([
            f'Hello there NUSC {name}!',
            '',
            'I am Cinnabot🤖, to serve the residents of NUS College!',
        ])
        text += '\n'.join([
            ' Here are a some things I can do for you!\n',
			*help_text,
			'',
			'Use /help <feature name> for more details!',
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())

    
class About(Command):

    command = 'about'
    help_text = 'Useful links for NUS and NUSC!'
    help_full = '/about links you to the repository for our code (:'

    def callback(self, update: Update, context: CallbackContext):
        text = '\n'.join([
            '🤖: Here are the links you may need:',
            '',
            'LumiNUS: https://luminus.nus.edu.sg/',
            'EduRec: https://myedurec.nus.edu.sg/',
            'NUSMods: https://nususc.com/',
            'NUSC Web: https://nuscollege.nus.edu.sg/',
            'USC Web: https://nususc.com/',
            '',
            '🤖: Here are the apps you may need:',
            '',
            'uNivUS: ',
            'Google Play - https://play.google.com/store/apps/details?id=sg.edu.nus.univus',
            'App Store - https://apps.apple.com/us/app/univus/id1508660612',
            '',
            'NUS Hostel Dining: ',
            'Google Play - https://play.google.com/store/apps/details?id=com.neseapl.nus.dining.system',
            'App Store - https://apps.apple.com/gb/app/nus-hostel-dining/id1519951130',
            '',
            'NUS NextBus: ',
            'Google Play - https://play.google.com/store/apps/details?id=nus.ais.mobile.android.shuttlebus',
            'App Store - https://apps.apple.com/sg/app/nus-nextbus/id542131822',
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())


class Help(Command):
    
    command = 'help'
    help_text = 'Let me help you!'
    help_full = 'Use /help <feature name> for more details!'

    def callback(self, update: Update, context: CallbackContext):
        help_dict = context.bot_data['help_text']
        help_text = [f'/{function}: {help}' for function, help in help_dict.items()]
        text = '\n'.join([
            'Here are a some things I can do for you!',
			*help_text,
			'',
			'Use /help <feature name> for more details!',
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