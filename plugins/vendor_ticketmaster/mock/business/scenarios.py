"""Business scenarios — predefined workflows for integration testing.

Each scenario is a sequence of business system actions that represent
a real-world workflow. Tests iterate through these scenarios and verify
the proxy handles each step correctly.
"""

from __future__ import annotations

from typing import Any

# ── Scenario type ──────────────────────────────────────────────

# Each step is a tuple: (action_name, kwargs_dict)
# Actions map to BusinessMockClient methods
Scenario = list[tuple[str, dict[str, Any]]]


# ── Scenarios ──────────────────────────────────────────────────

HAPPY_PATH: Scenario = [
    # Step 1: 業務系統查詢 Coldplay 活動
    ("search", {"keyword": "Coldplay"}),
    # Step 2: 業務系統對該活動下單
    (
        "create_order",
        {
            "event_id": "evt_001",
            "seat_category": "seat_a",
            "quantity": 2,
            "customer": {
                "name": "王小明",
                "email": "wang@example.com",
                "phone": "+886912345678",
            },
            "idempotency_key": "scenario_happy_001",
        },
    ),
    # Step 3: 業務系統查詢訂單狀態
    ("get_order", {"order_id": "{order_id}"}),  # {order_id} filled by test runner
    # Step 4: 業務系統輪詢訂單
    ("poll_order", {"order_id": "{order_id}"}),
    # Step 5: 業務系統查詢庫存
    ("check_inventory", {"event_id": "evt_001"}),
]


VENDOR_TIMEOUT: Scenario = [
    # Step 1: 正常查詢
    ("search", {"keyword": "Coldplay"}),
    # Step 2: 下單 → 外部供應商逾時 → proxy 應回傳 retryable error
    (
        "create_order",
        {
            "event_id": "evt_timeout",
            "seat_category": "seat_a",
            "quantity": 1,
            "customer": {"name": "測試", "email": "test@example.com", "phone": "+886900000000"},
            "idempotency_key": "scenario_timeout_001",
        },
    ),
    # Step 3: 查單 → 外部供應商逾時
    ("get_order", {"order_id": "ord_timeout_001"}),
]


EMPTY_RESULTS: Scenario = [
    # 查詢無結果關鍵字
    ("search", {"keyword": "NONEXISTENT_EVENT_999"}),
]


INVALID_REQUEST: Scenario = [
    # 缺少必要欄位
    (
        "create_order",
        {
            "event_id": "evt_001",
            # Missing: seat_category, quantity, customer
        },
    ),
]


# ── All scenarios registry ────────────────────────────────────

SCENARIOS: dict[str, Scenario] = {
    "happy_path": HAPPY_PATH,
    "vendor_timeout": VENDOR_TIMEOUT,
    "empty_results": EMPTY_RESULTS,
    "invalid_request": INVALID_REQUEST,
}


def get_scenario(name: str) -> Scenario:
    """Get a scenario by name. Raises KeyError if not found."""
    if name not in SCENARIOS:
        raise KeyError(f"Scenario '{name}' not found. Available: {list(SCENARIOS.keys())}")
    return SCENARIOS[name]
