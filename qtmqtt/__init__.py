# -*- coding: utf-8 -*-

"""Top-level package for QtMQTT."""

__author__ = """Edwin Yllanes"""
__email__ = "e.yllanescucho+removethisifyouarehuman@gmail.com"
__version__ = "0.1.0"

import typing

import paho.mqtt.client as mqtt
from qtpy import QtCore


class ProtocolVersion:
    MQTT_3_1 = mqtt.MQTTv31
    MQTT_3_1_1 = mqtt.MQTTv311


class ClientState:
    Disconnected = 0
    Connecting = 1
    Connected = 2


class ClientError:
    NoError = 0
    InvalidProtocolVersion = 1
    IdRejected = 2
    ServerUnavailable = 3
    BadUsernameOrPassword = 4
    NotAuthorized = 5
    UnknownError = 258


class SubscriptionState:
    Unsubscribed = 0
    SubscriptionPending = 1
    Subscribed = 2
    UnsubscriptionPending = 3
    Error = 4


class MqttMessage:
    def __init__(self) -> None:
        self._payload: str = ""

    def __str__(self) -> str:
        return self.payload.decode()

    @property
    def payload(self) -> str:
        return self._payload


class MqttTopicName:
    def __init__(self, name: str) -> None:
        self.m_name = name

    @property
    def name(self) -> str:
        return self.m_name


class MqttTopicFilter:
    def __init__(self, filter: str = "") -> None:
        self._filter = filter

    @property
    def filter(self) -> str:
        return self._filter

    def match(self, topic: MqttTopicName) -> bool:
        return mqtt.topic_matches_sub(self.filter, topic.name)

    def __eq__(self, other: typing.Any) -> bool:
        if not isinstance(other, MqttTopicFilter):
            return False
        return self is other or self.filter == other.filter

    def __hash__(self) -> int:
        return hash(self.filter)


class MqttSubscription(QtCore.QObject):
    qosChanged = QtCore.Signal(int)
    stateChanged = QtCore.Signal(int)
    messageReceived = QtCore.Signal(MqttMessage)

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super(MqttSubscription, self).__init__(parent)
        self.m_qos = 0
        self.m_state = SubscriptionState.Unsubscribed
        self.m_topic = None
        self.m_client = None

    @QtCore.Property(int, notify=qosChanged)
    def qos(self) -> int:
        return self.m_qos

    @QtCore.Property(int, notify=stateChanged)
    def state(self) -> int:
        return self.m_state

    @QtCore.Property(MqttTopicFilter)
    def topic(self) -> MqttTopicFilter:
        return self.m_topic

    def setState(self, s: MqttTopicFilter) -> None:
        if self.m_state == s:
            return
        self.m_state = s
        self.stateChanged.emit(s)


class MqttClient(QtCore.QObject):
    cleanSessionChanged = QtCore.Signal(bool)
    clientIdChanged = QtCore.Signal(str)
    errorChanged = QtCore.Signal(int)
    hostnameChanged = QtCore.Signal(str)
    keepAliveChanged = QtCore.Signal(int)
    passwordChanged = QtCore.Signal(str)
    portChanged = QtCore.Signal(int)
    protocolVersionChanged = QtCore.Signal(int)
    stateChanged = QtCore.Signal(int)
    usernameChanged = QtCore.Signal(str)

    connected = QtCore.Signal()
    disconnected = QtCore.Signal()
    messageSent = QtCore.Signal(int)
    messageReceived = QtCore.Signal(bytes, MqttTopicName)

    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super(MqttClient, self).__init__(parent)
        self.m_hostname = ""
        self.m_port = 1883
        self.m_clientId = ""
        self.m_keepAlive = 60
        self.m_protocolVersion = ProtocolVersion.MQTT_3_1_1
        self.m_state = ClientState.Disconnected
        self.m_error = ClientError.NoError
        self.m_username = ""
        self.m_password = ""
        self.m_cleanSession = True

        self.m_connection = MqttConnection(self)
        self.m_connection.setClient(self)

    @QtCore.Property(bool, notify=cleanSessionChanged)
    def cleanSession(self) -> bool:
        return self.m_cleanSession

    @cleanSession.setter
    def cleanSession(self, v: bool) -> None:
        if self.m_cleanSession == v:
            return
        self.m_cleanSession = v
        self.cleanSessionChanged.emit(v)

    def get_clientId(self) -> str:
        return self.m_clientId

    def set_clientId(self, v: str) -> None:
        if self.m_clientId == v:
            return
        self.m_clientId = v
        self.clientIdChanged.emit(v)

    clientId = QtCore.Property(
        str, fget=get_clientId, fset=set_clientId, notify=clientIdChanged,
    )

    @QtCore.Property(int, notify=errorChanged)
    def error(self) -> int:
        return self.m_error

    @error.setter
    def error(self, v: int) -> None:
        if self.m_error == v:
            return
        self.m_error = v
        self.errorChanged.emit(v)

    def get_hostname(self) -> str:
        return self.m_hostname

    def set_hostname(self, v: str) -> None:
        if self.m_hostname == v:
            return
        self.m_hostname = v
        self.hostnameChanged.emit(v)

    hostname = QtCore.Property(
        str, fget=get_hostname, fset=set_hostname, notify=hostnameChanged,
    )

    def get_keepAlive(self) -> int:
        return self.m_keepAlive

    def set_keepAlive(self, v: int) -> None:
        if self.m_keepAlive == v:
            return
        self.m_keepAlive = v
        self.keepAliveChanged.emit(v)

    keepAlive = QtCore.Property(
        int, fget=get_keepAlive, fset=set_keepAlive, notify=keepAliveChanged,
    )

    @QtCore.Property(str, notify=passwordChanged)
    def password(self) -> str:
        return self.m_password

    @password.setter
    def password(self, v: str) -> None:
        if self.m_password == v:
            return
        self.m_password = v
        self.passwordChanged.emit(v)

    def get_port(self) -> int:
        return self.m_port

    def set_port(self, v: int) -> None:
        if self.m_port == v:
            return
        self.m_port = v
        self.portChanged.emit(v)

    port = QtCore.Property(int, fget=get_port, fset=set_port, notify=portChanged)

    @QtCore.Property(int, notify=protocolVersionChanged)
    def protocolVersion(self) -> int:
        return self.m_protocolVersion

    @protocolVersion.setter
    def protocolVersion(self, v: int) -> None:
        if self.m_protocolVersion == v:
            return
        self.m_protocolVersion = v
        self.protocolVersionChanged.emit(v)

    def get_state(self) -> int:
        return self.m_state

    def set_state(self, v: int) -> None:
        if self.m_state == v:
            return
        self.m_state = v
        self.stateChanged.emit(v)
        if v == ClientState.Connected:
            self.connected.emit()
        elif v == ClientState.Disconnected:
            self.disconnected.emit()

    state = QtCore.Property(int, fget=get_state, fset=set_state, notify=stateChanged)

    @QtCore.Property(str, notify=usernameChanged)
    def username(self) -> str:
        return self.m_username

    @username.setter
    def username(self, v: str) -> None:
        if self.m_username == v:
            return
        self.m_username = v
        self.usernameChanged.emit(v)

    @QtCore.Slot()
    def connectToHost(self) -> None:
        if self.state == ClientState.Connected:
            return

        self.m_error = ClientError.NoError
        self.m_connection.ensureTransportOpen()

    @QtCore.Slot()
    def disconnectFromHost(self) -> None:
        if self.state == ClientState.Disconnected:
            return
        self.m_connection.sendControlDisconnect()

    def publish(
        self,
        topic: MqttTopicName,
        message: bytes = b"",
        qos: int = 0,
        retain: bool = False,
    ) -> int:
        if isinstance(topic, str):
            topic = MqttTopicName(topic)
        if not isinstance(topic, MqttTopicName):
            return -1
        if qos < 0 or qos > 2:
            return -1
        if self.state != ClientState.Connected:
            return -1
        return self.m_connection.sendControlPublish(topic, message, qos, retain)

    def subscribe(self, topic: MqttTopicFilter, qos: int = 0) -> MqttSubscription:
        if self.state != ClientState.Connected:
            return None
        return self.m_connection.sendControlSubscribe(topic, qos)

    def unsubscribe(self, topic: MqttTopicFilter) -> None:
        self.m_connection.sendControlUnsubscribe(topic)


class MqttConnection(QtCore.QObject):
    def __init__(self, parent: typing.Optional[QtCore.QObject] = None) -> None:
        super(MqttConnection, self).__init__(parent)
        self.m_client = None
        self.mqtt_client = mqtt.Client()

        self.m_activeSubscriptions = {}
        self.m_pendingSubscriptionAck = {}
        self.m_pendingUnsubscriptions = {}

    def connect_callbacks(self) -> None:
        self.mqtt_client.on_connect = self.on_connect
        self.mqtt_client.on_disconnect = self.on_disconnect
        self.mqtt_client.on_message = self.on_message
        self.mqtt_client.on_publish = self.on_publish
        self.mqtt_client.on_subscribe = self.on_subscribe
        self.mqtt_client.on_unsubscribe = self.on_unsubscribe

    def setClient(self, client: MqttClient) -> None:
        self.m_client = client

    def ensureTransportOpen(self) -> None:
        self.mqtt_client.reinitialise(
            client_id=self.m_client.clientId, clean_session=self.m_client.cleanSession,
        )
        self.connect_callbacks()
        res = self.mqtt_client.connect(
            self.m_client.hostname,
            port=self.m_client.port,
            keepalive=self.m_client.keepAlive,
        )
        if res == mqtt.MQTT_ERR_SUCCESS:
            self.m_client.state = ClientState.Connecting
        else:
            self.m_client.state = ClientState.Disconnected
        self.mqtt_client.loop_start()

    def sendControlDisconnect(self) -> None:
        res = self.mqtt_client.disconnect()
        if res == mqtt.MQTT_ERR_NO_CONN:
            print("broker, problem")
        elif res == mqtt.MQTT_ERR_SUCCESS:
            print("disconnecting")
        else:
            print(res)

    def sendControlPublish(
        self, topic: MqttTopicFilter, message: mqtt.MQTTMessage, qos: int, retain: bool,
    ) -> None:
        info = self.mqtt_client.publish(topic.name, message, qos, retain)
        return info.mid

    def sendControlSubscribe(
        self, topic: MqttTopicFilter, qos: int = 0,
    ) -> typing.Optional[MqttSubscription]:
        if topic in self.m_activeSubscriptions:
            return self.m_activeSubscriptions[topic]

        result, mid = self.mqtt_client.subscribe(topic.filter, qos)

        if result == mqtt.MQTT_ERR_SUCCESS:
            subscription = MqttSubscription(self)
            subscription.m_topic = topic
            subscription.m_client = self.m_client
            subscription.m_qos = qos
            subscription.setState(SubscriptionState.SubscriptionPending)
            self.m_activeSubscriptions[subscription.topic] = subscription
            self.m_pendingSubscriptionAck[mid] = subscription
            return subscription
        return None

    def sendControlUnsubscribe(self, topic: MqttTopicFilter) -> bool:
        if topic not in self.m_activeSubscriptions:
            return False
        else:
            sub = self.m_activeSubscriptions[topic]
            result, mid = self.mqtt_client.unsubscribe(topic.filter)
            if result == mqtt.MQTT_ERR_SUCCESS:
                self.m_pendingUnsubscriptions[mid] = sub
                sub.setState(SubscriptionState.UnsubscriptionPending)
                return True
            return False

    # Callbacks:

    def on_connect(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        flags: typing.Dict[str, int],
        rc: int,
    ) -> None:
        if rc == ClientError.NoError:
            self.m_client.state = ClientState.Connected
        else:
            self.m_client.state = ClientState.Disconnected
        self.m_client.error = rc

    def on_disconnect(self, client: mqtt.Client, userdata: typing.Any, rc: int) -> None:
        if rc != mqtt.MQTT_ERR_SUCCESS:
            self.m_client.error = ClientError.UnknownError
        else:
            self.m_client.error = ClientError.NoError
        self.m_client.state = ClientState.Disconnected

    def on_message(
        self, client: mqtt.Client, userdata: typing.Any, message: mqtt.MQTTMessage,
    ) -> None:
        topic = MqttTopicName(message.topic)
        print("message", message, message.payload)
        self.m_client.messageReceived.emit(message.payload, topic)
        msg = MqttMessage()
        msg._payload = message.payload
        for key, sub in self.m_activeSubscriptions.items():
            if key.match(topic):
                sub.messageReceived.emit(msg)

    def on_publish(self, client: mqtt.Client, userdata: typing.Any, mid: int) -> None:
        self.m_client.messageSent.emit(mid)

    def on_subscribe(
        self,
        client: mqtt.Client,
        userdata: typing.Any,
        mid: int,
        granted_qos: typing.List[int],
    ) -> None:
        if mid in self.m_pendingSubscriptionAck:
            subscription = self.m_pendingSubscriptionAck[mid]
            del self.m_pendingSubscriptionAck[mid]
            subscription.setState(MqttSubscription.Subscribed)

    def on_unsubscribe(
        self, client: mqtt.Client, userdata: typing.Any, mid: int,
    ) -> None:
        if mid in self.m_pendingUnsubscriptions:
            sub = self.m_pendingUnsubscriptions[mid]
            del self.m_pendingUnsubscriptions[mid]
            sub.setState(SubscriptionState.Unsubscribed)
