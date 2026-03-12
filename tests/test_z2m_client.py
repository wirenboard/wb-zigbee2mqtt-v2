# pylint: disable=redefined-outer-name,protected-access,too-few-public-methods
import json
from unittest.mock import MagicMock

import pytest

from wb.zigbee2mqtt.z2m.client import PERMIT_JOIN_TIME, PERMIT_JOIN_TIME_DISABLED, Z2MClient
from wb.zigbee2mqtt.z2m.model import BridgeInfo, BridgeState


class MockMessage:
    def __init__(self, payload: str) -> None:
        self.payload = payload.encode("utf-8")


@pytest.fixture()
def mqtt_client() -> MagicMock:
    return MagicMock()


@pytest.fixture()
def callbacks() -> dict:
    return {
        "on_bridge_state": MagicMock(),
        "on_bridge_info": MagicMock(),
        "on_bridge_log": MagicMock(),
    }


@pytest.fixture()
def z2m_client(mqtt_client: MagicMock, callbacks: dict) -> Z2MClient:
    return Z2MClient(
        mqtt_client=mqtt_client,
        base_topic="zigbee2mqtt",
        on_bridge_state=callbacks["on_bridge_state"],
        on_bridge_info=callbacks["on_bridge_info"],
        on_bridge_log=callbacks["on_bridge_log"],
    )


class TestSubscribe:
    def test_subscribes_to_bridge_topics(self, z2m_client: Z2MClient, mqtt_client: MagicMock) -> None:
        z2m_client.subscribe()

        mqtt_client.subscribe.assert_any_call("zigbee2mqtt/bridge/state")
        mqtt_client.subscribe.assert_any_call("zigbee2mqtt/bridge/info")
        mqtt_client.subscribe.assert_any_call("zigbee2mqtt/bridge/logging")

    def test_registers_message_callbacks(self, z2m_client: Z2MClient, mqtt_client: MagicMock) -> None:
        z2m_client.subscribe()

        topics = [c.args[0] for c in mqtt_client.message_callback_add.call_args_list]
        assert "zigbee2mqtt/bridge/state" in topics
        assert "zigbee2mqtt/bridge/info" in topics
        assert "zigbee2mqtt/bridge/logging" in topics


class TestHandleBridgeState:
    @pytest.mark.parametrize("state", [BridgeState.ONLINE, BridgeState.OFFLINE, BridgeState.ERROR])
    def test_valid_state_plain_string(self, z2m_client: Z2MClient, callbacks: dict, state: str) -> None:
        z2m_client._handle_bridge_state(None, None, MockMessage(state))

        callbacks["on_bridge_state"].assert_called_once_with(state)

    @pytest.mark.parametrize("state", [BridgeState.ONLINE, BridgeState.OFFLINE, BridgeState.ERROR])
    def test_valid_state_json_format(self, z2m_client: Z2MClient, callbacks: dict, state: str) -> None:
        z2m_client._handle_bridge_state(None, None, MockMessage(json.dumps({"state": state})))

        callbacks["on_bridge_state"].assert_called_once_with(state)

    def test_unknown_state_ignored(self, z2m_client: Z2MClient, callbacks: dict) -> None:
        z2m_client._handle_bridge_state(None, None, MockMessage("unknown"))

        callbacks["on_bridge_state"].assert_not_called()


class TestHandleBridgeInfo:
    def test_parses_full_payload(self, z2m_client: Z2MClient, callbacks: dict) -> None:
        payload = json.dumps(
            {
                "version": "1.40.0",
                "permit_join": True,
                "permit_join_end": 1733666394,
                "log_level": "info",
            }
        )

        z2m_client._handle_bridge_info(None, None, MockMessage(payload))

        callbacks["on_bridge_info"].assert_called_once_with(
            BridgeInfo(version="1.40.0", permit_join=True, permit_join_end=1733666394, log_level="info")
        )

    def test_permit_join_false(self, z2m_client: Z2MClient, callbacks: dict) -> None:
        payload = json.dumps({"version": "2.0.0", "permit_join": False})

        z2m_client._handle_bridge_info(None, None, MockMessage(payload))

        info: BridgeInfo = callbacks["on_bridge_info"].call_args[0][0]
        assert info.permit_join is False
        assert info.permit_join_end is None
        assert info.log_level == ""

    def test_invalid_json_ignored(self, z2m_client: Z2MClient, callbacks: dict) -> None:
        z2m_client._handle_bridge_info(None, None, MockMessage("not json{{{"))

        callbacks["on_bridge_info"].assert_not_called()


class TestHandleBridgeLog:
    def test_parses_json_message(self, z2m_client: Z2MClient, callbacks: dict) -> None:
        payload = json.dumps({"level": "info", "message": "Interview successful"})

        z2m_client._handle_bridge_log(None, None, MockMessage(payload))

        callbacks["on_bridge_log"].assert_called_once_with("Interview successful")

    def test_plain_text_fallback(self, z2m_client: Z2MClient, callbacks: dict) -> None:
        z2m_client._handle_bridge_log(None, None, MockMessage("plain text log"))

        callbacks["on_bridge_log"].assert_called_once_with("plain text log")

    def test_missing_message_field(self, z2m_client: Z2MClient, callbacks: dict) -> None:
        payload = json.dumps({"level": "info"})

        z2m_client._handle_bridge_log(None, None, MockMessage(payload))

        callbacks["on_bridge_log"].assert_called_once_with("")


class TestCommands:
    def test_set_permit_join_enabled(self, z2m_client: Z2MClient, mqtt_client: MagicMock) -> None:
        z2m_client.set_permit_join(True)

        mqtt_client.publish.assert_called_once_with(
            "zigbee2mqtt/bridge/request/permit_join",
            json.dumps({"time": PERMIT_JOIN_TIME}),
        )

    def test_set_permit_join_disabled(self, z2m_client: Z2MClient, mqtt_client: MagicMock) -> None:
        z2m_client.set_permit_join(False)

        mqtt_client.publish.assert_called_once_with(
            "zigbee2mqtt/bridge/request/permit_join",
            json.dumps({"time": PERMIT_JOIN_TIME_DISABLED}),
        )

    def test_request_devices_update(self, z2m_client: Z2MClient, mqtt_client: MagicMock) -> None:
        z2m_client.request_devices_update()

        mqtt_client.publish.assert_called_once_with(
            "zigbee2mqtt/bridge/request/devices/get",
            "{}",
        )
