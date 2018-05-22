"""
Functions that are useful for asserting expected outcomes
"""

import socket
import time

DEFAULT_TIMEOUT = 20

def wait_for(test, timeout_seconds=DEFAULT_TIMEOUT):
    """
    Repeatedly calls the test function for timeout_seconds until either test
    returns a truthy value, at which point the function returns True -- or the
    timeout is exceeded, at which point it will return False.
    """
    start = time.time()
    while True:
        if test():
            return True
        if time.time() - start > timeout_seconds:
            return False
        time.sleep(0.5)


def ensure_always(test, timeout_seconds=DEFAULT_TIMEOUT):
    """
    Repeatedly calls the given test.  If it ever returns false before the timeout
    given is completed, returns False, otherwise True.
    """
    start = time.time()
    while True:
        if not test():
            return False
        if time.time() - start > timeout_seconds:
            return True
        time.sleep(0.5)


def container_cmd_exit_0(container, command):
    """
    Tests if a command run against a container returns with an exit code of 0
    """
    code, _ = container.exec_run(command)
    return code == 0


def tcp_socket_open(host, port):
    """
    Returns True if there is an open TCP socket at the given host/port
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1)
    try:
        return sock.connect_ex((host, port)) == 0
    except socket.timeout:
        return False


def has_datapoint_with_metric_name(fake_ingest, metric_name):
    """
    Returns True if the fake_ingest has any datapoints that have the given
    metric_name
    """
    for datapoint in fake_ingest.datapoints:
        if datapoint.metric == metric_name:
            return True
    return False


def has_all_dims(dp_or_event, dims):
    """
    Tests if `dims`'s are all in a certain datapoint or event
    """
    return dims.items() <= {d.key: d.value for d in dp_or_event.dimensions}.items()


def has_datapoint_with_all_dims(fake_ingest, dims):
    """
    Tests if any datapoints has all of the given dimensions
    """
    for datapoint in fake_ingest.datapoints:
        if has_all_dims(datapoint, dims):
            return True
    return False


def has_datapoint_with_dim(fake_ingest, key, value):
    """
    Tests if any datapoint received has the given dim key/value on it.
    """
    return has_datapoint_with_all_dims(fake_ingest, {key: value})
