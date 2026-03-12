# pylint: disable=redefined-outer-name,too-few-public-methods
from unittest.mock import MagicMock

import pytest

from wb.zigbee2mqtt.config_loader import BRIDGE_DEVICE_ID_DEFAULT as DEVICE_ID
from wb.zigbee2mqtt.config_loader import BRIDGE_DEVICE_NAME_DEFAULT as DEVICE_NAME
from wb.zigbee2mqtt.wb_converter.controls import BRIDGE_CONTROLS
from wb.zigbee2mqtt.wb_converter.publisher import DEVICES_PREFIX, WbPublisher


class MockMessage:
    def __init__(self, payload: str) -> None:
        self.payload = payload.encode("utf-8")


@pytest.fixture()
def mqtt_client() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def publisher(mqtt_client: MagicMock) -> WbPublisher:
    return WbPublisher(mqtt_client, DEVICE_ID, DEVICE_NAME)


class TestPublishBridgeDevice:
    def test_publishes_device_name(self, publisher: WbPublisher, mqtt_client: MagicMock) -> None:
        publisher.publish_bridge_device()

        mqtt_client.publish.assert_any_call(
            f"{DEVICES_PREFIX}/{DEVICE_ID}/meta/name",
            DEVICE_NAME,
            retain=True,
            qos=1,
        )

    def test_publishes_all_control_types(self, publisher: WbPublisher, mqtt_client: MagicMock) -> None:
        publisher.publish_bridge_device()

        for control_id, meta in BRIDGE_CONTROLS.items():
            mqtt_client.publish.assert_any_call(
                f"{DEVICES_PREFIX}/{DEVICE_ID}/controls/{control_id}/meta/type",
                meta.type,
                retain=True,
                qos=1,
            )

    def test_publishes_readonly_flag(self, publisher: WbPublisher, mqtt_client: MagicMock) -> None:
        publisher.publish_bridge_device()

        for control_id, meta in BRIDGE_CONTROLS.items():
            expected_value = "1" if meta.readonly else "0"
            mqtt_client.publish.assert_any_call(
                f"{DEVICES_PREFIX}/{DEVICE_ID}/controls/{control_id}/meta/readonly",
                expected_value,
                retain=True,
                qos=1,
            )


class TestPublishBridgeControl:
    def test_publishes_value_with_retain(self, publisher: WbPublisher, mqtt_client: MagicMock) -> None:
        publisher.publish_bridge_control("state", "online")

        mqtt_client.publish.assert_called_once_with(
            f"{DEVICES_PREFIX}/{DEVICE_ID}/controls/state",
            "online",
            retain=True,
            qos=1,
        )


class TestSubscribeBridgeCommands:
    def test_subscribes_to_command_topics(self, publisher: WbPublisher, mqtt_client: MagicMock) -> None:
        publisher.subscribe_bridge_commands(MagicMock(), MagicMock())

        mqtt_client.subscribe.assert_any_call(f"{DEVICES_PREFIX}/{DEVICE_ID}/controls/permit_join/on")
        mqtt_client.subscribe.assert_any_call(f"{DEVICES_PREFIX}/{DEVICE_ID}/controls/update_devices/on")

    def test_permit_join_on_callback(self, publisher: WbPublisher, mqtt_client: MagicMock) -> None:
        on_permit_join = MagicMock()
        publisher.subscribe_bridge_commands(on_permit_join, MagicMock())

        permit_join_topic = f"{DEVICES_PREFIX}/{DEVICE_ID}/controls/permit_join/on"
        callbacks = {c.args[0]: c.args[1] for c in mqtt_client.message_callback_add.call_args_list}
        callback = callbacks[permit_join_topic]

        callback(None, None, MockMessage("1"))
        on_permit_join.assert_called_once_with(True)

        on_permit_join.reset_mock()
        callback(None, None, MockMessage("0"))
        on_permit_join.assert_called_once_with(False)

    def test_update_devices_callback(self, publisher: WbPublisher, mqtt_client: MagicMock) -> None:
        on_update_devices = MagicMock()
        publisher.subscribe_bridge_commands(MagicMock(), on_update_devices)

        update_topic = f"{DEVICES_PREFIX}/{DEVICE_ID}/controls/update_devices/on"
        callbacks = {c.args[0]: c.args[1] for c in mqtt_client.message_callback_add.call_args_list}
        callback = callbacks[update_topic]

        callback(None, None, MockMessage("1"))
        on_update_devices.assert_called_once()
