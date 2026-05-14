# Ticket Vendor Plugin

Ticket vendor proxy plugins for [plugin-hub](https://github.com/shawnlin0125/plugin-hub).

Implements the **Consumer-Driven Contract** defined by the business system (Grails).
Each vendor plugin proxies between the unified API and external vendor APIs.

## Architecture

```
┌──────────────────────────────────────────────────────────┐
│         業務系統 (Grails)                                  │
│    GET /api/v1/ticketmaster/search?keyword=Coldplay       │
│    vendor 在 URL path，業務系統明確選擇供應商                │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│   plugin-hub (API Gateway)                                │
│   Reverse proxy → ticket-proxy pods                       │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│   ticket-proxy (FastAPI, this repo)                       │
│   vendor plugins: ticketmaster, kktix, ibon...            │
│   轉換: 統一 API format → 外部供應商 API format             │
└──────────────┬───────────────────────────────────────────┘
               │
               ▼
┌──────────────────────────────────────────────────────────┐
│   外部票券供應商: TicketMaster / KKTIX / ibon              │
└──────────────────────────────────────────────────────────┘
```

## Repository Structure

```
ticket-vendor/
├── proxy/                        ← FastAPI proxy service
│   └── main.py                   ← Serves /api/v1/{vendor}/*
├── plugins/                      ← Vendor plugin implementations
│   └── vendor_ticketmaster/      ← Reference implementation
│       ├── plugin.py             ← implements Plugin + VendorProxy ABCs
│       ├── mock/
│       │   ├── vendor/           ← Mock external vendor API
│       │   └── business/         ← Mock business system client
│       ├── fixtures/             ← Test data
│       ├── schema/migrations/    ← DB migrations (independent schema)
│       └── tests/                ← 3 test types: contract, vendor-mock, business-mock
├── unified-ticket-api/           ← Business API SDK (owned by 業務系統)
│   └── unified_ticket_api/
│       ├── abc.py                ← VendorProxy ABC (5 business methods)
│       └── models/               ← SearchRequest, OrderResponse, ...
├── specs/
│   └── business-api.md           ← Unified API specification
├── scripts/
│   ├── validate-vendor.py        ← CI convention enforcement (7 checks)
│   └── generate-manifest.py      ← Generate plugin-manifest.json
├── AI_DEVELOPMENT_GUIDE.md       ← AI agent development conventions
├── VENDOR_CHECKLIST.md           ← New vendor checklist
├── plugin-manifest.json          ← Auto-generated, consumed by plugin-hub
├── Dockerfile                    ← Ticket proxy container
└── pyproject.toml                ← Dependencies + plugin registration
```

## Two SDKs, Two Contracts

Every vendor plugin inherits from **two ABCs**:

| ABC | Owner | Defines | Repo |
|-----|:-----:|---------|------|
| `Plugin` (platform_plugin_sdk) | plugin-hub | lifecycle: start/stop/health | plugin-hub |
| `VendorProxy` (unified_ticket_api) | 業務系統 | business: search/orders/inventory | ticket-vendor |

```python
from platform_plugin_sdk import Plugin
from unified_ticket_api import VendorProxy

class TicketmasterPlugin(Plugin, VendorProxy):
    async def start(self): ...       # ← Plugin ABC
    async def search(self, req): ... # ← VendorProxy ABC
```

## Adding a New Vendor

1. Copy `plugins/vendor_ticketmaster/` → `plugins/vendor_{new}/`
2. Implement both ABCs (Plugin + VendorProxy)
3. Write 3 test types (contract / vendor-mock / business-mock)
4. Register entry point in `pyproject.toml`
5. Submit PR → CI matrix tests → all pass
6. CI auto-updates `plugin-manifest.json`
7. Hub auto-discovers new vendor (dashboard shows ✨NEW badge + CI status)
8. Click **Enable** → vendor goes live on ALL proxy instances
9. Update `proxy-plugins` ConfigMap (from Hub's `/api/load-plugins`) → restart proxy pods

**See:** [`AI_DEVELOPMENT_GUIDE.md`](AI_DEVELOPMENT_GUIDE.md) + [`VENDOR_CHECKLIST.md`](VENDOR_CHECKLIST.md)

## Development

```bash
# Install
pip install git+https://github.com/shawnlin0125/plugin-hub.git#subdirectory=platform-plugin-sdk
pip install -e /path/to/ticket-vendor/unified-ticket-api
pip install -e ".[dev]"

# Run tests
cd plugins/vendor_ticketmaster && python -m pytest tests/ -v

# Validate conventions
python scripts/validate-vendor.py ticketmaster

# Generate manifest
python scripts/generate-manifest.py > plugin-manifest.json

# Run proxy locally
pip install fastapi uvicorn aiohttp
LOAD_PLUGINS=ticketmaster python proxy/main.py
```

## CI

PR to `plugins/**` triggers:
1. **validate** — vendor isolation + convention check
2. **test** — matrix of all plugins (fail-fast: false)
3. **manifest** — auto-generate `plugin-manifest.json`

## Business API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/{vendor}/search` | Search events |
| POST | `/api/v1/{vendor}/orders` | Create order |
| GET | `/api/v1/{vendor}/orders/{id}` | Get order |
| GET | `/api/v1/{vendor}/orders/{id}/poll` | Poll order |
| GET | `/api/v1/{vendor}/inventory` | Check inventory |

Full spec: [`specs/business-api.md`](specs/business-api.md)
