import logging

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

class Feedback(Conversation):

    command = 'feedback'
    help_text = 'to give feedback'
    help_full = (
        '/feedback: to give feedback'
    )

    # States
    GET_FEEDBACK_MESSAGE, TO_USC, TO_DINING, TO_RESIDENTIAL, TO_USDEVS = range(5)

    # Class helper variables
    KEYBOARD = [
        ["USC"],
        ["Dining"],
        ["Residential"],
        ["Cinnabot"],
        ["OHS"],
    ]

    RECIPIENT_IDS = {
        "usc": 715358126,
        "dining": 715358126,
        "residential": 715358126,
        "cinnabot": 715358126,
    }

    TAGS = [button for row in KEYBOARD for button in row]

    KEYBOARD_PATTERN = '^(' + '|'.join(TAGS) + ')$' # Regex to match all valid replies

    @property
    def handler(self):
        return ConversationHandler(
            entry_points = [CommandHandler(self.command, self.entry)],
            states = {
                self.GET_FEEDBACK_MESSAGE: [MessageHandler(Filters.regex(self.KEYBOARD_PATTERN), self.get_feedback_message)],
                self.TO_USC: [MessageHandler(Filters.text, self.to_usc)],
                self.TO_DINING: [MessageHandler(Filters.text, self.to_dining)],
                self.TO_RESIDENTIAL: [MessageHandler(Filters.text, self.to_residential)],
                self.TO_USDEVS: [MessageHandler(Filters.text, self.to_usdevs)],
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def entry(self, update: Update, context: CallbackContext):
        text = '\n'.join([
            "🤖: What will you like to give feedback to?",
            "Use /cancel if you chicken out.",
        ])

        reply_markup = ReplyKeyboardMarkup(
            self.KEYBOARD,
            resize_keyboard = True,
            one_time_keyboard = True,
            selective = True,
        )

        update.message.reply_text(text, reply_markup=reply_markup)
        return self.GET_FEEDBACK_MESSAGE
    
    def error(self, update: Update, context: CallbackContext):
        """Alerts the user of a bad reply and continues trying to parse user replies."""
        logger.info('error')
        text = f'🤖: "{update.message.text}" not recognized'
        update.message.reply_text(text)
        return self.GET_FEEDBACK_MESSAGE

    def get_feedback_message(self, update: Update, context: CallbackContext):
        """Prompts the user for the feedback message and removes the keyboard."""
        logger.info('get_feedback_message')

        target = update.message.text.lower()
        recipients = {
            "usc": "the University Scholars Club",
            "dining": "the Dining Hall Committee",
            "residential": "the Residential Assistants",
            "cinnabot": "USDevs, the developers of CinnaBot",
        }

        text = ''

        if target == "ohs":
            text = "[OHS Feedback](https://bit.ly/faultycinnamon)"
        else:
            text = f"This feedback will be sent to {recipients[target]}. Please send your message."
        
        if target == "dining":
            text += "\n(Indicate which stall you ate and whether it was Breakfast or Dinner)"

        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        
        if target == "usc":
            return self.TO_USC
        elif target == "dining":
            return self.TO_DINING
        elif target == "residential":
            return self.TO_RESIDENTIAL
        elif target == "cinnabot":
            return self.TO_USDEVS

        return ConversationHandler.END

    def to_usc(self, update: Update, context: CallbackContext):
        """Ends the user flow by forwarding the feedback to USC."""
        logger.info('to_usc')

        update.message.forward(self.RECIPIENT_IDS['usc'])

        text = '\n'.join([
            '🤖: Feedback received! I will now transmit feedback to USC',
            '',
            'We really appreciate you taking the time out to submit feedback.'
        ])

        update.message.reply_text(text)

        return ConversationHandler.END

    def to_dining(self, update: Update, context: CallbackContext):
        """Ends the user flow by forwarding the feedback to USC."""
        logger.info('to_dining')

        update.message.forward(self.RECIPIENT_IDS['dining'])

        text = '\n'.join([
            '🤖: Feedback received! I will now transmit feedback to the dining hall committee.',
            '',
            'We really appreciate you taking the time out to submit feedback.'
        ])

        update.message.reply_text(text)

        return ConversationHandler.END
    
    def to_residential(self, update: Update, context: CallbackContext):
        """Ends the user flow by forwarding the feedback to USC."""
        logger.info('to_residential')

        update.message.forward(self.RECIPIENT_IDS['residential'])

        text = '\n'.join([
            '🤖: Feedback received! I will now transmit feedback to the residential committee.',
            '',
            'We really appreciate you taking the time out to submit feedback.'
        ])

        update.message.reply_text(text)

        return ConversationHandler.END

    def to_usdevs(self, update: Update, context: CallbackContext):
        """Ends the user flow by forwarding the feedback to USC."""
        logger.info('to_usdevs')

        update.message.forward(self.RECIPIENT_IDS['usdevs'])

        text = '\n'.join([
            '🤖: Feedback received! I will now transmit feedback to USDevs.',
            '',
            'We really appreciate you taking the time out to submit feedback.'
        ])

        update.message.reply_text(text)

        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = f'🤖: Function /{self.command} cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END