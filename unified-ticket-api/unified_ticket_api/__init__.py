"""Unified Ticket Vendor API — 業務系統定義的票券供應商代理合約。

由業務系統 (Grails) 擁有此合約。
所有 ticket-vendor plugin 必須相依此 package 並實作 VendorProxy ABC。

使用方式：

    pip install unified-ticket-api

    from unified_ticket_api import VendorProxy, SearchRequest, SearchResponse

    class MyVendorPlugin(VendorProxy):
        async def search(self, req: SearchRequest) -> SearchResponse:
            ...

Version: 0.1.0
Owner: Business System Team
"""

from .abc import VendorProxy
from .models import (
    # Common
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
    # Search
    SearchRequest,
    SearchResponse,
    EventItem,
    # Orders
    CreateOrderRequest,
    OrderResponse,
    # Inventory
    InventoryRequest,
    InventoryResponse,
    InventorySeatCategory,
)

__all__ = [
    # ABC
    "VendorProxy",
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

__version__ = "0.1.0"
