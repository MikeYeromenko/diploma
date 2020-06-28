from rest_framework.exceptions import APIException


class DateFormatError(APIException):
    status_code = 400
    default_detail = 'GET-parameter "date" has wrong format.'
    default_code = 'wrong_date_in_request'


class DatePassedError(APIException):
    status_code = 400
    default_detail = 'GET-parameter "date" sets time, that had passed. It must have present or future value.'
    default_code = 'date_in_request_passed'


class DateEssential(APIException):
    status_code = 400
    default_detail = 'GET-parameter "date" must be to get full info about seance and free seats.'
    default_code = 'date_essential'


class OrderingFormatError(APIException):
    status_code = 400
    default_detail = 'GET-parameter "ordering" has wrong value not in [expensive, cheap].'
    default_code = 'wrong_ordering_in_request'
