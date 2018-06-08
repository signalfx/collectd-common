"""
Logic for running collectd with a given config and plugin code
"""
from contextlib import contextmanager
import string
import tempfile

from .assertions import ensure_always
from .containers import run_container, container_ip, copy_path_into_container
from . import fake_backend


BASIC_COLLECTD_CONFIG = string.Template("""
TypesDB "/usr/share/collectd/types.db"

Hostname "test-collectd"

Interval $interval
Timeout 20
ReadThreads 5
WriteQueueLimitHigh 500000
WriteQueueLimitLow  400000

LoadPlugin logfile
<Plugin logfile>
        LogLevel "info"
        File "stdout"
        Timestamp true
        PrintSeverity true
</Plugin>

$extra_config
""")

WRITE_HTTP_TEMPLATE = string.Template("""
<LoadPlugin "write_http">
   FlushInterval 1
</LoadPlugin>
<Plugin "write_http">
  <Node "signalfx">
    URL "$url"
    User "auth"
    Password "testing"
    Format "JSON"
    BufferSize 4096
    Timeout 5
    LogHttpError true
  </Node>
</Plugin>
""")

DEFAULT_COLLECTD_IMAGE = "quay.io/signalfuse/collectd:latest"
COLLECTD_CONF_PATH = "/etc/collectd/collectd.conf"


def mount_for_local_dir(local_dir, container_dir):
    """
    Returns a dict that can be passed as the `volumes` value when running a
    docker container.  It will specify that the local_dir should be mounted in
    the container at container_dir.
    """
    return {local_dir: {"bind": container_dir, "mode": "ro"}}


@contextmanager
def run_collectd(extra_config, plugin_dir, interval=10, image=DEFAULT_COLLECTD_IMAGE):
    """
    Run collectd in a container with the given extra_config that will be
    appended to a basic core collectd configuration.

    `plugin_dir` is the path to the plugin under test on the local
    filesystem.  That directory will be mounted into the container at the same
    path.
    """
    conf = BASIC_COLLECTD_CONFIG.substitute(interval=interval,
                                            extra_config=extra_config)
    with run_collectd_with_config(conf,
                                  [(plugin_dir, "/opt/collectd-plugin")],
                                  image) as (ingest, collectd):
        yield ingest, collectd


@contextmanager
def ingest_running():
    """
    Starts up the fake ingest/metricproxy combo and also adds a write_http
    config to use that.  Yields the final config with write_http configured and
    the ingest interface
    """
    with fake_backend.run_all() as (ingest, mp_url):
        def render_config(config):
            return config + "\n" + WRITE_HTTP_TEMPLATE.substitute(url=mp_url)

        yield render_config, ingest


@contextmanager
def run_collectd_with_config(config, files=None, image=DEFAULT_COLLECTD_IMAGE):
    """
    Runs collectd with the given config content as the main collectd.conf file.

    Yields (ingest, collectd) where `ingest` is the fake backend that has the
    datapoints and events, and `collectd` is an object that has some helpful
    methods and attributes for interacting with collectd.
    """
    with ingest_running() as (render_config, ingest):
        with tempfile.NamedTemporaryFile(dir="/tmp") as conf_file:
            conf_file.write(render_config(config).encode('utf-8'))
            conf_file.flush()

            if files is None:
                files = []

            files.append((conf_file.name, COLLECTD_CONF_PATH))
            with run_container(image, files,
                               command=[
                                   "/usr/sbin/collectd", "-C", COLLECTD_CONF_PATH, "-f"
                               ]) as cont:
                def collectd_running():
                    """
                    Returns True if the collectd container is running
                    """
                    cont.reload()
                    return cont.status == "running"

                assert ensure_always(collectd_running, 5), "collectd died shortly after starting"

                class Collectd():
                    """
                    A shell class that holds some attribute and methods useful
                    for interacting with collectd.
                    """
                    container = cont

                    ip = container_ip(cont)

                    def logs(self):
                        """
                        Return the latest output from collectd
                        """
                        return self.container.logs()

                    def reconfig(self, new_config):
                        """
                        Reconfigure collectd by overwriting the config file and
                        restarting the container
                        """
                        conf_file.seek(0)
                        conf_file.truncate()
                        conf_file.write(render_config(new_config).encode('utf-8'))
                        conf_file.flush()
                        copy_path_into_container(conf_file.name, self.container, COLLECTD_CONF_PATH)
                        self.container.restart()

                yield ingest, Collectd()
