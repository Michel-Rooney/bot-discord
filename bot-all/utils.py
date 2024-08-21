from datetime import datetime


def now():
    return datetime.now()


def msg_time():
    return f'[{now()}]'
