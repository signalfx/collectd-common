"""To be imported as collectd module for unit testing (conftest.py) and development.
from collectdtesting import fauxllectd as collectd  # for any references in current module.
import sys
sys.modules['collectd'] = collectd

Desired functionality beyond dummy functions TBD.
"""
import logging


logging.basicConfig(level='DEBUG')


class Values(object):

    def __init__(self, *a, **kw):
        pass

    def dispatch(self):
        pass


def register_config(*a, **kw):
    pass


def register_read(*a, **kw):
    pass


def register_flush(*a, **kw):
    pass


def register_shutdown(*a, **kw):
    pass


def register_log(*a, **kw):
    pass


def debug(*a, **kw):
    logging.debug(*a, **kw)


def info(*a, **kw):
    logging.info(*a, **kw)


def notice(*a, **kw):
    pass


def warning(*a, **kw):
    logging.warn(*a, **kw)


def error(*a, **kw):
    logging.error(*a, **kw)


def register_notification(*a, **kw):
    pass
