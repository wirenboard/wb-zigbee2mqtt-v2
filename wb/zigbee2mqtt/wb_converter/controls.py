from dataclasses import dataclass
from typing import Optional


@dataclass
class ControlMeta:
    type: str
    readonly: bool
    title: Optional[str] = None
    order: int = 0


BRIDGE_CONTROLS: dict[str, ControlMeta] = {
    "state": ControlMeta(type="text", readonly=True, title="State", order=1),
    "version": ControlMeta(type="text", readonly=True, title="Version", order=2),
    "log_level": ControlMeta(type="text", readonly=True, title="Log level", order=3),
    "log": ControlMeta(type="text", readonly=True, title="Log", order=4),
    "permit_join": ControlMeta(type="switch", readonly=False, title="Permit join", order=5),
    "update_devices": ControlMeta(type="pushbutton", readonly=False, title="Update devices", order=6),
}
