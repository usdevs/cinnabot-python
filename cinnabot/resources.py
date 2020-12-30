import logging

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove, 
    Update,
)
from telegram.ext import (
    ConversationHandler,
    CommandHandler,
    MessageHandler,
    Filters,
    CallbackContext,
)

from cinnabot import Conversation

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


class Resources(Conversation):

    command = 'resources'
    help_text = 'list of important resources!'
    help_full = (
        "/resources <tag>: searches resources for a specific tag\n"
        "/resources: returns all tags"
    )

    # States
    GET_RESOURCES = 0

    # Class helper variables
    KEYBOARD = [
        ['Telegram', 'Links'],
        ['Interest Groups', 'Everything'],
    ]

    TAGS = [button for row in KEYBOARD for button in row]

    KEYBOARD_PATTERN = '^(' + '|'.join(TAGS) + ')$' # Regex to match all valid replies

    @property
    def handler(self):
        """Conversation handler to pass to dispatcher"""
        return ConversationHandler(
            entry_points = [CommandHandler(self.command, self.entry)],
            states = {
                self.GET_RESOURCES: [
                    MessageHandler(Filters.regex(self.KEYBOARD_PATTERN), self.get_resources)
                ],
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def entry(self, update: Update, context: CallbackContext):
        """Starts a user flow for /resources"""
        logger.info('entry')
        text = '🤖: How can I help you? (/cancel to exit)'
        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(self.KEYBOARD))
        return self.GET_RESOURCES

    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        text = f'🤖: "{update.message.text}" not recognized'
        update.message.reply_text(text)
        return self.GET_RESOURCES

    def get_resources(self, update: Update, context: CallbackContext):
        """Ends the user flow by sending a message with the desired resources and removing the keyboard."""
        logger.info('get_resources')
        text = '🤖: Link this to firebase! The current json solution is not the best ):'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = '🤖: Function /resources cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    