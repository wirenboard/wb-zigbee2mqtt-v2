import logging
from typing import Optional

from ..z2m.model import ExposeFeature
from .controls import ControlMeta

logger = logging.getLogger(__name__)

# Mapping of z2m property names to WB control types (for numeric exposes)
NUMERIC_TYPE_MAP: dict[str, str] = {
    "temperature": "temperature",
    "humidity": "rel_humidity",
    "pressure": "atmospheric_pressure",
    "co2": "concentration",
    "noise": "sound_level",
    "power": "power",
    "voltage": "voltage",
}

# Specific/composite expose types that contain nested features
NESTED_TYPES = {"light", "switch", "lock", "climate", "fan", "cover", "composite"}


def map_exposes_to_controls(exposes: list[ExposeFeature]) -> dict[str, ControlMeta]:
    """Convert a list of z2m expose features into a flat dict of WB controls"""
    controls: dict[str, ControlMeta] = {}
    order = 1
    for expose in exposes:
        for prop, meta in _flatten_expose(expose):
            if prop not in controls:
                meta.order = order
                controls[prop] = meta
                order += 1
    controls["last_seen"] = ControlMeta(
        type="text", readonly=True, order=order,
        title={"en": "Last seen", "ru": "Последняя активность"},
    )
    return controls


def _flatten_expose(expose: ExposeFeature) -> list[tuple[str, ControlMeta]]:
    """Recursively flatten an expose feature into (property, ControlMeta) pairs"""
    if expose.type in NESTED_TYPES and expose.features:
        result = []
        for sub in expose.features:
            result.extend(_flatten_expose(sub))
        return result
    return _map_leaf_feature(expose)


def _map_leaf_feature(feature: ExposeFeature) -> list[tuple[str, ControlMeta]]:
    """Map a single leaf expose feature to a (property, ControlMeta) pair"""
    if not feature.property:
        return []

    wb_type = _resolve_wb_type(feature)
    if wb_type is None:
        return []

    meta = ControlMeta(type=wb_type, readonly=True)
    return [(feature.property, meta)]


def _resolve_wb_type(feature: ExposeFeature) -> Optional[str]:
    if feature.type == "numeric":
        return NUMERIC_TYPE_MAP.get(feature.property, "value")
    if feature.type == "binary":
        return "switch"
    if feature.type in ("enum", "text"):
        return "text"
    logger.warning("Unknown expose type '%s' for property '%s'", feature.type, feature.property)
    return None
