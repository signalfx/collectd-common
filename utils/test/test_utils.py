from collectdutil.utils import ParsedConfig


def test_parsed_config():
    config_string = ('\n\n\n\t\t\t\t     Key1 "Value1"\n\n\n\n\n\t\t\t\t\t  \n\n\n Key2 "Value2" "Value3"\n\t\t'
                     '\t\t\tKey3 true\n Key4 false\nKey5 100\n\n\n Key5 200\n\n\nKey6 "multiple component" '
                     '"strings with spaces"')
    config = ParsedConfig(config_string)
    children = config.children
    assert children
    child = children[0]
    assert child.key == 'Key1'
    assert child.values == ['Value1']
    child = children[1]
    assert child.key == 'Key2'
    assert child.values == ['Value2', 'Value3']
    child = children[2]
    assert child.key == 'Key3'
    assert child.values == [True]
    child = children[3]
    assert child.key == 'Key4'
    assert child.values == [False]
    child = children[4]
    assert child.key == 'Key5'
    assert child.values == [100]
    child = children[5]
    assert child.key == 'Key5'
    assert child.values == [200]
    child = children[6]
    assert child.key == 'Key6'
    assert child.values == ['multiple component', 'strings with spaces']
