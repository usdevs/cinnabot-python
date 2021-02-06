"""Data for the bot is all stored here!

DATA:        maps application states to their associated content
Claims.DATA[STATE]: maps user input to a list of replies for a particular state
"""

# Base imports
import logging
from pathlib import Path

# 3rd party imports
from telegram import (
    Update,
    Message,
    ReplyKeyboardMarkup, 
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Updater,
    CallbackContext,
    ConversationHandler,
    CommandHandler, 
    MessageHandler, 
    Filters,
)

# Local imports
from cinnabot import Conversation

# Logging config
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
)
logger = logging.getLogger(__name__)

# Application states
STATES = range(7)
(
    START,
    PURCHASE_TYPE, 
    PURCHASE_CATEGORY,
    SPECIAL_REQUEST,
    QUERIES,
    STUDENT_GROUP,
    END,
) = STATES


class Reply:
    """Data class that handles telegram reply type according to arguments.
    This exists in part only to make maintaining the chatbot structure easier"""

    # Chatbot data is associated with this class rn but maybe that's not the best? 
    # Move it to the Claims(Conversation) when integrating to cinnabot.

    def __init__(self, text: str, photo=None, audio=None, document=None, keyboard=None):
        self.text = text
        self.photo = photo
        self.audio = audio
        self.document = document
        self.keyboard = keyboard

    def _reply_with_attachment(self, message: Message, attachment_type: str):
        """Attempts to send a attachment and sends an error message if unsuccessful"""
        try:
            filepath = getattr(self, attachment_type)
            function = getattr(message, f'reply_{attachment_type}')
            with open(filepath, 'rb') as attachment:
                function(**{
                    attachment_type: attachment,
                    'caption': self.text,
                })
        except Exception as e:
            logger.error(e)
            message.reply_text(f'{self.text}:\n{attachment_type.title()} not found!')

    def reply_to(self, message: Message):
        if self.photo is None and self.audio is None and self.document is None and self.keyboard is None:
            message.reply_markdown(
                text = self.text,
                reply_markup = ReplyKeyboardRemove()
            )

        elif self.photo is not None:
            self._reply_with_attachment(message, 'photo')

        elif self.audio is not None:
            self._reply_with_attachment(message, 'audio')
        
        elif self.document is not None:
            self._reply_with_attachment(message, 'document')
        
        elif self.keyboard is not None:
            message.reply_markdown(
                text = self.text,
                reply_markup = ReplyKeyboardMarkup(
                    keyboard = [[button] for button in Claims.DATA[self.keyboard]] + [['Back']],
                    one_time_keyboard = True,
                    resize_keyboard = True,
                    selective = True,
                )
            )


class Claims(Conversation):

    command = 'claimsbot'
    help_text = 'Filling up claims do be hard sometimes...'
    help_full = 'Filling up claims do be hard sometimes...'

    DATA = dict()

    @property
    def handler(self):
        return ConversationHandler(
            entry_points = [
                CommandHandler(self.command, self.entry),
            ],
            states = {
                state: self._make_handlers(mapping)
                for state, mapping in self.DATA.items()
            },
            fallbacks = [
                CommandHandler('claims', self.entry),
                MessageHandler(Filters.text, self.error),
            ],
            per_chat = True,
            per_user = False,
            per_message = False,
        )
    
    def entry(self, update: Update, context: CallbackContext, **kwargs):
        """kwargs included for compatibility with replay=True hack"""
        logger.info(f'{update.message.from_user.id}: "entry"')
        context.chat_data['history'] = list()
        context.chat_data['history'].append(self.entry)
        update.message.reply_text(
            text = (
                'Welcome to Claimsbot, your one-stop guide to finance claiming!\n'
                '\n'
                'You can file a finance claim by following these 5 simple steps!\n'
                '\n'
                '1. Make a fund request and get approval from your respective Attache\n'
                '2. Make your purchase\n'
                '3. Fill up your RFP Form and provide relevant supporting documents\n' 
                '4. Submit your RFP Form to your relevant Attache\n'
                '5. Check your bank account for the reimbursement! (usually takes about one month)\n'
                '\n'
                'What would you like to do?'
            ),
            reply_markup = ReplyKeyboardMarkup(
                keyboard = [[button] for button in self.DATA[START]],
                one_time_keyboard = True,
                resize_keyboard = True,
                selective = True,
            )
        )
        return START

    def back(self, update: Update, context: CallbackContext):
        """Delegates callback to the last recorded callback"""
        last_callback = context.chat_data['history'].pop() # Undo wrong callback
        last_callback = context.chat_data['history'][-1] # Replay last callback
        next_state = last_callback(update, context, replay=True) # Skip content messages
        return next_state

    def error(self, update: Update, context: CallbackContext):
        logger.error(f'{update.message.from_user.id}: "{update.message.text}"')
        update.message.reply_text(
            text = 'Sorry! I didn\'t understand you.'
        )

    def _make_callback(self, user_input, replies):
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

    def _make_handlers(self, mapping):
        """Builds a list of handlers from chatbot data"""
        handlers = [MessageHandler(Filters.regex('Back'), self.back)]
        for user_input, replies in mapping.items():
            pattern = '^' + user_input.replace('(', r'\(').replace(')', r'\)') + '$'
            handlers.append(MessageHandler(
                Filters.regex(pattern), 
                self._make_callback(user_input, replies),
            ))
        return handlers


Claims.DATA[START] = {
    'Make a Fund Request': [
        Reply(
            'Please head over to tinyurl.com/uspfundreq to make your fund request, '
            'and do inform your respective Attaches via telegram once you’ve '
            'submitted your request form!\n'
            '\n'
            'Also, which student group are you representing?',
            keyboard = STUDENT_GROUP
        )
    ], 
    'Filing a student claim': [
        Reply(
            'RFP Form Sample',
            photo = Path('cinnabot', 'claims', 'image0.jpg')
        ),
        Reply(
            'This bot will provide you with a step-by-step guide to filing your student claim'
            ' - simply select the relevant options and follow the instructions + sample documents provided!'
            ' All documents required can be found at tinyurl.com/uspfinance .\n'
            '\n'
            'To start off, all claims require you to fill up the Request for Payment Form (RFP) as below!'
            ' But depending on the specific details of your claim,'
            ' you\'ll need to attach additional documents behind your RFP!\n'
            '\n'
            'First up, what kind of purchase are you making?',
            keyboard = PURCHASE_TYPE
        ),
    ],
}

Claims.DATA[PURCHASE_TYPE] = {
    'Physical Purchase': [
        Reply(
            'Did you make your purchase physically at a store?\n'
            '\n'
            'If you did, simply keep the physical receipt and tape it to a piece of A4 paper.'
            ' Then, staple the A4 paper behind your RFP!\n'
            '\n'
            'Some pro-tips:\n'
            '\n'
            '1. Avoid handwritten/contactless sale receipts!\n'
            '\n'
            '2. Be sure to tape your receipt as stapling isn\'t allowed by the Office of Finance.\n'
            '\n'
            '3. Physical receipts may fade quickly - be sure to submit asap!'

        ),
        Reply(
            'Physical Receipt Sample',
            photo = Path('cinnabot', 'claims', 'image1.jpg')
        ),
    ],
    'Online (Credit card)': [
        Reply(
            'Did you make your purchase online using a Credit Card?\n'
            '\n'
            'If you did, please attach the following screenshots behind your RFP:\n'
            '\n'
            '1. *Product Description* (Price + description)\n'
            '2. *Order Confirmation*\n'
            '3. *Bank statement indicating deducted value*'
        ),
        Reply(
            'Product Description Sample',
            photo = Path('cinnabot', 'claims', 'image2.jpg')
        ),
        Reply(
            'Order Confirmation Sample',
            photo = Path('cinnabot', 'claims', 'image3.jpg')
        ),
        Reply(
            'Bank Statement Screenshot Sample',
            photo = Path('cinnabot', 'claims', 'image4.jpg')
        ),
    ],
    'Online (Mobile payment)': [
        Reply(
            'Did you make your purchase online using mobile payments such as Grabpay, PayLah!, PayNow etc.?\n'
            '\n'
            'If you did, please attach the following screenshots behind your RFP:\n'
            '\n'
            '1. *Product Description* (Price + description)\n'
            '2. *Order Confirmation*\n'
            '3. *Payment Page*'
        ),
        Reply(
            'Product Description Sample',
            photo = Path('cinnabot', 'claims', 'image5.jpg')
        ),
        Reply(
            'Order Confirmation Sample',
            photo = Path('cinnabot', 'claims', 'image6.jpg')
        ),
        Reply(
            'Payment Page Screenshot Sample',
            photo = Path('cinnabot', 'claims', 'image7.jpg')
        ),
    ],  
    'Invoice': [
        Reply(
            'Did you make a purchase through an invoice billed to NUS?\n'
            '\n'
            'If you did, please attach the invoice behind your RFP for submission!\n'
            '\n'
            'Pro-tips: \n'
            '\n'
            '1. Do inform the vendor of the NUS billing address, to be reflected within the invoice:'
            ' National university of Singapore, University Scholars Programme, '
            'Cinnamon College Administrative Office, University Town 2, '
            '18 College Avenue East, Singapore 138593\n'
            '\n'
            '2. Invoices contain legal due dates on when they must be paid by, etc. within 30 days. Be sure to submit them asap!\n'
            '\n'
            '3. Within the RFP form, provide the name, email and contact number of the vendor instead of yours! Matric no. may be left blank.'
        ),
        Reply(
            'Invoice Sample (Please make sure there’s a product description in the invoice)',
            photo = Path('cinnabot', 'claims', 'image8.jpg')
        ),
    ],
}

Claims.DATA[PURCHASE_TYPE] = {
    user_input: [
        *replies,
        Reply(
            'Next, does your purchase fall under any of the following categories?',
            keyboard = PURCHASE_CATEGORY
        ),
    ]
    for user_input, replies in Claims.DATA[PURCHASE_TYPE].items()
}

Claims.DATA[PURCHASE_CATEGORY] = {
    'Food': [
        Reply(
            'If you are filing a claim for food items ordered at an event,'
            ' Please attach a name-list with the full names of all event attendees behind your RFP.\n'
            '\n'
            'Do note that food purchases are capped at $5 per person! Etc. you cannot claim for $40 worth of food if 5 people came for the event. '
        ),
        Reply(
            'Name-list Sample',
            photo = Path('cinnabot', 'claims', 'image9.jpg'),
        ),
    ], 
    'Transport': [
        Reply(
            'If you are claiming for the use of transport,'
            ' please fill in and attach the Transport Claim Form behind your RFP.\n'
            '\n'
            'Within the form, you\'ll need to include a valid justification for the use of transport under the \"purpose of trips"!\n'
            '\n'
            'Valid Justifications include:\n'
            '1. Transporting of heavy equipment or large amounts of equipment\n'
            '2. Transportation of a large group of people etc.\n'
            '\n'
            'Invalid Justifications include:\n'
            '1. Convenience\n'
            '2. To avoid being late etc.'
        ),
        Reply(
            'Transport Claim Form Sample',
            photo = Path('cinnabot', 'claims', 'image10.jpg')
        )
    ], 
    'Prizes/Vouchers': [
        Reply(
            'If you\'re filing a claim for prizes and/or vouchers awarded for an event, '
            'please attach these supporting documents to your RFP:\n'
            '\n'
            '1. *Prize Claim Form* (requires signature of prize recipients + witness who distributed the prizes + claimee)\n'
            '2. *Proof of Event* (publicity material declaring the event + prizes)'
        ),
        Reply(
            'Prize Claim Form Sample',
            photo = Path('cinnabot', 'claims', 'image11.jpg')
        ),
        Reply(
            'Publicity Material Sample',
            photo = Path('cinnabot', 'claims', 'image12.jpg')
        ),
    ], 
    'NIL': [],
}

Claims.DATA[PURCHASE_CATEGORY] = {
    user_input: [
        *replies,
        Reply(
            'Lastly, does your claim fall under any of these special circumstances?',
            keyboard = SPECIAL_REQUEST
        ),
    ]
    for user_input, replies in Claims.DATA[PURCHASE_CATEGORY].items()
}

Claims.DATA[SPECIAL_REQUEST] = {
    'Claiming on behalf of someone else': [
        Reply(
            'Are you filing a claim on behalf of somebody else, and their name is reflected on the receipts/supporting documents instead of yours?\n '
            '\n'
            'If so, please request the person who bought the items to'
            ' write the following declaration beside the relevant documents:\n' 
            '\n'
            'I, (Name of Payee, Matric Number), declare that I paid for the item, '
            'and (Name of Claimant, Matric Number), has reimbursed me the amount that I have paid. '
            'Please reimburse (Name of Claimant) instead. (Payee’s Signature)'
        ),
    ],
    'Claiming only part of the receipt': [
        Reply(
            'Are you filing a claim for only certain items listed in your receipt?\n'
            '\n'
            'If so, simply include the following declaration beside your receipt:\n'
            '\n'
            'This is a partial claim. I, (Name, Matric Number), will only be '
            'claiming $$(Amount to be Claimed) from this receipt. (Signature).'
        ),
    ], 
    'Receipt is a photocopy/printout': [
        Reply(
            'Are you filing a claim using a photocopy/printout of the original receipt?\n'
            '\n'
            'If so, please include the following declaration on the receipt:\n'
            '\n'
            'I, (Name, Matric Number), declare that this receipt has not not been claimed before. '
            'The original receipt has not been attached because (Justification).\n'
            '\n'
            'Valid Justifications include:\n'
            '1. Receipt not provided by vendor despite asking\n'
            '2. Receipt faded with time\n'
            '3. Only electronic receipt/invoice provided by the vendor despite asking etc.\n'
            '\n'
            'Invalid Justifications include\n' 
            '1. Loss of receipt\n'
            '2. Torn or damaged (by self) receipt etc.\n'
        ),
    ],
    'Payment currency not in SGD': [
        Reply(
            'Are you filing a claim for which the payment currency is not in SGD?\n'
            'ie. the value reflected in the bank statement in SGD differs from the value reflected in your product description screenshot (in foreign currency.)\n'
            '\n'
            'If so, please include the following documents:\n'
            '1. *Screenshot of the exchange rate on the day of purchase*\n'
            '2. *Screenshot of foreign retail transaction fees by bank*\n'
            '3. *Screenshot of a calculation showing: original price in foreign currency x exchange rate x foreign retail transaction fee = SGD amount deducted from bank statement*\n'
            '\\*The calculated amount need not tally exactly, but should closely align with the amount in the bank statement!'
        ),
        Reply(
            'Screenshot of exchange rate Sample',
            photo = Path('cinnabot', 'claims', 'image14.jpg')
        ),
        Reply(
            'Foreign retail transaction fee Sample',
            photo = Path('cinnabot', 'claims', 'image15.jpg')
        ),
        Reply(
            'Calculation Sample',
            photo = Path('cinnabot', 'claims', 'image16.jpg')
        ),
    ], 
    'NIL': [],
}

Claims.DATA[SPECIAL_REQUEST] = {
    user_input: [
        *replies,
        Reply(
            'That\'s the end of our student claim walkthrough! Once you have filled in the RFP form and the relevant supporting documents, '
            'you are ready to submit your claim to your respective Attaches!\n'
            '\n'
            'Finally, do you still have any questions regarding your submission?',
            keyboard = QUERIES
        ),
    ]
    for user_input, replies in Claims.DATA[SPECIAL_REQUEST].items()
}

Claims.DATA[QUERIES] = {
    'Yes!': [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            'Which student group are you representing?',
            keyboard = STUDENT_GROUP
        ),
    ], 
    'Nope :D': [
        Reply(
            'Thank you for using Claimsbot!',
            keyboard = END,
        ),
    ],
}

Claims.DATA[STUDENT_GROUP] = {
    "Ursaia/Nocturna/Ianthe": [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            '*Attache(s) for Ursaia/Nocturna/Ianthe*\n'
            "Yi Jin @limyijin",
            keyboard = END,
        )
    ],
    "Triton/Ankaa/Saren": [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            '*Attache(s) for Triton/Ankaa/Saren*\n'
            "Alson @alsontay",
            keyboard = END,
        )
    ],
    "Comm Life (IG/GUI)": [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            '*Attache(s) for Comm Life (IG/GUI)*\n'
            "Wei Ching @chingariro\n"
            "Harz @mdharz",
            keyboard = END,
        )
    ],
    "FOP": [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            '*Attache(s) for FOP*\n'
            "Natalie @natalieeeeee ",
            keyboard = END,
        )
    ],
    "Secretariat": [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            '*Attache(s) for Secretariat*\n'
            "Bo Xuan @tangboxuan",
            keyboard = END,
        )
    ],
    "Standing Comm (Advisory)": [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            '*Attache(s) for Standing Comm (Advisory)*\n'
            "Jing Ying @tjingying\n"
            "Bo Xuan @tangboxuan",
            keyboard = END,
        )
    ],
    "Welfare": [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            '*Attache(s) for Welfare*\n'
            "Jing Ying @tjingying",
            keyboard = END,
        )
    ],
    "Others": [
        Reply(
            'Please direct your queries to your respective Attaches via telegram!\n'
            '\n'
            '*Attache(s) for Others*\n'
            'Cheng Zhi @cz\\_erny',
            keyboard = END,
        )
    ],
}

Claims.DATA[END] = {
    'The End!': [
        Reply(
            'We hope to see you again soon! (Use /claimsbot to go again)',
        ), 
    ],
}


# Run a simple test bot
if __name__ == '__main__':
    import json
    import os

    with open('config.json', 'r') as f:
        config = json.load(f)
    
    TOKEN = os.environ.get('TOKEN', config['telegram_bot_token'])
    PORT = os.environ.get('PORT', 5000)

    # Initialize bot
    updater = Updater(TOKEN)

    # Register bot behaviour
    updater.dispatcher.add_handler(Claims().handler)

    # Use polling for development testing
    updater.start_polling()
    updater.idle()

    # Or use webhooks for deployment
    # updater.bot.set_webhook(f'https://pressxtohonk-telegram-bot.herokuapp.com/{TOKEN}')
    # updater.start_webhook('0.0.0.0', PORT, url_path=TOKEN)
    # updater.idle()
