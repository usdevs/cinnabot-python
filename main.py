# 3rd party imports
from telegram.ext import PicklePersistence, Updater, CallbackQueryHandler

# Local imports
from cinnabot.base import Start, About, Help
from cinnabot.claims import Claims
from cinnabot.feedback import Feedback
# from cinnabot.laundry import Laundry
from cinnabot.resources import Resources
from cinnabot.spaces import Spaces
from cinnabot.travel import PublicBus, NUSBus, NUSMap 
from google.cloud.firestore import Client
from google.auth.credentials import AnonymousCredentials


# Initialize a backend with a firestore client
firestore = Client(
	project='usc-website-206715',
	credentials=AnonymousCredentials(),
)

# Initialize to check that all requirements defined in utils.py have been met.
FEATURES = [
	Start(), 
	About(),
	Spaces(database=firestore),
	Claims(),
	NUSMap(),
	Feedback(),
	Resources(),
	NUSBus(),
	Help(),
]

def make_cinnabot(token):
	"""Helps initialize an updater with our features"""
	# The updater primarily gets telegram updates from telegram servers
	updater = Updater(token)

	# The dispatcher routes updates to the first matching handler
	for feature in FEATURES:
		updater.dispatcher.add_handler(feature.handler)

	# Ad-hoc handler registration for inline keyboards ):
	updater.dispatcher.add_handler(CallbackQueryHandler(NUSBus().refresh, pattern='^NUSBus.refresh.*$'))

	# Store data for /help and /help <feature> in the bot
	updater.dispatcher.bot_data['help_text'] = dict()
	updater.dispatcher.bot_data['help_full'] = dict()
	for feature in FEATURES:
		updater.dispatcher.bot_data['help_text'][feature.command] = feature.help_text
		updater.dispatcher.bot_data['help_full'][feature.command] = feature.help_full

	return updater

if __name__ == '__main__':
	import logging

	logging.basicConfig(
		format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
		level=logging.INFO,
	)

	logger = logging.getLogger(__name__)
	
	# Deploy using webhooks if on server
	try:
		import os
		TOKEN = os.environ['TOKEN']
		HOST = os.environ['HOST']
		PORT = os.environ.get('PORT', 5000)
		logger.info(f'Deploying on webhook...')
		cinnabot = make_cinnabot(TOKEN)
		cinnabot.bot.set_webhook(f'{HOST}/{TOKEN}')		
		cinnabot.start_webhook('0.0.0.0', PORT, url_path=TOKEN)
		cinnabot.idle()
	
	# Fallback to polling (likely to be local development)
	except KeyError:
		import json
		with open('config.json', 'r') as f:
			config = json.load(f)
			TOKEN = config.get('telegram_bot_token')
		logger.warning(f'Deploying locally...')
		cinnabot = make_cinnabot(TOKEN)
		cinnabot.start_polling()
		cinnabot.idle()

	# Deployment failed?
	except Exception as e:
		logger.error(e)
