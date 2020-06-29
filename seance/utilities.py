import datetime
from os.path import splitext


def get_timestamp_path(instance, filename):
    return f'{datetime.datetime.now().timestamp()}{splitext(filename)[0][:10]}'
