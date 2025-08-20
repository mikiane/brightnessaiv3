from ics import Calendar, Event
from dateutil import tz
from datetime import datetime

# Create a new calendar
c = Calendar()

# List of appointments
appointments = [
    ("18 JULY 2023", "9:00", "13:00"),
    ("19 JULY 2023", "12:00", "14:00"),
    ("20 JULY 2023", "15:30", "17:30"),
    ("24 JULY 2023", "13:00", "17:00"),
    ("26 JULY 2023", "12:00", "14:00"),
    ("27 JULY 2023", "13:00", "17:00"),
    ("31 JULY 2023", "13:00", "17:00"),
    ("02 AUGUST 2023", "12:00", "14:00"),
    ("04 AUGUST 2023", "13:00", "17:00"),
    ("28 AUGUST 2023", "13:00", "17:00"),
    ("31 AUGUST 2023", "13:00", "17:00")
]

# Timezone info
paris_tz = tz.gettz('Europe/Paris')

# Create events
for appointment in appointments:
    date_str, start_str, end_str = appointment

    # Parse date and time
    start_time = datetime.strptime(start_str, "%H:%M")
    end_time = datetime.strptime(end_str, "%H:%M")

    # Parse date and adjust year
    date_time = datetime.strptime(date_str, "%d %B %Y")

    # Combine date and time
    start_datetime = datetime.combine(date_time.date(), start_time.time(), tzinfo=paris_tz)
    end_datetime = datetime.combine(date_time.date(), end_time.time(), tzinfo=paris_tz)

    # Create event
    e = Event()
    e.name = "RDV Centre Services"
    e.begin = start_datetime
    e.end = end_datetime
    c.events.add(e)

# Write to file
with open("rdv_centre_services.ics", "w") as f:
    f.write(str(c))
