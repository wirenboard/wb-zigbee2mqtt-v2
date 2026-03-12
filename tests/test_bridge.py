# pylint: disable=redefined-outer-name,protected-access,too-few-public-methods
from unittest.mock import MagicMock, patch

import pytest

from wb.zigbee2mqtt.bridge import Bridge
from wb.zigbee2mqtt.z2m.model import BridgeInfo


@pytest.fixture()
def mqtt_client() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def mock_z2m() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def mock_wb() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def bridge(mqtt_client: MagicMock, mock_z2m: MagicMock, mock_wb: MagicMock) -> Bridge:
    with (
        patch("wb.zigbee2mqtt.bridge.Z2MClient", return_value=mock_z2m),
        patch("wb.zigbee2mqtt.bridge.WbPublisher", return_value=mock_wb),
    ):
        return Bridge(mqtt_client, "zigbee2mqtt", "zigbee2mqtt", "Zigbee2MQTT")


class TestSubscribe:
    def test_publishes_bridge_device(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge.subscribe()

        mock_wb.publish_bridge_device.assert_called_once()

    def test_subscribes_z2m(self, bridge: Bridge, mock_z2m: MagicMock) -> None:
        bridge.subscribe()

        mock_z2m.subscribe.assert_called_once()

    def test_subscribes_wb_commands(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge.subscribe()

        mock_wb.subscribe_bridge_commands.assert_called_once()

    def test_passes_permit_join_handler(
        self, bridge: Bridge, mock_z2m: MagicMock, mock_wb: MagicMock
    ) -> None:
        bridge.subscribe()

        kwargs = mock_wb.subscribe_bridge_commands.call_args.kwargs
        assert kwargs["on_permit_join"] == mock_z2m.set_permit_join

    def test_passes_update_devices_handler(
        self, bridge: Bridge, mock_z2m: MagicMock, mock_wb: MagicMock
    ) -> None:
        bridge.subscribe()

        kwargs = mock_wb.subscribe_bridge_commands.call_args.kwargs
        assert kwargs["on_update_devices"] == mock_z2m.request_devices_update


class TestRepublish:
    def test_republishes_bridge_device(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge.republish()

        mock_wb.publish_bridge_device.assert_called_once()


class TestCallbacks:
    def test_on_bridge_state(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge._on_bridge_state("online")

        mock_wb.publish_bridge_control.assert_called_once_with("state", "online")

    def test_on_bridge_info_version(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge._on_bridge_info(
            BridgeInfo(version="1.40.0", permit_join=False, permit_join_end=None, log_level="info")
        )

        mock_wb.publish_bridge_control.assert_any_call("version", "1.40.0")

    def test_on_bridge_info_log_level(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge._on_bridge_info(
            BridgeInfo(version="1.40.0", permit_join=False, permit_join_end=None, log_level="debug")
        )

        mock_wb.publish_bridge_control.assert_any_call("log_level", "debug")

    def test_on_bridge_info_permit_join_true(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge._on_bridge_info(
            BridgeInfo(version="1.40.0", permit_join=True, permit_join_end=None, log_level="info")
        )

        mock_wb.publish_bridge_control.assert_any_call("permit_join", "1")

    def test_on_bridge_info_permit_join_false(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge._on_bridge_info(
            BridgeInfo(version="1.40.0", permit_join=False, permit_join_end=None, log_level="info")
        )

        mock_wb.publish_bridge_control.assert_any_call("permit_join", "0")

    def test_on_bridge_log(self, bridge: Bridge, mock_wb: MagicMock) -> None:
        bridge._on_bridge_log("Interview successful")

        mock_wb.publish_bridge_control.assert_called_once_with("log", "Interview successful")
