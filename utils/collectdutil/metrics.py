"""
Common utility functions for dealing with metrics in collectd
"""

# This is only available when run in the collectd embedded python interpreter
import collectd


def encode_dimensions(dimensions=None, max_len=1022):
    """
    Encodes a dictionary of key/value pairs as a comma-delimited list of
    key=value tokens.  This string is suitable for use in the `[]` suffix
    syntax in `plugin_instance`, `host`, and `type_instance` fields.
    """
    if dimensions:
        return ','.join(['='.join(p) for p in dimensions.items()])[:max_len]
    return ''


def dispatch_values(values=None, dimensions=None,
                    plugin=None, plugin_instance=None,
                    type=None, type_instance=None,
                    plugin_instance_max_length=1024,
                    time=None, host=None, interval=None):
    """
    Dispatch a collectd value list with the given fields, using the special
    SignalFx dimension encoding.
    """

    if dimensions:
        # currently ingest parses dimensions out of the plugin_instance
        dim_string = encode_dimensions(dimensions,
                                       max_len=plugin_instance_max_length-len(plugin_instance)-2)
        plugin_instance += '[%s]' % dim_string

    value = collectd.Values(
        host=host,
        plugin=plugin,
        plugin_instance=plugin_instance,
        time=time,
        type=type,
        type_instance=type_instance,
        values=values,
        interval=interval,
        meta={'_': 0})

    if interval:
        value.interval = interval

    value.dispatch()


def dispatch_datapoint(metric_name, value, dimensions, plugin):
    """
    A convenience method that papers over some of the complexities of collectd
    value lists when you just want to send a single value
    """
    return dispatch_values(values=[value], dimensions=dimensions,
                           plugin=plugin, type=metric_name)
