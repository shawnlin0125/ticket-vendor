"""型別定義 — 業務系統合約的全部資料結構。"""

from .common import (
    Customer,
    Ticket,
    SeatCategory,
    PriceRange,
    Pagination,
    ErrorCode,
    ErrorDetail,
    ErrorResponse,
    ApiResponse,
    OrderStatus,
)
from .search import SearchRequest, SearchResponse, EventItem
from .orders import CreateOrderRequest, OrderResponse
from .inventory import InventoryRequest, InventoryResponse, InventorySeatCategory

__all__ = [
    # Common
    "Customer",
    "Ticket",
    "SeatCategory",
    "PriceRange",
    "Pagination",
    "ErrorCode",
    "ErrorDetail",
    "ErrorResponse",
    "ApiResponse",
    "OrderStatus",
    # Search
    "SearchRequest",
    "SearchResponse",
    "EventItem",
    # Orders
    "CreateOrderRequest",
    "OrderResponse",
    # Inventory
    "InventoryRequest",
    "InventoryResponse",
    "InventorySeatCategory",
]
