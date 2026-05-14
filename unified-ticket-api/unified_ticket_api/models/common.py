"""共通型別 — 所有端點共用的資料結構。

由業務系統定義，代理系統必須回傳符合這些型別的資料。
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Generic, Optional, TypeVar

T = TypeVar("T")


# ── Customer ──────────────────────────────────────────────────


@dataclass
class Customer:
    """下單客戶資訊。"""
    name: str
    email: str
    phone: str


# ── Ticket ────────────────────────────────────────────────────


@dataclass
class Ticket:
    """票券資訊。"""
    ticket_no: str
    barcode: str


# ── Seat & Price ──────────────────────────────────────────────


@dataclass
class SeatCategory:
    """座位區資訊。"""
    id: str
    name: str
    price: int


@dataclass
class PriceRange:
    """價格區間。"""
    min: int
    max: int
    currency: str = "TWD"


# ── Pagination ────────────────────────────────────────────────


@dataclass
class Pagination:
    """分頁資訊，所有 list 端點共用。"""
    total: int
    page: int
    page_size: int


# ── Error ─────────────────────────────────────────────────────


class ErrorCode(Enum):
    """統一錯誤碼 — 所有 vendor 回傳相同錯誤碼。"""
    VENDOR_TIMEOUT = "VENDOR_TIMEOUT"
    VENDOR_ERROR = "VENDOR_ERROR"
    VENDOR_UNAVAILABLE = "VENDOR_UNAVAILABLE"
    INVALID_REQUEST = "INVALID_REQUEST"
    ORDER_NOT_FOUND = "ORDER_NOT_FOUND"
    INSUFFICIENT_INVENTORY = "INSUFFICIENT_INVENTORY"
    DUPLICATE_ORDER = "DUPLICATE_ORDER"
    RATE_LIMITED = "RATE_LIMITED"
    VENDOR_NOT_FOUND = "VENDOR_NOT_FOUND"


@dataclass
class ErrorDetail:
    """錯誤詳情。"""
    code: ErrorCode
    message: str
    vendor_code: str | None = None
    retryable: bool = False


@dataclass
class ErrorResponse:
    """錯誤回應 wrapper。"""
    error: ErrorDetail


# ── API Response ──────────────────────────────────────────────


@dataclass
class ApiResponse(Generic[T]):
    """統一成功回應 wrapper — 所有端點共用。

    業務系統預期的回應格式：
    {
        "data": { ... },
        "meta": {
            "vendor": "ticketmaster",
            "request_id": "req_abc123",
            "timestamp": "2026-05-14T08:00:00Z"
        }
    }
    """
    data: T

    @property
    def meta(self) -> dict:
        # 由代理系統自動填充，不在 model 內定義
        return {}


# ── Order Status ──────────────────────────────────────────────


class OrderStatus(str, Enum):
    """訂單狀態 — 所有 vendor 統一定義。"""
    PENDING = "pending"          # 已提交，等待供應商確認
    CONFIRMED = "confirmed"      # 供應商已確認
    FAILED = "failed"            # 下單失敗
    EXPIRED = "expired"          # 逾時未付款
    CANCELLED = "cancelled"      # 已取消
