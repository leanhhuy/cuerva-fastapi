import datetime
import time
from datetime import timedelta

class DateTimeUtil(object):
    @staticmethod
    def readTimeStamp(timeStamp):
        # result = datetime.datetime.fromtimestamp(timeStamp, pytz.timezone("Europe/Madrid"))
        # result = datetime.datetime.utcfromtimestamp(int(timeStamp) + 3600)
        result = datetime.datetime.utcfromtimestamp(timeStamp)
        return result

    @staticmethod
    def to_timezone_naive(dtime):
        if DateTimeUtil.is_timezone_aware(dtime):
            utcoffset = dtime.utcoffset()
            seconds = utcoffset.seconds
            result = dtime.replace(tzinfo=None)
            result -= timedelta(seconds=seconds)
            return result
        else:
            return dtime

    @staticmethod
    def is_timezone_aware(dtime):
        tzinfo = dtime.tzinfo
        if tzinfo is None:
            return False
        else:
            return True