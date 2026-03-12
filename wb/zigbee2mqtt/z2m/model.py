from dataclasses import dataclass
from typing import Optional


@dataclass
class BridgeInfo:
    version: str
    permit_join: bool
    permit_join_end: Optional[int]
    log_level: str


class BridgeState:  # pylint: disable=too-few-public-methods
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"
