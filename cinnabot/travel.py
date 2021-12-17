from datetime import datetime
import heapq
import json
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
    help_text = 'NUS bus timings near your location!'
    help_full = (
        '/nusbus: NUS bus timings for bus stops around your location.\n'
        '/nusbus location: List of bus timings at your location.\n'
        '/nusbus location bus: Live tracking of a bus until it reaches your stop. (WIP)'
    )

    # Number of seconds before API request times out
    TIMEOUT = 3.0

    # States
    GET_BUS_TIMINGS = 0

    # list of bus stops and their locations
    with Path('cinnabot', 'travel', 'nusstops.json').open('r') as f:
        BUS_STOPS = json.load(f)

    # maps user arguments to a key recognised by the nusBusStopLocations map
    ALIASES = {
        "kr":    "kr-mrt",
        "yih":   "yih/engin",
        "engin": "yih/engin",
        "com":   "comp",
    }

    # groups of bus stops that should be returned together
    GROUPS = {
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
    LOCATIONS = [location for group in GROUPS.values() for location in group]

    # For location prompt message
    KEYBOARD = [
        ['UTown', 'Science'],
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
                self.GET_BUS_TIMINGS: [
                    MessageHandler(Filters.regex(self.KEYBOARD_PATTERN), self.bus_timings_from_keyboard),
                    MessageHandler(Filters.location, self.bus_timings_from_location),
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
        data = query.data.replace('NUSBus.refresh', '')
        locations = json.loads(data)

        logger.info(f'/nusbus.refresh {data}')
        query.edit_message_text(
            text = self._bus_timings_api_response(locations),
            reply_markup = query.message.reply_markup,
            parse_mode = ParseMode.MARKDOWN,
        )
        query.answer() # Stop loading animation on button

    def entry(self, update: Update, context: CallbackContext):
        """Delegation to sub-handlers depending on input format"""
        # /nusbus
        if not context.args:
            return self.prompt_location(update, context)

        # /nusbus location
        elif (len(context.args) == 1):
            return self.bus_timings_from_text(update, context)

        # /nusbus location bus
        elif (len(context.args) == 2):
            return self.bus_stalking(update, context)

        # Error
        else:
            logging.warning(f'/nusbus unhandled input: {update.message.text}')
            return self.error(update, context)

    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        update.message.reply_text('🤖: Sorry I didn\'t understand that!')

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = f'🤖: Function /{self.command} cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    
    def prompt_location(self, update: Update, context: CallbackContext):
        """Send a keyboard to get user location"""
        logger.info('/nusbus')
        text = "🤖: Where are you?"
        reply_markup = ReplyKeyboardMarkup(
            [[KeyboardButton('Here', request_location=True)], *self.KEYBOARD],
            resize_keyboard = True,
            one_time_keyboard = True,
            selective = True,
        )
        update.message.reply_text(text, reply_markup=reply_markup)
        return self.GET_BUS_TIMINGS
    
    def bus_timings_from_text(self, update: Update, context: CallbackContext):
        """Parses and validates raw user input before delegating reply to a helper function"""
        input_raw = context.args[0]
        input_as_group = self.ALIASES.get(input_raw.lower(), input_raw.lower())
        input_as_location = input_raw.upper().replace('UTOWN', 'UTown')

        # Check if input is a group
        if input_as_group in self.GROUPS:
            context.user_data['locations'] = self.GROUPS[input_as_group]
            return self._bus_timings(update, context)
        
        # Check if input is a location
        elif input_as_location in self.LOCATIONS:
            context.user_data['locations'] = [input_as_location]
            return self._bus_timings(update, context)

        # Handle unrecognized input
        else:
            update.message.reply_text(f'🤖: {input_raw} is not a valid location')
            return ConversationHandler.END

    def bus_timings_from_keyboard(self, update: Update, context: CallbackContext):
        """Unpacks keyboard input into a location list before delegating reply to a helper function"""
        group = update.message.text.lower()
        context.user_data['locations'] = self.GROUPS[group]
        return self._bus_timings(update, context)

    def bus_timings_from_location(self, update: Update, context: CallbackContext):
        """Selects the nearest location before delegating reply to a helper function"""
        user_lat = update.message.location.latitude
        user_lng = update.message.location.longitude
        
        # Get the 3 nearest bus stops by distance
        nearest_stops = heapq.nsmallest(
            3, self.BUS_STOPS, 
            key = lambda bus_stop: (
                (user_lat-float(bus_stop['lat']))**2 + 
                (user_lng-float(bus_stop['lng']))**2
            ), # skip the sqrt bc slowww
        )

        context.user_data['locations'] = [bus_stop['no'] for bus_stop in nearest_stops]
        return self._bus_timings(update, context)

    def _bus_timings(self, update: Update, context: CallbackContext):
        """Extracts relevant locations from allowed input formats and sends the corresponding bus timings"""
        locations = context.user_data['locations']
        del context.user_data['locations']

        logger.info(f'/nusbus {locations}')
        update.message.reply_text(
            '🤖: Getting bus timings...', 
            reply_markup = ReplyKeyboardRemove(),
        )
        update.message.reply_text(
            text = self._bus_timings_api_response(locations),
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton('Refresh', callback_data=f'NUSBus.refresh{json.dumps(locations)}')]]),
            parse_mode = ParseMode.MARKDOWN,
        )
        return ConversationHandler.END

    def _bus_timings_api_response(self, locations):
        """Calls API and builds message body for location timings"""
        # Execute API calls sequentially 
        # Todo: Throttle requests bc the API doesn't like it when we query too fast.
        # - Using time.sleep in the main thread blocks the entire application.
        # - Making the whole bot async (to use asyncio.sleep) is probably more trouble than it's worth. 
        # - (But if the async paradigm becomes a hit in python then maybe can consider just to give people more exposure)
        # - Consider using context.job_queue to schedule a (possibly repeating) job for API calls in a seperate thread.
        # - job queue example: https://github.com/python-telegram-bot/python-telegram-bot/blob/master/examples/timerbot.py        
        results = dict()
        for bus_stop_name in locations:
            try:
                data = requests.get(
                    url = f'https://better-nextbus.appspot.com/ShuttleService', 
                    params = {'busstopname': bus_stop_name},
                    timeout = self.TIMEOUT, # Waits max 1s
                ).json()
                results[bus_stop_name] = data['ShuttleServiceResult']['shuttles']
            
            except requests.exceptions.Timeout:
                results[bus_stop_name] = None
        
        # Parse data into a nicely formatted message 
        lines = list()
        for bus_stop_name, shuttles in results.items():
            lines.append(f'*{bus_stop_name}*')

            if shuttles is not None:
                for shuttle in shuttles:
                    bus_name = shuttle['name']
                    timing_1 = shuttle["arrivalTime"]
                    timing_2 = shuttle["nextArrivalTime"]
                    indicator = '🛑' if '-' in timing_1 else '🚍' # Checks for negative timings too
                    if timing_1 == "Arr":
                        lines.append(f'{indicator}{bus_name} : {timing_1}, {timing_2} mins')
                    elif timing_1 == "1":
                        lines.append(f'{indicator}{bus_name} : {timing_1} min, {timing_2} mins')
                    else:
                        lines.append(f'{indicator}{bus_name} : {timing_1} mins, {timing_2} mins')
            
            else:
                lines.append(f'❗️Error: Cinnabot got ignored ):')
            
            lines.append('')            

        # Add timestamp to let people know the message has been refreshed
        timestamp = datetime.now().strftime('%c') # https://strftime.org/
        lines.append(f'Last updated: {timestamp}')
        
        text = '\n'.join(lines)
        return text 

    def bus_stalking(self, update: Update, context: CallbackContext):
        logger.info('/nusbus location bus')

        # Clean input
        bus_stop_name, route_code = context.args
        bus_stop_name = bus_stop_name.upper().replace('UTOWN', 'UTown') 
        route_code = route_code.upper()
        
        # Get bus timing
        try:
            shuttle_service_data = requests.get(
                url = f'https://better-nextbus.appspot.com/ShuttleService', 
                params = {'busstopname': bus_stop_name},
                timeout = self.TIMEOUT, # Waits max 1s
            ).json()

            arrival_time = None
            for shuttle in shuttle_service_data['ShuttleServiceResult']['shuttles']:
                if shuttle['name'] == route_code.upper():
                    arrival_time = shuttle['arrivalTime']
                    break
        
        except requests.exceptions.Timeout:
            update.message.reply_text(f'🤖: Cinnabot got ignored ):')
            return ConversationHandler.END
            
        # Get bus locations
        try:
            active_bus_data = requests.get(
                url = f'https://better-nextbus.appspot.com/ActiveBus', 
                params = {'route_code': route_code},
                timeout = self.TIMEOUT, # Waits max 1s
            ).json()

            active_bus = active_bus_data['ActiveBusResult']['activebus'][0]
            
        except requests.exceptions.Timeout:
            update.message.reply_text(f'🤖: Cinnabot got ignored ):')
            return ConversationHandler.END
        
        # Reply a live location
        # Todo: Actually make this live
        # - Maybe spawn a job that refreshes this message every 10s or so?
        update.message.reply_location(
            latitude = active_bus['lat'], 
            longtitude = active_bus['lng'],
            heading = active_bus['direction'],
            live_period = arrival_time,
            proximity_alert_radius = 100, 
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton(text='Come faster la', callback_data=0)]]),
        )
        update.message.reply_text('*[BETA]* Stalk the bus\'s live location!', reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

class NUSMap(Conversation):

    command = 'map'
    help_text = 'Map of NUS if you\'re lost!'
    help_full = (
        '/map: Map of NUS if you\'re lost!'
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
