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
            f'How may I help you NUSC {name}?',
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
            '🤖: Here are some NUS links you may need:',
            '',
            '<a href="https://luminus.nus.edu.sg/">LumiNUS</a>',
            '<a href="https://myedurec.nus.edu.sg/">EduRec</a>',
            '<a href="https://nususc.com/">NUSMods</a>',
            '<a href="https://www.usp.nus.edu.sg/curriculum/module-timetable/">USP Academic Semester Timetable</a>',
            '<a href="https://nuscollege.nus.edu.sg/">NUSC Web</a>',
            '<a href="https://nususc.com/">USC Web</a>',
            '<a href="https://uhms.nus.edu.sg/StudentPortal/6B6F7C08/8/238/Home-Home_">UHMS Portal</a>'
            '',
            '',
            '🤖: Here are some NUS apps you may need:',
            '',
            'uNivUS: ',
            '<a href="https://play.google.com/store/apps/details?id=sg.edu.nus.univus">Google Play</a>',
            '<a href="https://apps.apple.com/us/app/univus/id1508660612">App Store</a>',
            '',
            'NUS Hostel Dining: ',
            '<a href="https://play.google.com/store/apps/details?id=com.neseapl.nus.dining.system">Google Play</a>',
            '<a href="https://apps.apple.com/gb/app/nus-hostel-dining/id1519951130">App Store</a>',
            '',
            'NUS NextBus: ',
            '<a href="https://play.google.com/store/apps/details?id=nus.ais.mobile.android.shuttlebus">Google Play</a>',
            '<a href="https://apps.apple.com/sg/app/nus-nextbus/id542131822">App Store</a>',
            '',
            'NUS ResLife: ',
            '<a href="https://play.google.com/store/apps/details?id=com.guidebook.apps.NUSResLife.android&hl=en_SG">Google Play</a>',
            '<a href="https://apps.apple.com/sg/app/nus-residential-life/id1142053403">App Store</a>',
            '',
            '🤖: Here are some NUSC social media links you may need:',
            '',
            'NUSC:',
            '<a href="https://www.instagram.com/nuscollege/?hl=en">Instagram</a>',
            '<a href="https://www.youtube.com/channel/UC0m6Dvm5ZrQztv9sngQMOCw/featured">YouTube</a>',
            '<a href="https://www.facebook.com/nuscollege/">Facebook</a>',
            '<a href="https://www.linkedin.com/company/nus-college/about">LinkedIn</a>',
            '',                        
        ])
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove(), parse_mode=ParseMode.HTML)


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