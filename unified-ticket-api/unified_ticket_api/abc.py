"""VendorProxy ABC — 業務系統對代理系統的合約。

由業務系統定義，所有 ticket-vendor plugin 必須實作。

使用方式：

    from unified_ticket_api import VendorProxy
    from platform_plugin_sdk import Plugin

    class TicketmasterPlugin(Plugin, VendorProxy):
        async def search(self, req: SearchRequest) -> SearchResponse:
            ...

設計原則：
  - 消費方（業務系統）定義合約 → Consumer-Driven Contract
  - @abstractmethod 強制所有 vendor 實作相同方法
  - 型別標注讓 IDE 自動補全 + mypy 靜態檢查
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from .models import (
    SearchRequest,
    SearchResponse,
    CreateOrderRequest,
    OrderResponse,
    InventoryRequest,
    InventoryResponse,
)


class VendorProxy(ABC):
    """票券供應商代理合約。

    每個 vendor plugin 必須繼承此類別並實作所有抽象方法。

    plugin-hub 管理 lifecycle（start/stop/health），
    此 ABC 管理 business API（search/orders/inventory）。
    """

    # ── 查詢 ──────────────────────────────────────────────────

    @abstractmethod
    async def search(self, request: SearchRequest) -> SearchResponse:
        """查詢活動 / 商品結構。

        GET /api/v1/{vendor}/search

        Args:
            request: 查詢參數，包含 keyword / category / date range / pagination

        Returns:
            SearchResponse: 統一格式的活動列表

        Note:
            代理系統負責將外部供應商 API 格式轉換為 SearchResponse。
        """
        ...

    # ── 下單 ──────────────────────────────────────────────────

    @abstractmethod
    async def create_order(self, request: CreateOrderRequest) -> OrderResponse:
        """建立訂單（下單）。

        POST /api/v1/{vendor}/orders

        Args:
            request: 訂單內容，包含 event_id / seat_category / quantity / customer

        Returns:
            OrderResponse: status = PENDING 或 FAILED

        Note:
            idempotency_key 用於避免重複下單。
        """
        ...

    # ── 查單 ──────────────────────────────────────────────────

    @abstractmethod
    async def get_order(self, order_id: str) -> OrderResponse:
        """查詢訂單狀態。

        GET /api/v1/{vendor}/orders/{order_id}

        Args:
            order_id: 由代理系統產生的統一訂單 ID

        Returns:
            OrderResponse: 包含當前狀態、票券資訊（若有）
        """
        ...

    # ── 輪詢 ──────────────────────────────────────────────────

    @abstractmethod
    async def poll_order(self, order_id: str) -> OrderResponse:
        """輪詢訂單最新狀態。

        GET /api/v1/{vendor}/orders/{order_id}/poll

        與 get_order 相同，但設計意圖是用於 short polling。
        業務系統應定時呼叫此方法，而非使用 webhook。

        Args:
            order_id: 訂單 ID

        Returns:
            OrderResponse: 當前最新狀態
        """
        ...

    # ── 庫存 ──────────────────────────────────────────────────

    @abstractmethod
    async def check_inventory(self, request: InventoryRequest) -> InventoryResponse:
        """查詢庫存。

        GET /api/v1/{vendor}/inventory

        Args:
            request: 包含 event_id

        Returns:
            InventoryResponse: 各座位區的可用 / 總量
        """
        ...
