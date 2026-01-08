# HKTVmall 連接器模組
from app.connectors.hktv.interface import HKTVConnectorInterface
from app.connectors.hktv.mock import MockHKTVConnector

__all__ = ["HKTVConnectorInterface", "MockHKTVConnector"]
