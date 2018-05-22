from contextlib import contextmanager
from io import BytesIO
import tarfile
import time

import docker

from .assertions import wait_for

DOCKER_API_VERSION = "1.34"

def get_docker_client():
    """
    Create a new Docker client, using envvars to configure the client.
    """
    return docker.from_env(version=DOCKER_API_VERSION)


def print_lines(msg):
    """
    Print each line separately to make it easier to read in pytest output
    """
    for l in msg.splitlines():
        print(l)


def container_ip(container):
    """
    Returns the IP address of the container within the docker network
    """
    return container.attrs["NetworkSettings"]["IPAddress"]


def is_container_port_open(container, port):
    """
    Tests if a port in the given container is listening for TCP connections
    """
    ip = container_ip(container)
    client = get_docker_client()

    try:
        client.containers.run('busybox:1.28', 'nc -z %s %d' % (ip, port), remove=True)
        return True
    except docker.errors.ContainerError:
        return False


def copy_path_into_container(path, container, target_path):
    tario = BytesIO()
    tar = tarfile.TarFile(fileobj=tario, mode='w')

    tar.add(path, target_path)

    tar.close()

    container.put_archive("/", tario.getvalue())
    # Apparently when the above `put_archive` call returns, the file isn't
    # necessarily fully written in the container, so wait a bit to ensure it
    # is.
    time.sleep(2)


@contextmanager
def run_container(image_name, files=None, wait_for_ip=True, **kwargs):
    """
    Runs a container, putting the given files (A list of tuples of the form
    (local_path, container_path)) into the container before starting it
    """
    client = get_docker_client()
    if not image_name.startswith("sha256"):
        container = client.images.pull(image_name)
    container = client.containers.create(image_name, **kwargs)

    if files:
        for source, target in files:
            copy_path_into_container(source, container, target)

    container.start()

    def has_ip_addr():
        container.reload()
        return container_ip(container)

    if wait_for_ip:
        wait_for(has_ip_addr, timeout_seconds=5)
    try:
        yield container
    finally:
        print("Container %s logs:" % container.image)
        print_lines(container.logs())
        container.remove(force=True, v=True)
