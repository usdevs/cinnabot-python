from datetime import datetime
import logging
from pathlib import Path

import requests
from telegram import (
    Update, 
    KeyboardButton, 
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ParseMode,
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

class PublicBus(Command):

    command = 'publicbus'
    help_text = 'public bus timings for bus stops around your location'
    help_full = ''

    def callback(self, update: Update, context, CallbackContext):
        return

class NUSBus(Conversation):
    """This feels lowkey illegal or something.
    
    NUS next but "API reference": 'https://nextbus.comfortdelgro.com.sg/testMethod.asmx'
    Mysterious imposter endpoint: 'https://better-nextbus.appspot.com'

    The mysterious endpoint follows the official API quite closely. 
    - e.g.: the `GetActiveBus` operation in the original is corresponds to GET https://better-nextbus.appspot.com/ActiveBus?route_code=A1 
    """

    command = 'nusbus'
    help_text = 'NUS bus timings for bus stops around your location.'
    help_full = (
        '/nusbus: NUS bus timings for bus stops around your location.\n'
        '/nusbus location: List of bus timings at your location.\n'
        '/nusbus location bus: Live tracking of a bus until it reaches your stop.'
    )

    # States
    GET_BUS_TIMING = 0

    # maps user arguments to a key recognised by the nusBusStopLocations map
    ALIASES = {
        "kr":    "kr-mrt",
        "yih":   "yih/engin",
        "engin": "yih/engin",
        "Com":   "comp",
    }

    # groups of bus stops that should be returned together
    LOCATIONS = {
        "utown":     ["UTown"],
        "science":   ["S17", "LT27"],
        "kr-mrt":    ["KR-MRT", "KR-MRT-OPP"],
        "mpsh":      ["STAFFCLUB", "STAFFCLUB-OPP"],
        "arts":      ["LT13", "LT13-OPP", "AS7"],
        "yih/engin": ["YIH", "YIH-OPP", "MUSEUM", "RAFFLES"],
        "comp":      ["COM2"],
        "biz":       ["HSSML-OPP", "BIZ2", "NUSS-OPP"],
        "cenlib":    ["COMCEN", "CENLIB"],
        "law":       ["BUKITTIMAH-BTC2"],
    }

    # For location prompt message
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
        """Handles overall conversation flow"""
        return ConversationHandler(
            entry_points = [CommandHandler(self.command, self.entry)],
            states = {
                self.GET_BUS_TIMING: [
                    MessageHandler(Filters.regex(self.KEYBOARD_PATTERN), self._send_location_timings),
                ],
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def refresh(self, update: Update, context: CallbackContext):
        """Handles callbacks from the 'Refresh' button attached to messages"""
        query = update.callback_query
        location = query.data.replace('NUSBus.refresh', '')

        query.edit_message_text(
            text = self._location_timings(location), 
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Refresh', callback_data=f'NUSBus.refresh{location}')]]),
            parse_mode = ParseMode.MARKDOWN,
        )
        query.answer() # Stop loading animation on button

    def entry(self, update: Update, context: CallbackContext):
        """Input validation + delegation to sub-handlers depending on input format"""
        # /nusbus
        if not context.args:
            next_state = self._prompt_location(update, context)
            return next_state
        
        # /nusbus location
        elif (len(context.args) == 1) and (context.args[0].lower() in self.LOCATIONS):
            next_state = self._send_location_timings(update, context)
            return next_state

        # /nusbus location bus
        elif (len(context.args) == 2) and (context.args[0].lower() in self.LOCATIONS):
            next_state = self._send_live_information(update, context)
            return next_state

        # Error
        logging.warning(f'/nusbus unhandled input: {update.message.text}')
        return ConversationHandler.END

    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        text = f'🤖: "{update.message.text}" not recognized'
        update.message.reply_text(text)
            
    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = f'🤖: Function /{self.command} cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def _prompt_location(self, update: Update, context: CallbackContext):
        """Send a keyboard to get user location"""
        text = "🤖: Where are you?"
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton('here', request_location=True)], *self.KEYBOARD],
            resize_keyboard = True,
            one_time_keyboard = True,
            selective = True,
        )
        update.message.reply_text(text, reply_markup=reply_markup)
        return self.GET_BUS_TIMING
    
    def _send_location_timings(self, update: Update, context: CallbackContext):
        """Get bus timings by location from the API and format nicely for the user"""
        # from /nusbus location command
        if context.args:
            location = context.args[0].lower()
        
        # From location keyboard button
        elif update.message.text.lower() in self.LOCATIONS:
            location = update.message.text.lower()

        # From "Here" keyboard button
        else:
            lat = update.message.location.latitude
            lng = update.message.location.longitude
            location = 'utown' # Stub. This should get the nearest location
        
        update.message.reply_text(
            text = '🤖: Getting bus timings...', 
            reply_markup = ReplyKeyboardRemove(),
        )
        
        update.message.reply_text(
            text = self._location_timings(location), 
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Refresh', callback_data=f'NUSBus.refresh{location}')]]),
            parse_mode = ParseMode.MARKDOWN
        )

        return ConversationHandler.END

    def _location_timings(self, location):
        """Calls API and builds message body for location timings"""
        # Execute API calls sequentially 
        # Todo: try async cuz this has a noticeable delay ):
        results = list()
        for bus_stop_name in self.LOCATIONS[location]:
            url = f'https://better-nextbus.appspot.com/ShuttleService?busstopname={bus_stop_name}'
            data = requests.get(url).json()
            results.append(data['ShuttleServiceResult'])

        # Parse data into a nicely formatted message
        lines = []
        for result in results:
            lines.append(f'*{result["name"]}*')
            for shuttle in result['shuttles']:
                bus_name = shuttle['name']
                timing_1 = shuttle["arrivalTime"]
                timing_2 = shuttle["nextArrivalTime"]
                indicator = '🛑' if '-' in timing_1 else '🚍' # Checks for negative timings too
                if timing_1 == "-":
                    lines.append(f'{indicator}{bus_name} : - mins')
                elif timing_1 == "1":
                    lines.append(f'{indicator}{bus_name} : {timing_1} min, {timing_2} mins')
                elif timing_1 == "Arr":
                    lines.append(f'{indicator}{bus_name} : {timing_1}, {timing_2} mins')
                else:
                    lines.append(f'{indicator}{bus_name} : {timing_1} mins, {timing_2} mins')
            lines.append('')
        
        # Add timestamp to let people know the message has been refreshed
        timestamp = datetime.now().strftime('%c') # https://strftime.org/
        lines.append(f'Last updated: {timestamp}')
        
        text = '\n'.join(lines)
        return text 

    def _send_live_information(self, update: Update, context: CallbackContext):
        bus_stop_name, veh_plate = context.args
        data1 = requests.get(f'https://better-nextbus.appspot.com/ShuttleService?busstopname={bus_stop_name}').json()
        data2 = requests.get(f'https://better-nextbus.appspot.com/BusLocation?veh_plate={veh_plate}').json()
        
        update.message.reply_location(
            latitude = data2['BusLocationResult']['lat'], 
            longtitude = data2['BusLocationResult']['lng'],
            heading = data2['BusLocationResult']['direction'],
            live_period = 7*60, # Link this to bus arrival time
            proximity_alert_radius = 100, 
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Come faster la', callback_data=0)]]),
        )
        update.message.reply_text('HAXHAXHAX', reply_markup=ReplyKeyboardRemove())
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
