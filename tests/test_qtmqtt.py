# flake8: noqa

"""Tests for `qtmqtt` package."""

import os
import sys

import pytest
from qtpy import QtCore, QtNetwork, QtTest

from qtmqtt import MqttClient


@pytest.fixture
def mqtt_connection(request):
    broker_location = os.path.join(
        request.config.rootdir, "internals/paho.mqtt.testing/interoperability/startbroker.py",
    )
    broker_process = QtCore.QProcess()
    python_path = sys.executable
    arguments = [broker_location]
    configuration = "localhost_testing.conf"
    broker_dir = QtCore.QFileInfo(broker_location).absoluteDir()
    if broker_dir.exists(configuration):
        arguments += [
            "-c",
            QtCore.QDir.toNativeSeparators(broker_dir.absoluteFilePath(configuration)),
        ]
        broker_process.setWorkingDirectory(broker_dir.absolutePath())
    broker_process.start(python_path, arguments)
    if not broker_process.waitForStarted():
        raise Exception("Could not start MQTT test broker.")

    max_tries = 6

    for try_counter in range(max_tries):
        socket = QtNetwork.QTcpSocket()
        socket.connectToHost("localhost", 1883)

        if socket.waitForConnected(3000):
            yield "localhost"
            break
        QtTest.QTest.qWait(5000)
    print("Could not launch MQTT test broker.")


def test_connection(qtbot, mqtt_connection):
    client = MqttClient()
    client.hostname = mqtt_connection
    with qtbot.waitSignal(client.connected, timeout=3000):
        client.connectToHost()

    with qtbot.waitSignal(client.disconnected, timeout=3000):
        client.disconnectFromHost()