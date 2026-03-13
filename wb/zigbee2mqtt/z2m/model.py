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
