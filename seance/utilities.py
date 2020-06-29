import datetime
from os.path import splitext


def get_timestamp_path(instance, filename):
    return f'{datetime.datetime.now().timestamp()}{splitext(filename)[0][:10]}'


class Basket:
    def __init__(self, seat_pk=None, seance_pk=None, seance_date=None):
        """
        Initializing new object
        """
        self.seat_pk = seat_pk
        self.seance_pk = seance_pk
        self.seance_date = seance_date

    def create_key(self):
        """creates key for basket object to write it in basket dict into session"""
        return f'{self.seat_pk}_{self.seance_pk}_{self.seance_date}'

