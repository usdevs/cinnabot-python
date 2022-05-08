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

class NUSMap(Conversation):

    command = 'map'
    help_text = 'Find your way around NUS!'
    help_full = (
        '/map: Find your way around NUS!'
    )

    # States
    GET_MAP = 0

    # Class helper variables
    KEYBOARD = [
        ['CHS', 'Computing'],
        ['Law', 'Business'],
        ['UTown', 'CDE'],
    ]

    NUSMODS_URLS = {
        "chs": "https://nusmods.com/venues/AS4-0602",
        "computing": "https://nusmods.com/venues/COM1-0120",
        "law": "https://nusmods.com/venues" + "\n\n PS: Law venues are available under 'L'!",
        "business": "https://nusmods.com/venues/BIZ2-0115",
        "utown": "https://nusmods.com/venues/UT-AUD2",
        "cde": "https://nusmods.com/venues/SDE-ER4",
    }

    IMAGE_URLS = {
        "chs": Path("cinnabot", "maps", "CHS Map.png"),
        "computing": Path("cinnabot", "maps", "Computing Map.png"),
        "law": Path("cinnabot", "maps", "Law Map.png"),
        "business": Path("cinnabot", "maps", "Biz Map.png"),
        "utown": Path("cinnabot", "maps", "UTown Map.png"),
        "cde": Path("cinnabot", "maps", "CDE Map.png"),
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
                f'🤖: Hey {name}, here is a map of your location. Hope you may find your way around!',
                '',
                'For more information, please visit',
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
