"""Ticket Proxy — FastAPI service that serves the unified ticket API.

This service:
  1. Reads LOAD_PLUGINS env to know which vendors to load
  2. Loads vendor plugins dynamically
  3. Serves /api/v1/{vendor}/search, /orders, /inventory
  4. Constructs SDK models and calls vendor plugin methods

Architecture:
  Hub Admin (Go)  ──reverse proxy──→  ticket-proxy (Python) :8000
  hub.shawnlin.online/api/v1/{vendor}/*  →  ticket-proxy:8000
"""

from __future__ import annotations

import importlib
import os
import sys
from pathlib import Path
from typing import Optional

import uvicorn
from fastapi import FastAPI, HTTPException, Query

# Add project root so plugins/ can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from unified_ticket_api import (
    SearchRequest,
    CreateOrderRequest,
    InventoryRequest,
    Customer,
)

# ── App ───────────────────────────────────────────────────────

app = FastAPI(
    title="Ticket Vendor Proxy",
    description="Unified API proxy — TicketMaster, KKTIX, ibon, ...",
    version="0.1.0",
)

loaded_plugins: dict[str, object] = {}


# ═══════════════════════════════════════════════════════════════
# Plugin Loading
# ═══════════════════════════════════════════════════════════════

def load_plugins() -> None:
    """Load vendor plugins specified by LOAD_PLUGINS env var."""
    plugins_str = os.environ.get("LOAD_PLUGINS", "").strip()
    if not plugins_str:
        print("⚠️  LOAD_PLUGINS is empty — no vendors loaded")
        return

    plugin_ids = [p.strip() for p in plugins_str.split(",") if p.strip()]
    if not plugin_ids:
        return

    for pid in plugin_ids:
        try:
            mod = importlib.import_module(f"vendor_{pid}.plugin")
            plugin_instance = None
            for name in dir(mod):
                obj = getattr(mod, name)
                if isinstance(obj, type) and hasattr(obj, "plugin_id"):
                    if getattr(obj, "plugin_id", None) == pid:
                        plugin_instance = obj()
                        break
            if plugin_instance is None:
                print(f"⚠️  Could not find plugin class for {pid}")
                continue

            loaded_plugins[pid] = plugin_instance
            print(f"✅ Loaded: {pid} ({plugin_instance.plugin_name} v{plugin_instance.version})")
        except Exception as e:
            print(f"❌ Failed to load {pid}: {e}")

    print(f"📦 Total loaded: {len(loaded_plugins)} vendor(s)")


def get_plugin(vendor: str):
    """Get a loaded plugin by vendor ID."""
    plugin = loaded_plugins.get(vendor)
    if plugin is None:
        raise HTTPException(status_code=404, detail=f"Vendor '{vendor}' not found or enabled")
    return plugin


# ═══════════════════════════════════════════════════════════════
# Business API Endpoints
# ═══════════════════════════════════════════════════════════════

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "vendors": list(loaded_plugins.keys()),
        "count": len(loaded_plugins),
    }


@app.get("/api/v1/{vendor}/search")
async def search(
    vendor: str,
    keyword: str = "",
    category: Optional[str] = None,
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
    page: int = 1,
    page_size: int = Query(20, le=100),
):
    """GET /api/v1/{vendor}/search"""
    plugin = get_plugin(vendor)
    try:
        req = SearchRequest(
            keyword=keyword,
            category=category,
            date_from=date_from,
            date_to=date_to,
            page=page,
            page_size=page_size,
        )
        result = await plugin.search(req)
        return {"data": _dataclass_to_dict(result)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.post("/api/v1/{vendor}/orders")
async def create_order(vendor: str, body: dict):
    """POST /api/v1/{vendor}/orders"""
    plugin = get_plugin(vendor)
    try:
        customer_dict = body.get("customer", {})
        req = CreateOrderRequest(
            event_id=body["event_id"],
            seat_category=body["seat_category"],
            quantity=body["quantity"],
            customer=Customer(
                name=customer_dict.get("name", ""),
                email=customer_dict.get("email", ""),
                phone=customer_dict.get("phone", ""),
            ),
            idempotency_key=body.get("idempotency_key", ""),
        )
        result = await plugin.create_order(req)
        return {"data": _dataclass_to_dict(result)}
    except KeyError as e:
        raise HTTPException(status_code=400, detail=f"Missing field: {e}")
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/api/v1/{vendor}/orders/{order_id}")
async def get_order(vendor: str, order_id: str):
    """GET /api/v1/{vendor}/orders/{order_id}"""
    plugin = get_plugin(vendor)
    try:
        result = await plugin.get_order(order_id)
        return {"data": _dataclass_to_dict(result)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


@app.get("/api/v1/{vendor}/orders/{order_id}/poll")
async def poll_order(vendor: str, order_id: str):
    """GET /api/v1/{vendor}/orders/{order_id}/poll"""
    return await get_order(vendor, order_id)


@app.get("/api/v1/{vendor}/inventory")
async def inventory(vendor: str, event_id: str = Query(...)):
    """GET /api/v1/{vendor}/inventory?event_id=..."""
    plugin = get_plugin(vendor)
    try:
        req = InventoryRequest(event_id=event_id)
        result = await plugin.check_inventory(req)
        return {"data": _dataclass_to_dict(result)}
    except Exception as e:
        raise HTTPException(status_code=502, detail=str(e))


# ═══════════════════════════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════════════════════════

def _dataclass_to_dict(obj):
    """Convert dataclass/enum to JSON-safe dict."""
    from dataclasses import is_dataclass, asdict
    from enum import Enum
    if isinstance(obj, Enum):
        return obj.value
    if is_dataclass(obj):
        return asdict(obj)
    return obj


@app.on_event("startup")
async def startup():
    load_plugins()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
