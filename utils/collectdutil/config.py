"""
Functions to help with collectd config objects.

See https://collectd.org/documentation/manpages/collectd-python.5.shtml#config
for a description of the config class passed into Python plugins by collectd.
"""


def simple_config_to_dict(conf):
    """
    Converts a basic collectd config object to a dictionary, flattening any values
    that only have a single item into that single item as the value.

    If a config key appears more than once, the value in the dict will be a
    list of all of its occurrances.

    This does NOT support config instances with children config objects.
    """
    out = {}

    for val in conf.children:
        flattened_val = val.values
        if len(val.values) == 1:
            flattened_val = val.values[0]

        prev = out.get(val.key)
        if prev is not None:
            if not isinstance(prev, (list, tuple)):
                prev = [prev]

            flattened_val = prev + [flattened_val]

        out[val.key] = flattened_val

    return out
