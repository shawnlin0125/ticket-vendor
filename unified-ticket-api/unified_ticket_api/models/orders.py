"""訂單管理 — POST /api/v1/{vendor}/orders, GET .../{id}"""

from __future__ import annotations

from dataclasses import dataclass, field

from .common import Customer, Ticket, OrderStatus


@dataclass
class CreateOrderRequest:
    """業務系統 → 代理系統：建立訂單（下單）。

    所有欄位必要。
    """
    event_id: str
    seat_category: str
    quantity: int
    customer: Customer
    idempotency_key: str               # 避免重複下單


@dataclass
class OrderResponse:
    """代理系統 → 業務系統：訂單狀態。

    這是業務系統預期的回應格式。
    create_order / get_order / poll_order 都回傳此格式。
    """
    order_id: str                      # 統一 ID，由代理系統產生
    vendor_order_id: str               # 供應商原始 order ID
    status: OrderStatus
    # 以下欄位在下單時可能為 None，查單 / 輪詢時填充
    event_name: str | None = None
    seat_category: str | None = None
    quantity: int | None = None
    total_amount: int | None = None
    currency: str = "TWD"
    created_at: str | None = None      # ISO 8601
    confirmed_at: str | None = None
    expires_at: str | None = None      # 逾時時間
    tickets: list[Ticket] = field(default_factory=list)
