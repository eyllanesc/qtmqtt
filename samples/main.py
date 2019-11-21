import os
from functools import partial

os.environ["QT_API"] = "PySide2"

from qtpy import QtCore

from qtmqtt import (MqttClient, MqttMessage, MqttSubscription, MqttTopicFilter,
                    MqttTopicName, SubscriptionState)


class Receiver(QtCore.QObject):
    def __init__(self, parent=None):
        super(Receiver, self).__init__(parent)
        self.client = MqttClient(self)
        self.client.connected.connect(self.on_connected)
        self.client.disconnected.connect(self.on_disconnect)
        # self.client.messageSent.connect(self.on_messageSent)
        # self.client.messageReceived.connect(self.on_messageReceived)
        self.client.hostname = "broker.hivemq.com"
        self.client.connectToHost()
        self.timer = QtCore.QTimer(interval=100)
        self.timer.timeout.connect(self.publish)
        self.m_counter = 0

    def on_connected(self):
        self.timer.start()
        subscription = self.client.subscribe(MqttTopicFilter("+/bar"))
        subscription.messageReceived.connect(
            partial(self.on_messageReceived_sub, subscription)
        )
        subscription.stateChanged.connect(self.on_stateChanged_sub)

    def on_stateChanged_sub(self, state):
        if state == SubscriptionState.Unsubscribed:
            self.client.disconnectFromHost()

    def on_messageReceived_sub(self, sub, msg):
        print("on_messageReceived_sub", sub, msg.payload)
        if msg.payload == b"200":
            print("unsubscribe")
            self.client.unsubscribe(sub.topic)

    def on_disconnect(self):
        print("on_disconnect")
        self.timer.stop()
        QtCore.QCoreApplication.quit()

    def on_messageSent(self, mid):
        print("on_messageSent", mid)

    def publish(self):
        mid = self.client.publish("foo/bar", str(self.m_counter).encode())
        print(mid)
        self.m_counter += 1

    @QtCore.Slot(bytes, MqttTopicName)
    def on_messageReceived(self, msg, topic):
        print("on_messageReceived", msg, topic)


if __name__ == "__main__":
    import sys

    app = QtCore.QCoreApplication(sys.argv)
    rec = Receiver()
    sys.exit(app.exec_())
