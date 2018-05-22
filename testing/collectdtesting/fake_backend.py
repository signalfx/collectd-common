"""
Logic pertaining to faking out the ingest server that collectd sends datapoints
to.
"""
from functools import partial as p
from contextlib import contextmanager
from io import BytesIO
import os
import string
import tempfile

from signalfx.generated_protocol_buffers \
    import signal_fx_protocol_buffers_pb2 as sf_pbuf
import requests

from .assertions import wait_for
from .containers import container_ip, get_docker_client, run_container, is_container_port_open

INGEST_DOCKERFILE = """
FROM python:3.6

WORKDIR /opt/lib
RUN pip install 'signalfx>=1.0' 'docker>=3.0.0'

ENTRYPOINT [ "python", "-u", "-c", "from collectdtesting import fake_ingest; fake_ingest.run_fake_ingest()" ]
"""


@contextmanager
def run_ingest():
    """
    Starts up a new fake ingest that will run on a random port.  The returned
    object will have properties on it for datapoints and events. The fake
    server will be stopped once the context manager block is exited.

    This is actually implemented by running the run_fake_ingest function in the
    fake_ingest.py module in a separate docker container so that this will work
    transparently when this function is executed on a Mac, since it is very
    difficult/hacky to refer back to the Mac host from a Docker container
    (which is where collectd/metricproxy run).  The following is moderately
    less hacky and more reliable.
    """

    test_package_dir = os.path.dirname(__file__)
    dockerfile = INGEST_DOCKERFILE.format(test_package=test_package_dir)

    client = get_docker_client()
    test_code_image, _ = client.images.build(
        fileobj=BytesIO(dockerfile.encode("utf-8")),
        rm=True, forcerm=True)

    with run_container(test_code_image.id,
                       [(test_package_dir, "/opt/lib/collectdtesting")],
                       ports={"8080/tcp": None}) as ingest_cont:

        local_port = ingest_cont.attrs["NetworkSettings"]["Ports"]["8080/tcp"][0]["HostPort"]
        assert wait_for(p(is_container_port_open, ingest_cont, 8080)), "fake ingest didn't start"

        class FakeBackend:
            """
            Encapsulates all of the things that users of this service need to know
            """
            host = container_ip(ingest_cont)
            port = 8080
            url = "http://%s:%d" % (host, port)
            local_url = "http://127.0.0.1:%s" % (local_port,)

            @property
            def datapoints(self):
                """
                Fetch the datapoints from the fake ingest and deserialize them
                """
                resp = requests.get(self.local_url + "/datapoints")
                dp_message = sf_pbuf.DataPointUploadMessage()
                dp_message.ParseFromString(resp.content)
                return dp_message.datapoints

            @property
            def events(self):
                """
                Fetch the events from the fake ingest and deserialize them
                """
                resp = requests.get(self.local_url + "/events")
                event_message = sf_pbuf.EventUploadMessage()
                event_message.ParseFromString(resp.content)
                return event_message.events

        yield FakeBackend()


METRICPROXY_CONFIG = string.Template("""
{
    "ForwardTo": [
        {
            "DefaultAuthToken": "test",
            "Name": "forwarder-to-fake-ingest",
            "type": "signalfx",
            "URL": "${ingest_url}/v2/datapoint",
            "EventURL": "${ingest_url}/v2/event"
        }
    ],
    "ListenFrom": [
        {
            "ListenAddr": "0.0.0.0:18080",
            "Type": "collectd"
        }
    ],
    "LogDir": "-"
}
""")


@contextmanager
def run_metric_proxy(ingest_url):
    """
    Run metricproxy to get the output from collectd and convert it to SignalFx
    datapoints.  Metrixproxy will then forward the datapoints to the fake
    ingest.

    See https://github.com/signalfx/metricproxy for config details.
    """
    with tempfile.NamedTemporaryFile(dir="/tmp") as conf_file:
        conf_file.write(METRICPROXY_CONFIG.substitute(ingest_url=ingest_url).encode('utf-8'))
        conf_file.flush()

        with run_container("quay.io/signalfx/metricproxy:v0.10.5",
                           [(conf_file.name, "/var/config/sfproxy/sfdbproxy.conf")]) \
                as mp_cont:

            assert wait_for(p(is_container_port_open, mp_cont, 18080)), \
                "metricproxy didn't start"
            yield "http://%s:18080/post-collectd" % (container_ip(mp_cont),)


@contextmanager
def run_all():
    """
    Runs the fake ingest server and metric proxy wired up to it so that
    collectd can post to metric proxy but we can assert against the final
    datapoints that would be seen by ingest
    """
    with run_ingest() as fake_ingest:
        with run_metric_proxy(fake_ingest.url) as mp_url:
            yield fake_ingest, mp_url
