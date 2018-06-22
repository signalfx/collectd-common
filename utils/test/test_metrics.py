try:
    from collections import OrderedDict
except ImportError:
    from ordereddict import OrderedDict

from time import time

from collectdutil.metrics import Metric, encode_dimensions


def test_encode_dimensions():
    dimensions = OrderedDict()
    dimensions['one'] = 'one_val'
    dimensions['two'] = 'two_val'
    dimensions['three'] = 'three_val'
    dimensions['four'] = 123.456
    encoded = encode_dimensions(dimensions)
    assert encoded == 'one=one_val,two=two_val,three=three_val,four=123.456'


def test_metric_attributes():
    current = time()
    dimensions = dict(one=1, two=2, three=3)
    metric = Metric(type_instance='ti', type='type', value=1, plugin='p', plugin_instance='pi', host='host',
                    dimensions=dimensions, time=current, interval=10)
    assert metric.type_instance == 'ti'
    assert metric.type == 'type'
    assert metric.value == 1
    assert metric.plugin == 'p'
    assert metric.plugin_instance == 'pi'
    assert metric.host == 'host'
    assert metric.dimensions == dimensions
    assert metric.encoded_dimensions
    assert metric.time == current
    assert metric.interval == 10


def test_encoded_metric_dimensions():
    dimensions = OrderedDict()
    dimensions['one'] = 'one_val'
    dimensions['two'] = 'two_val'
    dimensions['three'] = 'three_val'
    metric = Metric(type_instance='ti', type='type', value=1, plugin='', plugin_instance='pi',
                    dimensions=dimensions)
    assert metric.encoded_dimensions == 'one=one_val,two=two_val,three=three_val'
    assert str(metric)  # confirm no exceptions from __str__()
