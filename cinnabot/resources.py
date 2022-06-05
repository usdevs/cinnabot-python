import logging

from telegram import (
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove, 
    Update,
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
        
        '<a href="https://t.me/USPChannel">USChannel</a> \n'
        '<a href="https://t.me/cinnaspaces">CinnaSpaces Channel</a> \n'

        '\n'
        '🤖: Interest Groups: \n'

        '\n'
        'Sports ⚽🥏🏃🏽\n'

        '<a href="http://t.me/joinchat/DCoM1EmE53iMY1EynR17Cw">USPTrug</a> \n'
        '<a href="https://t.me/joinchat/MohGrU1ncc1WJCKgcNNQcw">USP Netball</a> \n'
        '<a href="https://t.me/joinchat/SqNtaymmWK81ZGQ9">USP Tchoukball</a> \n'
        '<a href="https://t.me/joinchat/U6IbNZtPikUoQOhB">USPike</a> \n'
        '<a href="https://t.me/joinchat/JJNb11U7qurTYLzbfXahFg">USP Badminton</a> \n'
        '<a href="https://t.me/joinchat/T2vwq8lCj48vKovY">USP Basketball</a> \n'
        '<a href="https://t.me/joinchat/TzBHhBgNOsTlMYCF">Floorball</a> \n'
        '<a href="https://t.me/joinchat/GYW3Z_nroERLUkyL">USClimbing</a> \n'
        '<a href="https://t.me/joinchat/ROaPIYuGO9phNzdl">Dodgeball</a> \n'
        '<a href="https://t.me/joinchat/UrToYxLM4I3PZtxU">USPlash</a> \n'
        '<a href="https://t.me/joinchat/JCHW8MeY-s4wM2U1">Tennis</a> \n'
        '<a href="https://t.me/joinchat/SUDh_IPV0v0lqNm2">Track</a> \n'
        '<a href="https://t.me/joinchat/RQH3JI1naeY3GmX8">USKick</a> \n'
        '<a href="https://t.me/+x75hyipDh5kyOWQ1">USoccer</a> \n'
        '<a href="https://t.me/joinchat/FKgI2N08iNG5VT1r">USPingpong</a> \n'
        '<a href="https://t.me/joinchat/UHzMoqFV3mPD-nwD">USSally</a> \n'
        '<a href="https://t.me/joinchat/FHPwCl0xTuY0MWY9">USContract Bridge</a> \n'
        '<a href="https://t.me/joinchat/SdaIKhTb5PWmoF91">USMinecraft</a> \n'
        '<a href="https://t.me/joinchat/dXK4mego_5NlZGRl">USTetris</a> \n'

        '\n'
        'Socio-Cultural ✍️🎶🗣️\n'
        '<a href="https://t.me/usprods">USProductions Broadcast</a> \n'
        '<a href="https://t.me/joinchat/1uEBsAY_GCAzZjc1">USFellowship</a> \n'
        '<a href="https://t.me/joinchat/UKa-ukjdAGtYLwow">USPlanet</a> \n'
        '<a href="https://bit.ly/3hKuQvH">Vibe!</a> \n'
        '<a href="http://t.me/welcome2livecore">LiveCore!</a> \n'
        '<a href="https://t.me/TheCinnamonConversation">The Cinnamon Conversation</a> \n'
        '<a href="https://t.me/uspaper">USPaper</a> \n'
        '<a href="https://t.me/cinnaroll2021">Cinnamon Roll</a> \n'
        '<a href="http://bit.ly/gctele19">Gender Collective</a> \n'
        '<a href="http://t.me/joinchat/5RhX1IhiQuRlZDg1">USProvisions</a> \n'
        '<a href="https://tinyurl.com/usdeduction">USDeduction</a> \n'
        '<a href="https://t.me/joinchat/LcQBHhG_3ewwNWRl">Smol Singlit</a> \n'
        '<a href="https://t.me/joinchat/DCqh_k7vnj8IVcry7bvy_Q">USR</a> \n'
        '<a href="http://tinyurl.com/usptabletop">USP Tabletop</a> \n'
        
        '\n'
        '🤖: Care Mental Health : \n'
        'As you study, do take care of your mental health! \n'
        'Use Mental Health: @asafespacebot (credits to Love, USP) \n'
        '\n'
        )
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove(), parse_mode = ParseMode.HTML)
        return ConversationHandler.END

    def cancel(self, update: Update, context: CallbackContext):
        """Ends the user flow by removing the keyboard."""
        logger.info('cancel')
        text = '🤖: Function /resources cancelled!'
        update.message.reply_text(text, reply_markup=ReplyKeyboardRemove())
        return ConversationHandler.END
    