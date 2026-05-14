"""搜尋商品 / 活動 — GET /api/v1/{vendor}/search"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional

from .common import SeatCategory, PriceRange


@dataclass
class SearchRequest:
    """業務系統 → 代理系統：查詢活動 / 商品結構。

    所有 query parameter 可選，至少一個不為空。
    """
    keyword: str = ""
    category: Optional[str] = None
    date_from: Optional[str] = None       # ISO 8601
    date_to: Optional[str] = None         # ISO 8601
    page: int = 1
    page_size: int = 20


@dataclass
class EventItem:
    """單一活動 / 商品項目。

    這是業務系統預期的統一格式，無論下游是哪個供應商。
    代理系統負責將外部供應商的原始格式轉換為此結構。
    """
    id: str                                  # 統一 ID，由代理系統產生
    vendor_event_id: str                     # 供應商原始 ID
    name: str                                # 活動名稱
    category: str                            # 分類 (concert, sports, theater...)
    venue: str                               # 場地
    date: str                                # 活動日期 (ISO 8601)
    status: str                              # on_sale / sold_out / cancelled
    price_range: PriceRange
    seat_categories: list[SeatCategory] = field(default_factory=list)


@dataclass
class SearchResponse:
    """代理系統 → 業務系統：搜尋結果。

    這是業務系統預期的回應格式。
    所有 vendor 的回應必須轉換為此格式。
    """
    items: list[EventItem]
    total: int
    page: int
    page_size: int
