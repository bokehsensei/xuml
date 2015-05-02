from collections import namedtuple

Event = namedtuple('Event', ['source', 'destination', 'event_name', 'args', 'kwargs'])
