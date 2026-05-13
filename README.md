# Ticket Vendor Plugin — TicketMaster Reference Implementation

Ticket vendor plugin for [plugin-hub](https://github.com/shawnlin0125/plugin-hub).

## Architecture

```
ticket-vendor (this repo)
├── plugins/
│   └── ticketmaster/    ← Complete reference implementation
│       ├── plugin.py        ← Implements platform_plugin_sdk.Plugin
│       ├── mock/server.py   ← Fake API for isolated testing
│       ├── fixtures/        ← events.json, tickets.json, empty.json, malformed.json
│       └── tests/           ← test_contract.py, test_transform.py, test_edge.py
├── k8s/
│   └── configmap-plugin-registry-ticket.yaml
├── .github/workflows/ci.yaml
└── pyproject.toml        ← entry_points registration
```

## Adding More Vendors

Copy `plugins/ticketmaster/` → `plugins/<new-vendor>/`, implement Plugin ABC, register in `pyproject.toml`.

## Install

```bash
pip install git+https://github.com/shawnlin0125/ticket-vendor.git
```
