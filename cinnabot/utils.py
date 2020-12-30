"""Contains some Abstract Base Classes (ABCs) to define interfaces that developers should follow.

Description
-----------
ABCs cannot be directly instantiated and their subclasses must implement the properties and methods
defined in the parent ABC. Features should always subclass these ABCs, and new features should be
written starting with it's ABC to ensure some standardization.

Motivation
----------
- Enforce standardized implementations across the project.
- Keep functionality and documentation for a feature within a single class.
- Allow editing of project-level features (logging, caching, etc.) if necessary.

Note
----
Guess who's secretly an OOP hoe,,, But also, python isn't java and shouldn't be treated as such!
We can see how this plays out and ditch it if it's more trouble than it's worth HAHA.
"""
import logging

from abc import ABC, abstractmethod

from telegram import Update
from telegram.ext import CallbackContext, CommandHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

class Command(ABC):
    """Interface for implementing a simple command.

    Requirements
    ------------
    command: str
        The command name without the slash
    help_text: str
        Simple one line help for /help 
    help_full: str
        A detailed user guide for /help <function>
    callback(update: Update, context: CallbackContext) -> None
        The callback to handle this command. Feature implementation goes here.
    """

    @property
    def handler(self):
        """Automatically builds a handler from the command and callback"""
        return CommandHandler(self.command, self.logged_callback)

    def logged_callback(self, update: Update, context: CallbackContext):
        """Adds logging to all commands"""
        user_id = update.message.from_user.id
        command = '/' + self.command + ' ' + ' '.join(context.args)
        logger.info(f'{user_id}: {command}')
        return self.callback(update, context)

    @property
    @abstractmethod
    def command(self):
        """Returns a string for this command's name without the slash."""
        return

    @property
    @abstractmethod
    def help_text(self):
        """Returns a short description of this command."""
        return
    
    @property
    @abstractmethod
    def help_full(self):
        """Returns a detailed user guide to this command."""
        return
    
    @abstractmethod
    def callback(self, update: Update, context: CallbackContext):
        """Defines the bot behaviour when the command is matched."""
        return


class Conversation(ABC):
    @property
    @abstractmethod
    def handler(self):
        """Returns a `telegram.ext.ConversationHandler` for this conversation"""
        return

    @property
    @abstractmethod
    def command(self):
        """Returns the conversation's entry point command without the slash."""
        return

    @property
    @abstractmethod
    def help_text(self):
        """Returns a short description of this command."""
        return
    
    @property
    @abstractmethod
    def help_full(self):
        """Returns a detailed user guide to this command."""
        return
