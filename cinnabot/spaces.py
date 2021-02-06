from datetime import datetime, timedelta
import pytz

from google.cloud.firestore import Client
from google.auth.credentials import AnonymousCredentials
from telegram import Update
from telegram.ext import CallbackContext

from .utils import Command

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
            self._spaces(update, context)
        
        # /spaces now
        elif context.args[0].lower() == 'now':
            self._spaces_now(update, context)
        
        # /spaces week
        elif context.args[0].lower() == 'week':
            self._spaces_week(update, context)
        
        # /spaces dd/mm(/yy)
        elif len(context.args) == 1:
            self._spaces_day(update, context)
        
        # /spaces dd/mm(/yy) dd/mm(/yy)
        elif len(context.args) == 2:
            self._spaces_date_range(update, context)

    def _spaces(self, update: Update, context: CallbackContext):
        """/spaces"""
        now = datetime.now()
        today = datetime(now.year, now.month, now.day) # reset time to midnight
        tomorrow = today + timedelta(days=1)
        events = self._events_between(today, tomorrow)

        # TODO: Group events by venue (cannot use firebase for this)
        display_events(events, update)


    def _spaces_now(self, update: Update, context: CallbackContext):
        """/spaces now"""
        now = datetime.now()
        events = self._events_between(now, now)

        display_events(events, update)


    def _spaces_week(self, update: Update, context: CallbackContext):
        """/spaces week"""
        now = datetime.now()
        today = datetime(now.year, now.month, now.day) # reset time to midnight
        week_later = today + timedelta(days=7)
        events = self._events_between(today, week_later)

        display_events(events, update)
        

    def _spaces_day(self, update: Update, context: CallbackContext):
        """/spaces dd/mm(/yy)"""
        text = update.message.text
        day_str = text.split()[1]

        try:
            day = format_day_string(day_str)
        except (ValueError, TypeError) as e:
            print("ERROR: ", e)
            return update.message.reply_text("Sorry that's an invalid date! Try dd/mm(/yy) instead :)")

        day_later = day + timedelta(days=1)
        events = self._events_between(day, day_later)
        display_events(events, update)


    def _spaces_date_range(self, update: Update, context: CallbackContext):
        """/spaces dd/mm(/yy) dd/mm(/yy)"""
        text = update.message.text
        date_range = text.split()[1:]

        try:
            start_date = format_day_string(date_range[0])
            end_date = format_day_string(date_range[1])
        except (ValueError, TypeError) as e:
            print("ERROR:", e)
            return update.message.reply_text("Sorry that's an invalid date! Try dd/mm(/yy) instead :)")

        events = self._events_between(start_date, end_date)
        display_events(events, update)
        

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

    
def format_event(event):
    """Return format string of event details (name, venue, start date, end date)."""
    # Each "event" is a dictionary following the schema of documents in firestore
    event_name = event['name']
    venue = event['venueName']
    start_date = str(event['startDate']).split('+')[0]
    end_date = str(event['endDate']).split('+')[0]

    # TODO: Remove seconds field from time
    response = f"Event: {event_name} \nVenue: {venue} \nStart: {start_date} \nEnd: {end_date}"

    print(80*'=')
    print(event['name'])
    print(80*'-')
    print('- Venue:', event['venueName'])
    print('- start:', event['startDate'])
    print('- end  :', event['endDate'])
    return response


def display_events(events, update):
    """Reply the user with list of events found."""
    if not events:
        update.message.reply_text("No events found!")
    else:
        for event in events:
            response = format_event(event)
            update.message.reply_text(response)


def format_day_string(day_str):
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
    
    # Test event querying (Actually this block can go in Spaces._spaces)
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
