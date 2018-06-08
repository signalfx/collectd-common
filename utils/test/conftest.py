from collectdtesting import fauxllectd
import sys

sys.modules['collectd'] = fauxllectd
