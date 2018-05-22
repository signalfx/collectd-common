"""
This is meant to be a standalone module that can be run in a base python:3
docker container that runs a simple fake ingest server that collects datapoints
and spits them back out upon request.
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import gzip
from google.protobuf import json_format

from signalfx.generated_protocol_buffers \
    import signal_fx_protocol_buffers_pb2 as sf_pbuf


def run_fake_ingest():
    """
    Fake the /v2/datapoint and /v2/event endpoints and just stick everything in
    lists that get dumped in the protobuf format upon GET requests to the server.
    """

    datapoints = []
    events = []

    class FakeIngest(BaseHTTPRequestHandler):
        """
        Simulates ingest for POST and implements a GET handler that allows
        querying sent datapoints/events
        """
        def do_GET(self):
            """
            Dump out the received datapoints and events in a pickled byte
            encoding.
            """
            obj = None
            if 'datapoint' in self.path:
                obj = sf_pbuf.DataPointUploadMessage()
                obj.datapoints.extend(datapoints)
            elif 'event' in self.path:
                obj = sf_pbuf.EventUploadMessage()
                obj.events.extend(events)
            else:
                self.send_response(404)
                self.end_headers()
                return

    
            out = obj.SerializeToString()
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            self.send_header("Content-Length", len(out))
            self.end_headers()
            self.wfile.write(out)

        def do_POST(self):
            body = self.rfile.read(int(self.headers.get('Content-Length')))
            is_json = "application/json" in self.headers.get("Content-Type")

            if "gzip" in self.headers.get("Content-Encoding", ""):
                body = gzip.decompress(body)

            if 'datapoint' in self.path:
                dp_upload = sf_pbuf.DataPointUploadMessage()
                if is_json:
                    json_format.Parse(body, dp_upload)
                else:
                    dp_upload.ParseFromString(body)
                datapoints.extend(dp_upload.datapoints)
            elif 'event' in self.path:
                event_upload = sf_pbuf.EventUploadMessage()
                if is_json:
                    json_format.Parse(body, event_upload)
                else:
                    event_upload.ParseFromString(body)
                events.extend(event_upload.events)
            else:
                self.send_response(404)
                self.end_headers()
                return

            self.send_response(200)
            self.send_header("Content-Type", "text/ascii")
            self.send_header("Content-Length", "4")
            self.end_headers()
            self.wfile.write("\"OK\"".encode("utf-8"))

    return HTTPServer(('0.0.0.0', 8080), FakeIngest).serve_forever()
