import logging
import random

from telegram import (
    Update,
    Message,
    ReplyKeyboardMarkup,
    ParseMode,
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

STATES = range(2)
(
    SHOP,
    END
) = STATES

class Reply:
    """Data class that handles telegram reply type according to arguments.
    This exists in part only to make maintaining the chatbot structure easier"""

    # Chatbot data is associated with this class rn but maybe that's not the best? 
    # Move it to the Claims(Conversation) when integrating to cinnabot.

    def __init__(self, text: str, keyboard=None):
        self.text = text
        self.keyboard = keyboard

    def reply_to(self, message: Message):
        if self.keyboard is not None:
            message.reply_markdown(
                text = self.text,
                reply_markup = ReplyKeyboardMarkup(
                    keyboard = [[button] for button in Supper.DATA[self.keyboard]] + [['Back']],
                    one_time_keyboard = True,
                    resize_keyboard = True,
                    selective = True,
                )
            )

class Supper(Conversation):

    command = 'supper'
    help_text = 'Order your supper here!'
    help_full = (
        'List of popular supper food'
    )

    DATA = dict()
    choices = ['SuperSnacks UTown', 'Al Amaan Restaurant', 'McDonalds']
    MENU = ''
    RANDOM_CHOICE = random.choice(choices)
    if (RANDOM_CHOICE == 'SuperSnacks UTown'):
        MENU = 'Super Snacks UTown: \n https://www.yqueue.co/sg/menu/supersnacks-nus-u-town \n'
    elif (RANDOM_CHOICE == 'Al Amaan Restaurant'):
        MENU = 'Al Amaan Restaurant: \n https://alamaanrestaurant.com/order/ \n'
    elif (RANDOM_CHOICE == 'McDonalds'):
        MENU = 'McDonalds: \n https://www.mcdelivery.com.sg/sg/ \n'

    @property
    def handler(self):
        """Conversation handler to pass to dispatcher"""
        return ConversationHandler(
            entry_points = [
                CommandHandler(self.command, self.entry),
            ],
            states = {
                state: self.make_handlers(mapping)
                for state, mapping in self.DATA.items()
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def entry(self, update: Update, context: CallbackContext):
        """Starts conversation after /supper"""
        logger.info('entry')
        context.chat_data['history'] = list()
        context.chat_data['history'].append(self.entry)
        name = update.message.from_user.first_name
        text = f'🤖: Hey {name}, what would you like to order? (/cancel to exit)'
        update.message.reply_text(
            text, 
            reply_markup=ReplyKeyboardMarkup(
                keyboard = [[button] for button in self.DATA[SHOP]],
                one_time_keyboard = True,
                resize_keyboard = True,
                selective = True,               
            )
        )
        return SHOP

    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        text = f'🤖: "{update.message.text}" not recognized'
        update.message.reply_text(text) 

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = '🤖: Function /supper cancelled!'
        update.message.reply_text(text)
        return ConversationHandler.END 
    
    def back(self, update: Update, context: CallbackContext):
        """Delegates callback to the last recorded callback"""
        last_callback = context.chat_data['history'].pop() # Undo wrong callback
        last_callback = context.chat_data['history'][-1] # Replay last callback
        next_state = last_callback(update, context) # Skip content messages
        return next_state

    def make_callback(self, user_input, replies):
        """Constructs a callback"""
        def callback(update: Update, context: CallbackContext, replay=False):
            logger.info(f'{update.message.from_user.id}: "{user_input}"')

            # Skip content messages on back command by setting `replay=True` 
            if replay:
                selected_replies = replies[-1:]
            else:
                context.chat_data['history'].append(callback)
                selected_replies = replies

            # Send out replies and update the application state
            next_state = ConversationHandler.END
            for reply in selected_replies:
                reply.reply_to(update.message)
                if reply.keyboard is not None:
                    next_state = reply.keyboard

            return next_state
        return callback   

    def make_handlers(self, mapping):
        """Builds a list of handlers from chatbot data"""
        handlers = [MessageHandler(Filters.regex('Back'), self.back)]
        for user_input, replies in mapping.items():
            pattern = '^' + user_input.replace('(', r'\(').replace(')', r'\)') + '$'
            handlers.append(MessageHandler(
                Filters.regex(pattern), 
                self.make_callback(user_input, replies),
            ))
        return handlers

Supper.DATA[SHOP] = {
    'I will decide by myself!': [
        Reply(
            '🤖: Here are your Menu and Order Forms! \n'
            '\n'
            'Super Snacks UTown: \n https://www.yqueue.co/sg/menu/supersnacks-nus-u-town \n'
            '\n'
            'Al Amaan Restaurant: \n https://alamaanrestaurant.com/order/ \n'
            '\n'
            'McDonalds: \n https://www.mcdelivery.com.sg/sg/ \n'
            '\n'
            'Your Delivery Address is: \n - 18 College Ave East,  Singapore 138593 (Cinnamon) \n - 16 College Ave West, Singapore 138527 (West) \n',
            keyboard = END
        )
    ], 
    'Decide for me im lazy!': [
        Reply(
            f'🤖: I have decided that your supper will be from ' + Supper.RANDOM_CHOICE + '!' + '\n' + Supper.MENU + '\n'
            'Your Delivery Address is: \n - 18 College Ave East,  Singapore 138593 (Cinnamon) \n - 16 College Ave West, Singapore 138527 (West) \n',
            keyboard = END
        )
    ]
}

Supper.DATA[END] = {
    'The End!': [
        Reply(
            '🤖: Enjoy your supper! (Use /supper to revisit)',
        ), 
    ],
}