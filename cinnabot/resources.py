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
    help_text = 'NUSC resources!'
    help_full = (
        "/resources <tag>: searches resources for a specific tag\n"
        "/resources: returns all tags"
    )

    # States
    GET_RESOURCES = 0

    # Class helper variables
    KEYBOARD = [
        ['Channels', 'Interest Groups'],
        ['Care Mental Health']
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
        text = (
        '🤖: Channels: \n' 
        
        'USChannel: t.me/USPChannel \n'
        'CinnaSpaces Channel: t.me/cinnaspaces \n'
        '\n'
        '🤖: Interest Groups: \n'
        
        'USProductions Broadcast: t.me/usprods \n'
        'USPTrug: http://t.me/joinchat/DCoM1EmE53iMY1EynR17Cw \n'
        'USFellowship: https://t.me/joinchat/1uEBsAY_GCAzZjc1 \n'
        'USPlanet: https://t.me/joinchat/UKa-ukjdAGtYLwow \n'
        'USP Netball: https://t.me/joinchat/MohGrU1ncc1WJCKgcNNQcw \n'
        'USP Tchoukball: https://t.me/joinchat/SqNtaymmWK81ZGQ9 \n'
        'Vibe!: https://bit.ly/3hKuQvH \n'
        'LiveCore!: http://t.me/welcome2livecore \n'
        'USPike: https://t.me/joinchat/U6IbNZtPikUoQOhB \n'
        'The Cinnamon Conversation: https://t.me/TheCinnamonConversation \n'
        'USPaper: https://t.me/uspaper \n'
        'USP Badminton: https://t.me/joinchat/JJNb11U7qurTYLzbfXahFg \n'
        'USP Basketball: https://t.me/joinchat/T2vwq8lCj48vKovY \n'
        'Cinnamon Roll: https://t.me/cinnaroll2021 \n'
        'Floorball: https://t.me/joinchat/TzBHhBgNOsTlMYCF \n'
        'USClimbing: https://t.me/joinchat/GYW3Z_nroERLUkyL \n'
        'USContract Bridge: https://t.me/joinchat/FHPwCl0xTuY0MWY9 \n'
        'Gender Collective: http://bit.ly/gctele19 \n'
        'USProvisions: http://t.me/joinchat/5RhX1IhiQuRlZDg1 \n'
        'USDeduction: https://tinyurl.com/usdeduction \n'
        'Smol Singlit: https://t.me/joinchat/LcQBHhG_3ewwNWRl \n'
        'Dodgeball: https://t.me/joinchat/ROaPIYuGO9phNzdl \n'
        'USPlash: https://t.me/joinchat/UrToYxLM4I3PZtxU \n'
        'Tennis: https://t.me/joinchat/JCHW8MeY-s4wM2U1 \n'
        'Track: https://t.me/joinchat/SUDh_IPV0v0lqNm2 \n'
        'USKick: https://t.me/joinchat/RQH3JI1naeY3GmX8 \n'
        'USR: https://t.me/joinchat/DCqh_k7vnj8IVcry7bvy_Q \n'
        'USP Tabletop: http://tinyurl.com/usptabletop \n'
        'USMinecraft: https://t.me/joinchat/SdaIKhTb5PWmoF91 \n'
        'USPingpong: https://t.me/joinchat/FKgI2N08iNG5VT1r \n'
        'UStetris: https://t.me/joinchat/dXK4mego_5NlZGRl \n'
        'USSally:https://t.me/joinchat/UHzMoqFV3mPD-nwD \n'
        'USoccer: https://t.me/+x75hyipDh5kyOWQ1'
        '\n'
        '🤖: Care Mental Health : \n'
        'As you study, do take care of your mental health! \n'
        'Use Mental Health: @asafespacebot (credits to Love, USP) \n'
        '\n'
        )
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = '🤖: Function /resources cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    