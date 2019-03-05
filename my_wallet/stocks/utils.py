import datetime
from django.utils import timezone


def find_quote_day(date, num_days=0, type='earlier'):
    quote_day = date - timezone.timedelta(days=num_days)

    if type == 'earlier':
        if quote_day.weekday() == 6:
            quote_day -= timezone.timedelta(days=2)
            return quote_day
        return quote_day

    elif type == 'later':
        if quote_day.weekday() == 6:
            quote_day -= datetime.timedelta(days=2)
            return quote_day
        quote_day -= datetime.timedelta(days=1)
        return quote_day
