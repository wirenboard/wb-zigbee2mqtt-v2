import sys
from unittest.mock import MagicMock

# wb_common is only available on Wiren Board hardware — stub it for local tests
sys.modules["wb_common"] = MagicMock()
sys.modules["wb_common.mqtt_client"] = MagicMock()
