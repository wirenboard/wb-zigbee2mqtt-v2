from dataclasses import dataclass
from typing import Optional


@dataclass
class BridgeInfo:
    version: str
    permit_join: bool
    permit_join_end: Optional[int]


class BridgeState:
    ONLINE = "online"
    OFFLINE = "offline"
    ERROR = "error"


class BridgeLogLevel:
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"

    RANK = {DEBUG: 0, INFO: 1, WARNING: 2, ERROR: 3}
