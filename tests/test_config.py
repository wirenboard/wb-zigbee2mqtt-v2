import json

import jsonschema
import pytest

from wb_zigbee2mqtt.config import Config, load_config


def test_load_config_missing_file() -> None:
    with pytest.raises(FileNotFoundError):
        load_config("/nonexistent/path/config.conf")


def test_load_config_invalid_json(tmp_path) -> None:
    config_file = tmp_path / "config.conf"
    config_file.write_text("not a json{{{", encoding="utf-8")

    with pytest.raises(ValueError, match="not valid JSON"):
        load_config(str(config_file), schema_path="/nonexistent/schema.json")


def test_load_config_missing_key(tmp_path) -> None:
    config_file = tmp_path / "config.conf"
    config_file.write_text(
        json.dumps({"broker_url": "unix:///var/run/mosquitto/mosquitto.sock"}),
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Missing required configuration key"):
        load_config(str(config_file), schema_path="/nonexistent/schema.json")


def test_load_config_custom_values(tmp_path) -> None:
    config_file = tmp_path / "config.conf"
    config_file.write_text(
        json.dumps({
            "broker_url": "mqtt-tcp://localhost:1883",
            "zigbee2mqtt_base_topic": "z2m",
        }),
        encoding="utf-8",
    )

    config = load_config(str(config_file), schema_path="/nonexistent/schema.json")

    assert config.broker_url == "mqtt-tcp://localhost:1883"
    assert config.zigbee2mqtt_base_topic == "z2m"


def test_load_config_schema_validation_error(tmp_path) -> None:
    config_file = tmp_path / "config.conf"
    schema_file = tmp_path / "schema.json"

    schema_file.write_text(
        json.dumps({
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "broker_url": {"type": "string"},
                "zigbee2mqtt_base_topic": {"type": "string"},
            },
            "required": ["broker_url", "zigbee2mqtt_base_topic"],
        }),
        encoding="utf-8",
    )
    config_file.write_text(
        json.dumps({"broker_url": 12345, "zigbee2mqtt_base_topic": "zigbee2mqtt"}),
        encoding="utf-8",
    )

    with pytest.raises(jsonschema.ValidationError):
        load_config(str(config_file), schema_path=str(schema_file))


def test_load_config_with_schema_validation(tmp_path) -> None:
    config_file = tmp_path / "config.conf"
    schema_file = tmp_path / "schema.json"

    schema_file.write_text(
        json.dumps({
            "$schema": "http://json-schema.org/draft-04/schema#",
            "type": "object",
            "properties": {
                "broker_url": {"type": "string"},
                "zigbee2mqtt_base_topic": {"type": "string"},
            },
            "required": ["broker_url", "zigbee2mqtt_base_topic"],
        }),
        encoding="utf-8",
    )
    config_file.write_text(
        json.dumps({
            "broker_url": "unix:///var/run/mosquitto/mosquitto.sock",
            "zigbee2mqtt_base_topic": "zigbee2mqtt",
        }),
        encoding="utf-8",
    )

    config = load_config(str(config_file), schema_path=str(schema_file))
    assert isinstance(config, Config)
