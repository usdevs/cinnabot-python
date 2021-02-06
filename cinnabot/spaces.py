from datetime import datetime, timedelta
import logging
import pytz

from google.cloud.firestore import Client
from google.auth.credentials import AnonymousCredentials
from telegram import Update, ParseMode
from telegram.ext import CallbackContext

from cinnabot import Command

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO,
)

logger = logging.getLogger(__name__)

class Spaces(Command):
    command = 'spaces'
    help_text = 'list of space bookings'
    help_full = (
        "To use the '/spaces' command, type one of the following:\n"
        "'/spaces' : to view all bookings for today\n"
        "'/spaces now' : to view bookings active at this very moment\n"
        "'/spaces week' : to view all bookings for this week\n"
        "'/spaces dd/mm(/yy)' : to view all bookings on a specific day\n"
        "'/spaces dd/mm(/yy) dd/mm(/yy)' : to view all bookings in a specific range of dates"
    )

    def __init__(self, database: Client):
        self.db = database

    def callback(self, update: Update, context: CallbackContext):
        """Delegates behaviour to sub-handlers depending on input format"""
        # /spaces
        if not context.args:
            self.spaces(update, context)
        
        # /spaces now
        elif context.args[0].lower() == 'now':
            self.spaces_now(update, context)
        
        # /spaces week
        elif context.args[0].lower() == 'week':
            self.spaces_week(update, context)
        
        # /spaces dd/mm(/yy)
        elif len(context.args) == 1:
            self.spaces_day(update, context)
        
        # /spaces dd/mm(/yy) dd/mm(/yy)
        elif len(context.args) == 2:
            self.spaces_date_range(update, context)

    def spaces(self, update: Update, context: CallbackContext):
        """/spaces"""
        now = datetime.now()
        today = datetime(now.year, now.month, now.day) # reset time to midnight
        tomorrow = today + timedelta(days=1)
        
        events = self._events_between(today, tomorrow)
        text = '\n'.join([
            f'Displaying bookings for today',
            '',
            self._format_events(events),
        ])
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    def spaces_now(self, update: Update, context: CallbackContext):
        """/spaces now"""
        now = datetime.now()

        events = self._events_between(now, now)        
        text = '\n'.join([
            f'Displaying ongoing bookings',
            '',
            self._format_events(events),
        ])
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    def spaces_week(self, update: Update, context: CallbackContext):
        """/spaces week"""
        now = datetime.now()
        today = datetime(now.year, now.month, now.day) # reset time to midnight
        week_later = today + timedelta(days=7)

        events = self._events_between(today, week_later)
        text = '\n'.join([
            f'Displaying bookings up to a week from today',
            '',
            self._format_events(events),
        ])
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    def spaces_day(self, update: Update, context: CallbackContext):
        """/spaces dd/mm(/yy)"""
        day_str = context.args[0]

        try:
            day = self._format_day_string(day_str)
        except (ValueError, TypeError) as e:
            logger.error(e)
            update.message.reply_text("Sorry that's an invalid date! Try dd/mm(/yy) instead :)")
            return
        
        day_later = day + timedelta(days=1)
        events = self._events_between(day, day_later)
        text = '\n'.join([
            f'Displaying bookings for {day.date()}',
            '',
            self._format_events(events),
        ])
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)

    def spaces_date_range(self, update: Update, context: CallbackContext):
        """/spaces dd/mm(/yy) dd/mm(/yy)"""
        date_range = context.args

        try:
            start_date = self._format_day_string(date_range[0])
            end_date = self._format_day_string(date_range[1])
        except (ValueError, TypeError) as e:
            logger.error(e)
            update.message.reply_text("Sorry that's an invalid date! Try dd/mm(/yy) instead :)")
            return
        
        events = self._events_between(start_date, end_date)
        text = '\n'.join([
            f'Displaying bookings between {start_date.date()} and {end_date.date()}',
            '',
            self._format_events(events),
        ])
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
        
    def _events_between(self, start_time: datetime, end_time: datetime):
        """gets a set of events (E) overlapping with some interval [start_time, end_time].
        
        E = {event : event.startDate <= end_time & event.endDate >= start_time}
        
        Sadly, firebase doesn't let us perform two inequality queries on different fields
        simultaneously, so we perform the less intensive query locally.
        """
        # Convert to datatype that plays well with firestore's timestamp
        start_time = pytz.UTC.localize(start_time)
        end_time = pytz.UTC.localize(end_time)

        # Query: event.endDate >= start_time
        not_ended = self.db.collection('events') \
            .where('endDate', '>=', start_time) \
            .get()

        # Query: event.startDate <= end_time
        events = [event.to_dict() for event in not_ended]
        events = [event for event in events if event.get('startDate') <= end_time]
        
        return events
    
    def _format_events(self, events):
        """Return format string of event details (name, venue, start date, end date)."""
        # refer to https://strftime.org/ for formatting details
        date_format = '%I:%M%p, %a %d %b %y'

        # Group events by venue
        events_by_venue = dict()
        for event in events:
            venue = event['venueName']
            if venue not in events_by_venue:
                 events_by_venue[venue] = list()
            events_by_venue[venue].append(event)

        # Build formatted message
        lines = list()
        for venue, venue_events in events_by_venue.items():
            lines.extend([
                '====================',
                f'🌌*{venue}*',
                '====================',
            ])
            for event in sorted(venue_events, key=lambda x: x['startDate']):
                event_name = event['name']
                start_date = event['startDate']
                end_date = event['endDate']

                lines.extend([
                    f'*{event_name}*',
                    f'- {start_date.strftime(date_format)} to',
                    f'- {end_date.strftime(date_format)}',
                ])
                
                # if start_date == end_date:
                #     lines.append(f'*{event_name}*: {start_time} to {end_time}, {end_date}')
                # else:
                #     lines.append(f'*{event_name}*: {start_time}, {start_date} to {end_time}, {end_date}')
            lines.append('')
        
        # Handle cases when events query returns no results
        if lines:
            text = '\n'.join(lines)
        else:
            text = 'No events found!'

        return text

    def _format_day_string(self, day_str):
        """Takes in string dd/mm(/yy) and returns datetime object. Returns ValuError otherwise."""
        date_fields = day_str.split('/')

        if len(date_fields) == 2:
            # dd/mm
            day_str += '/' + str(datetime.now().year)       # Append year
            day = datetime.strptime(day_str, "%d/%m/%Y")    # Str to datetime
        elif len(date_fields) == 3:
            # dd/mm/yy
            day = datetime.strptime(day_str, "%d/%m/%y")    # %y for last 2 digits of year
        else:
            raise ValueError

        return day


if __name__ == "__main__":
    from datetime import datetime, timedelta
    from google.cloud.firestore import Client

    # Initialize a backend with a firestore client
    firestore = Client(project='usc-website-206715')
    spaces = Spaces(database=firestore)
    
    # Test event querying (Actually this block can go in Spaces.spaces)
    now = datetime.now()
    today = datetime(now.year, now.month, now.day) # reset time to midnight
    tomorrow = today + timedelta(days=1)

    events = spaces._events_between(today, tomorrow)

    for event in events:
        # Each "event" is a dictionary following the schema of documents in firestore
        print(80*'=')
        print(event['name'])
        print(80*'-')
        print('- Venue:', event['venueName'])
        print('- start:', event['startDate'])
        print('- end  :', event['endDate'])
