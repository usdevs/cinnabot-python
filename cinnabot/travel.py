import logging
from pathlib import Path

from telegram import (
    Update, 
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
)
from telegram.ext import (
    CallbackContext, 
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    Filters,
)

from cinnabot import Command, Conversation

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

# '/weather: 2h weather forecast',
# '/spaces: list of space bookings',
# '/feedback: to give feedback',
# '/laundry: to check washer and dryer availability in cinnamon',

class PublicBus(Conversation):

    command = 'publicbus'
    help_text = 'public bus timings for bus stops around your location'
    help_full = (
        '/publicbus: Public bus timings for bus stops around your location.'
    )
    # Public bus json api: https://datamall.lta.gov.sg/content/dam/datamall/datasets/PublicTransportRelated/BusArrival.zip
    
    # States
    GET_BUS_TIMING, UNIVERSITY_TOWN, NEW_TOWN_SEC_SCH, AFT_DOVER_RD, AFT_CLEMENTI_AVE_1 = range(5)
    
    # Bus stop codes
    Bus_Stop_Code = {UNIVERSITY_TOWN : 19059,
                     NEW_TOWN_SEC_SCH : 19051,
                     AFT_DOVER_RD : 17099,
                     AFT_CLEMENTI_AVE_1 : 17091,
                     
                     }

    # Class helper variables
    KEYBOARD = [
        ['University Town', 'New Town Sec Sch'],
        ['Aft Dover Rd', 'Aft Clementi Ave 1'],
    ]

    TAGS = [button for row in KEYBOARD for button in row]

    KEYBOARD_PATTERN = '^(' + '|'.join(TAGS) + ')$' # Regex to match all valid replies

    @property
    def handler(self):
        return ConversationHandler(
            entry_points = [CommandHandler(self.command, self.entry)],
            states = {
                self.GET_BUS_TIMING: [MessageHandler(Filters.regex(self.KEYBOARD_PATTERN), self.get_bus_timing)],
                self.UNIVERSITY_TOWN: [MessageHandler(Filters.text, self.get_bus_timing)],
                self.NEW_TOWN_SEC_SCH: [MessageHandler(Filters.text, self.get_bus_timing)],
                self.AFT_DOVER_RD: [MessageHandler(Filters.text, self.get_bus_timing)],
                self.AFT_CLEMENTI_AVE_1: [MessageHandler(Filters.text, self.get_bus_timing)],
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def entry(self, update: Update, context: CallbackContext):
        text = "🤖: Where are you?"
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton('here', request_location=True)], *self.KEYBOARD],
            resize_keyboard = True,
            one_time_keyboard = True,
            selective = True,
        )
        update.message.reply_text(text, reply_markup=reply_markup)
        return self.GET_BUS_TIMING

    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        text = f'🤖: "{update.message.text}" not recognized'
        update.message.reply_text(text)
        return self.GET_BUS_TIMING

    def get_bus_timing(self, update: Update, context: CallbackContext):
        """Handles bus timings"""
        print(dir(self))
        text = "Successfully triggered"
        update.message.reply_text(text)
        return self.GET_BUS_TIMING

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = f'🤖: Function /{self.command} cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
        
class NUSBus(Conversation):

    command = 'nusbus'
    help_text = 'NUS bus timings for bus stops around your location.'
    help_full = (
        '/nusbus: NUS bus timings for bus stops around your location.'
    )

    # States
    GET_BUS_TIMING = 0

    # Class helper variables
    KEYBOARD = [
        ['Utown', 'Science'],
        ['Arts', 'Comp'],
        ['CenLib', 'Biz'],
        ['Law', 'Yih/Engin'],
        ['MPSH', 'KR-MRT'],
    ]

    TAGS = [button for row in KEYBOARD for button in row]

    KEYBOARD_PATTERN = '^(' + '|'.join(TAGS) + ')$' # Regex to match all valid replies

    @property
    def handler(self):
        return ConversationHandler(
            entry_points = [CommandHandler(self.command, self.entry)],
            states = {
                self.GET_BUS_TIMING: [

                ],
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def entry(self, update: Update, context: CallbackContext):
        text = "🤖: Where are you?"
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton('here', request_location=True)], *self.KEYBOARD],
            resize_keyboard = True,
            one_time_keyboard = True,
            selective = True,
        )
        update.message.reply_text(text, reply_markup=reply_markup)
        return self.GET_BUS_TIMING
    
    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        text = f'🤖: "{update.message.text}" not recognized'
        update.message.reply_text(text)
        return self.GET_BUS_TIMING

    def get_bus_timing(self, update: Update, context: CallbackContext):
        """Ends the user flow by sending a message with the desired resources and removing the keyboard."""
        logger.info('get_resources')
        text = '🤖: Link this to firebase! The current json solution is not the best ):'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = f'🤖: Function /{self.command} cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

class NUSMap(Conversation):

    command = 'map'
    help_text = 'to get a map of NUS if you\'re lost!'
    help_full = (
        '/map: to get a map of NUS if you\'re lost!'
    )

    # States
    GET_MAP = 0

    # Class helper variables
    KEYBOARD = [
        ['Arts', 'Comp'],
        ['Law', 'Biz'],
        ['UTown', 'Science'],
        ['SDE', 'YIH/Engin'],
    ]

    NUSMODS_URLS = {
        "arts": "https://nusmods.com/venues/AS4-0602",
        "comp": "https://nusmods.com/venues/COM1-0120",
        "law": "https://nusmods.com/venues" + "\n\n PS: Law venues are available under 'L'!",
        "biz": "https://nusmods.com/venues/BIZ2-0115",
        "utown": "https://nusmods.com/venues/UT-AUD2",
        "science": "https://nusmods.com/venues/S8-0314",
        "sde": "https://nusmods.com/venues/SDE-ER4",
        "yih/engin": "https://nusmods.com/venues/E3-05-21",
    }

    IMAGE_URLS = {
        "arts": Path("cinnabot", "maps", "FASS Map.png"),
        "comp": Path("cinnabot", "maps", "Computing Map.png"),
        "law": Path("cinnabot", "maps", "Law Map.png"),
        "biz": Path("cinnabot", "maps", "Biz Map.png"),
        "utown": Path("cinnabot", "maps", "UTown Map.png"),
        "science": Path("cinnabot", "maps", "Science Map.png"),
        "sde": Path("cinnabot", "maps", "SDE Map.png"),
        "yih/engin": Path("cinnabot", "maps", "Engineering Map.png"),
    }

    TAGS = [button for row in KEYBOARD for button in row]

    KEYBOARD_PATTERN = '^(' + '|'.join(TAGS) + ')$' # Regex to match all valid replies

    @property
    def handler(self):
        return ConversationHandler(
            entry_points = [CommandHandler(self.command, self.entry)],
            states = {
                self.GET_MAP: [MessageHandler(Filters.regex(self.KEYBOARD_PATTERN), self.get_map)]
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def entry(self, update: Update, context: CallbackContext):
        logger.info('/map')
        text = "🤖: Where are you?"
        reply_markup = ReplyKeyboardMarkup(
            self.KEYBOARD,
            resize_keyboard = True,
            one_time_keyboard = True,
            selective = True,
        )
        update.message.reply_text(text, reply_markup=reply_markup)
        return self.GET_MAP
    
    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        text = f'🤖: "{update.message.text}" not recognized'
        update.message.reply_text(text)
        return self.GET_MAP

    def get_map(self, update: Update, context: CallbackContext):
        """Ends the user flow by sending a message with the desired map and removing the keyboard."""
        logger.info('get_map')
        
        location = update.message.text.lower()
        name = update.message.from_user.first_name
        with open(self.IMAGE_URLS[location], 'rb') as image:
            text = '\n'.join([
                f'🤖: Hey {name}, heard of NUSMODs ?',
                '',
                'It is a student intiative made to improve the lives of students!',
                'They also have a function to help you find your way around!',
                'Click on the link below!',
                '',
                self.NUSMODS_URLS[location],
            ])
            update.message.reply_photo(photo=image, caption=text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = f'🤖: Function /{self.command} cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
