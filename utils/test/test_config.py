import pytest

from collectdutil.utils import ParsedConfig
from collectdutil.config import Config


descriptors = {
    'DescriptorOne': ('descriptor_one', False),
    'DescriptorTwo': ('descriptor_two', True),
    'DescriptorThree': ('descriptor_three', 234.0),
    'DescriptorFour': ('descriptor_four', ['one', 'two']),
    'DescriptorFive': ('descriptor_five', None),
    'DescriptorSix': ('descriptor_six', [True, False, 345])
}


def test_descriptors_without_using_defaults():
    cfg_str = '''
    DesCriptorOne true
    DescriptorTwo false
    DescripTorThree 123
    DesCriptorFour -123.456
    DescriptorFive "one" "two" "three"
    DesCriptorSix true true 123 false "test"
    Descriptorfive "four" "five"
    DescripTorFive "six"
    '''
    cfg = Config(ParsedConfig(cfg_str), descriptors=descriptors)
    assert cfg.descriptor_one is True
    assert cfg.descriptor_two is False
    assert cfg.descriptor_three == 123.0
    assert cfg.descriptor_four == -123.456
    assert cfg.descriptor_five == [['one', 'two', 'three'], ['four', 'five'], ['six']]
    assert cfg.descriptor_six == [True, True, 123.0, False, 'test']


def test_descriptors_with_using_defaults():
    cfg_str = '''
    DescrIptorOne true
    DescriptorSix true true 123 false "test"
    DescriptorFive "four" "five"
    DescripTorFive "six"
    '''
    cfg = Config(ParsedConfig(cfg_str), descriptors=descriptors)
    assert cfg.descriptor_one is True
    assert cfg.descriptor_two is True
    assert cfg.descriptor_three == 234.0
    assert cfg.descriptor_four == ['one', 'two']
    assert cfg.descriptor_five == [['four', 'five'], ['six']]
    assert cfg.descriptor_six == [True, True, 123.0, False, 'test']


metrics = {
    'metric_one': ('metric.one', 'gauge', True),
    'metric_two': ('metric.two', 'counter', False),
    'metric_three': ('metric.three', 'derive', True),
    'metric_four': ('metric.four', 'absolute', False),
}


def test_metrics_without_using_defaults():
    cfg_str = '''
    Metric "metric_one" false
    MeTric "metric_two" true
    Metric "metric_three" false
    Metric "metric_four" true
    '''
    cfg = Config(ParsedConfig(cfg_str), metrics=metrics)
    assert cfg.metric_one is False
    assert cfg.metric_two is True
    assert cfg.metric_three is False
    assert cfg.metric_four is True


def test_metrics_with_using_defaults():
    cfg_str = '''
    MetrIc "metric_two" true
    MeTric "metric_four" true
    '''
    cfg = Config(ParsedConfig(cfg_str), metrics=metrics)
    assert cfg.metric_one is True
    assert cfg.metric_two is True
    assert cfg.metric_three is True
    assert cfg.metric_four is True


def test_metrics_with_invalid_registration():
    with pytest.raises(TypeError):
        Config(ParsedConfig('Metric'), metrics=metrics)


def test_extra_dimensions():
    cfg_str = '''
    ExTraDiMension "dimension_one" "thing_one"
    EXTraDimenSion "dimension_two" "thing_two"
    ExtraDimension "dimension_three" "one"
    ExtraDimension "dimension_three" "two"
    ExtraDimension "invalid" "too" "many" "arguments"
    ExtraDimension "invalid"
    '''
    cfg = Config(ParsedConfig(cfg_str))
    assert cfg.extra_dimensions == dict(
        dimension_one='thing_one',
        dimension_two='thing_two',
        dimension_three='two'
    )
