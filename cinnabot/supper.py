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


class Supper(Conversation):

    command = 'supper'
    help_text = 'Order your supper here!'
    help_full = (
        'List of popular supper food'
    )

    # States
    GET_SHOPS = 0

    # Class helper variables
    KEYBOARD = [
        ['SuperSnacks UTown'],
        ['Al Amaan Restaurant'],
        ['Mc Donalds']
    ]

    TAGS = [button for row in KEYBOARD for button in row]

    KEYBOARD_PATTERN = '^(' + '|'.join(TAGS) + ')$' # Regex to match all valid replies


    @property
    def handler(self):
        """Conversation handler to pass to dispatcher"""
        return ConversationHandler(
            entry_points = [CommandHandler(self.command, self.entry)],
            states = {
                self.GET_SHOPS: [
                    MessageHandler(Filters.regex(self.KEYBOARD_PATTERN), self.get_shops)
                ],
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def entry(self, update: Update, context: CallbackContext):
        """Starts conversation after /supper"""
        logger.info('entry')
        name = update.message.from_user.first_name
        text = f'🤖: Hey {name}, what would you like to order? (/cancel to exit)'
        update.message.reply_text(text, reply_markup=ReplyKeyboardMarkup(self.KEYBOARD))
        return self.GET_SHOPS

    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        text = f'🤖: "{update.message.text}" not recognized'
        update.message.reply_text(text)
        return self.GET_SHOPS

    def get_shops(self, update: Update, context: CallbackContext):
        """Ends the user flow by sending a message with the desired shops and removing the keyboard."""
        logger.info('get_shops')
        text = (
            f'🤖: Here are your Menu and Order Forms! \n'
            '\n'
            'Super Snacks UTown: \n https://www.yqueue.co/sg/menu/supersnacks-nus-u-town \n'
            '\n'
            'Al Amaan Restaurant: \n https://alamaanrestaurant.com/order/ \n'
            '\n'
            'Mc Donalds: \n https://www.mcdelivery.com.sg/sg/ \n'
            '\n'
            'Your Delivery Address is: \n - 18 College Ave East,  Singapore 138593 (Cinnamon) \n - 16 College Ave West, Singapore 138527 (West) \n'
        )
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = '🤖: Function /supper cancelled!'
        update.message.reply_text(text)
        return ConversationHandler.END