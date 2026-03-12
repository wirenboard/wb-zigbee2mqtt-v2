import json
import logging
import os
from dataclasses import dataclass

import jsonschema

CONFIG_FILEPATH = "/mnt/data/etc/wb-zigbee2mqtt.conf"
SCHEMA_FILEPATH = "/usr/share/wb-mqtt-confed/schemas/wb-zigbee2mqtt.schema.json"

logger = logging.getLogger(__name__)


@dataclass
class Config:
    broker_url: str
    zigbee2mqtt_base_topic: str


def load_config(config_path: str, schema_path: str = SCHEMA_FILEPATH) -> Config:
    if not os.path.isfile(config_path):
        raise FileNotFoundError(f"Configuration file not found: {config_path}")

    with open(config_path, "r", encoding="utf-8") as config_file:
        try:
            config = json.load(config_file)
        except json.JSONDecodeError as e:
            raise ValueError(f"Configuration file is not valid JSON: {e}") from e

    if not os.path.isfile(schema_path):
        logger.warning("Schema file not found, skipping validation: %s", schema_path)
    else:
        with open(schema_path, "r", encoding="utf-8") as schema_file:
            schema = json.load(schema_file)
        jsonschema.validate(
            instance=config,
            schema=schema,
            format_checker=jsonschema.draft4_format_checker,
        )

    try:
        return Config(
            broker_url=config["broker_url"],
            zigbee2mqtt_base_topic=config["zigbee2mqtt_base_topic"],
        )
    except KeyError as e:
        raise ValueError(f"Missing required configuration key: {e}") from e
