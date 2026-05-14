"""庫存查詢 — GET /api/v1/{vendor}/inventory"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class InventoryRequest:
    """業務系統 → 代理系統：查詢庫存。"""
    event_id: str


@dataclass
class InventorySeatCategory:
    """單一座位區庫存資訊。"""
    id: str
    name: str
    available: int
    total: int


@dataclass
class InventoryResponse:
    """代理系統 → 業務系統：庫存資訊。"""
    event_id: str
    updated_at: str                    # ISO 8601
    seat_categories: list[InventorySeatCategory] = field(default_factory=list)
