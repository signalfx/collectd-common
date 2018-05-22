# Collectd Utils

A Python package that provides some common functionality for writing collectd
Python-based plugins.

It will also provide testing infrastructure for doing integration tests with
the collectd plugin.

## Best Practices

When writing a collectd Python plugin you should adhere to the following
guidelines:

 - Do **NOT** use module-level (global) variables, except for constants.

 - In keeping with the first point, each time the *configure* callback
     registered by your plugin is called, you should register one or more read
     callbacks associated with that configuration.  **Avoid** the pattern where
     configuration is appended to a module-level list variable that gets used
     by a single read callback function.

 - Collectd has a boolean config value type, which consists of the values
     `true` and `false` (without quotes).  They will be converted automatically
     by collectd to the Python boolean equivalents.  If your config takes
     boolean values, use that instead of strings such as `"true"`, `"yes"`,
     etc.

 - Collectd config supports repeated keys (keys with the same name multiple
     times) in the same config block.  It also supports multiple values after a
     single key (e.g. `Databases mydb1 mydb2`).  It is particularly useful to
     combine these two techniques when specifying key/value options, such as
     extra dimensions to add to metrics (`Dimension env prod` for a dimension
     with key `env` and value `prod`).  There should almost never be any need
     to use JSON or any other list/object encoding in collectd config given
     these two facilities.

 - By using the technique described in the previous point, make sure your
     plugin supports specifying extra dimensions that get applied to all
     datapoints.  This is necessary for Smart Agent support.

 - Have a config option for the read interval within a given plugin config.
     When you register the read callback, you can pass this interval as the
     `interval` keyword arg.  The conventional config name for this is
     `Interval`.

 - If your plugin does multiple independent operations (e.g. derives metrics
     independently from two separate endpoints on a service), consider
     registering multiple read callbacks to take better advantage of the
     collectd read thread pool.

## Reference

[collectd-python manpage](https://collectd.org/documentation/manpages/collectd-python.5.shtml) -
  This documents the Python interface fairly well.
