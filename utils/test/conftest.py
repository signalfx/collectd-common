import sys

from collectdutil import fauxllectd

sys.modules['collectd'] = fauxllectd
