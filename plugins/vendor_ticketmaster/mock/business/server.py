"""Mock Business System — simulates the upstream business system's calls.

This mock plays the role of the 業務系統（主系統）making requests to
the proxy's unified API (/api/v1/search, /orders, ...).

In tests, this is used to verify that the proxy correctly:
  - Accepts the unified API format
  - Translates correctly to vendor-specific API calls
  - Returns responses in the correct unified format
"""

import json
from pathlib import Path

import aiohttp

FIXTURES = Path(__file__).parent.parent.parent / "fixtures"


class BusinessMockClient:
    """Simulates the business system calling the proxy's unified API."""

    def __init__(self, proxy_base_url: str):
        self.base = proxy_base_url.rstrip("/")

    # ── Search ─────────────────────────────────────────────────

    async def search(self, keyword: str = "", page: int = 1, page_size: int = 20) -> dict:
        """Simulate: 業務系統查詢商品結構"""
        params = {"page": page, "page_size": page_size}
        if keyword:
            params["keyword"] = keyword

        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base}/api/v1/search",
                params=params,
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()
                return {
                    "status": resp.status,
                    "data": data,
                }

    # ── Orders ─────────────────────────────────────────────────

    async def create_order(
        self,
        event_id: str,
        seat_category: str,
        quantity: int,
        customer: dict,
        idempotency_key: str,
    ) -> dict:
        """Simulate: 業務系統下單"""
        payload = {
            "event_id": event_id,
            "seat_category": seat_category,
            "quantity": quantity,
            "customer": customer,
            "idempotency_key": idempotency_key,
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base}/api/v1/orders",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as resp:
                data = await resp.json()
                return {
                    "status": resp.status,
                    "data": data,
                }

    async def get_order(self, order_id: str) -> dict:
        """Simulate: 業務系統查單"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base}/api/v1/orders/{order_id}",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()
                return {
                    "status": resp.status,
                    "data": data,
                }

    async def poll_order(self, order_id: str) -> dict:
        """Simulate: 業務系統輪詢訂單狀態"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base}/api/v1/orders/{order_id}/poll",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()
                return {
                    "status": resp.status,
                    "data": data,
                }

    # ── Inventory ──────────────────────────────────────────────

    async def check_inventory(self, event_id: str) -> dict:
        """Simulate: 業務系統查庫存"""
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{self.base}/api/v1/inventory",
                params={"event_id": event_id},
                timeout=aiohttp.ClientTimeout(total=10),
            ) as resp:
                data = await resp.json()
                return {
                    "status": resp.status,
                    "data": data,
                }
