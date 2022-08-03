from source.Database import database
from source.utils.Reminder import Reminder


Reminder.notify_blink_average(database.get_session_average())
