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
    help_text = 'Give your feedback!'
    help_full = (
        '/feedback: Give your feedback!'
    )

    # States
    GET_FEEDBACK_MESSAGE = range(1)

    # Class helper variables
    KEYBOARD = [
        ["Office of Housing Services"],
        ["University Scholars Club"]
    ]

    TAGS = [button for row in KEYBOARD for button in row]

    KEYBOARD_PATTERN = '^(' + '|'.join(TAGS) + ')$' # Regex to match all valid replies

    @property
    def handler(self):
        return ConversationHandler(
            entry_points = [CommandHandler(self.command, self.entry)],
            states = {
                self.GET_FEEDBACK_MESSAGE: [MessageHandler(Filters.regex(self.KEYBOARD_PATTERN), self.get_feedback_message)],
            },
            fallbacks = [
                CommandHandler('cancel', self.cancel),
                MessageHandler(Filters.text, self.error),
            ],
        )

    def entry(self, update: Update, context: CallbackContext):
        text = '\n'.join([
            "🤖: What will you like to give feedback for?",
            "Use /cancel to exit.",
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
        """Prompts the user for the feedback message and removes the keyboard. If OHS is selected, ends the user flow."""
        logger.info('get_feedback_message')
        target = update.message.text.lower()
        text = ''

        if target == "office of housing services":
            text = "[Office of Housing Services Feedback]: https://bit.ly/faultycinnamon"
        
        if target == "university scholars club":
            text += "[USC Site Feedback]: https://nususc.com/feedback"

        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = f'🤖: Function /{self.command} cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END