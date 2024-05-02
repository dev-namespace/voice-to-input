#!/usr/bin/env python

import docker, time

CONTAINER_NAME = "voice-server"
client = docker.from_env()

def is_whisper_running():
    containers = client.containers.list()
    for container in containers:
        if container.image.tags[0] == "%s:latest" % CONTAINER_NAME:
            return True

def run_whisper(docker_port = 5000, host_port = 5000):
    try:
        print("Starting whisper-server...")
        client.containers.run("%s:latest" % CONTAINER_NAME, detach=True, ports={'%s/tcp' % docker_port: host_port})

        print("Let's give some time for the server to start...")
        is_active = False

        is_active = False
        while not is_active:
            print("...")
            is_active = ping_port("localhost", host_port)
            time.sleep(1)

        print("[*] Started %s" % CONTAINER_NAME)
        print("[!] %s is running on http://localhost:%s" % (CONTAINER_NAME, host_port))
    except Exception as e:
        print("[!] %s could not be started" % CONTAINER_NAME)
        print(e)
        raise e

def stop_whisper():
    print("Stopping whisper-server...")
    containers = client.containers.list()
    for container in containers:
        if container.image.tags[0] == "%s:latest" % CONTAINER_NAME:
            container.stop()
            print("[*] Stopped %s" % CONTAINER_NAME)
            return
    print("[!] %s not found" % CONTAINER_NAME)

import socket

def ping_port(host, port, timeout=1):
    """
    Try to establish a TCP connection to the specified host and port.
    If successful, return True, otherwise return False.
    """
    try:
        sock = socket.create_connection((host, port), timeout)
        sock.close()
        return True
    except (socket.timeout, socket.error):
        return False

if __name__ == "__main__":
    print("Checking if whisper-server is running...")
    print(is_whisper_running())
    if not is_whisper_running():
        run_whisper()
    stop_whisper()
