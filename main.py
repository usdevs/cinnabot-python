# Standard library imports
import json

# 3rd party imports
from telegram.ext import PicklePersistence, Updater

# Local imports
from cinnabot import Command, Conversation
from cinnabot.base import Start, About, Help
# from cinnabot.feedback import Feedback
# from cinnabot.laundry import Laundry
from cinnabot.resources import Resources
# from cinnabot.spaces import Spaces
from cinnabot.travel import PublicBus, NUSBus, NUSMap 

# Initialize to check that all requirements defined in utils.py have been met.
FEATURES = [
	Start(), 
	About(),
	Help(),
	# Feedback(),
	# Laundry(),
	Resources(),
	# Spaces(),
	# PublicBus(), 
	NUSBus(),
	NUSMap(),
]

def main():
	# Read config
	with open('config.json', 'r') as f:
		config = json.load(f)

	# The updater primarily gets telegram updates from telegram servers
	cinnabot = Updater(
		token = config['telegram_bot_token'], 
		persistence = PicklePersistence(config['persistence_file']),
	)

	# The dispatcher routes updates to the first matching handler
	for feature in FEATURES:
		cinnabot.dispatcher.add_handler(feature.handler)

	# Store data for /help and /help <feature> in the bot
	cinnabot.dispatcher.bot_data['help_text'] = dict()
	cinnabot.dispatcher.bot_data['help_full'] = dict()
	for feature in FEATURES:
		cinnabot.dispatcher.bot_data['help_text'][feature.command] = feature.help_text
		cinnabot.dispatcher.bot_data['help_full'][feature.command] = feature.help_full

	# Run the bot!
	# cinnabot.start_webhook() # For deployment
	cinnabot.start_polling()
	cinnabot.idle()

if __name__ == '__main__':
	main()