# Ticket Vendor Plugins

Ticket vendor plugins for [plugin-hub](https://github.com/shawnlin0125/plugin-hub).

## Architecture

```
ticket-vendor (this repo)
├── plugins/
│   ├── ticketmaster/    ← Full example: plugin + mock + fixtures + tests
│   ├── kktix/           ← Stub (replace with real API)
│   ├── ibon/            ← Stub
│   ├── fami/            ← Stub
│   └── tixcraft/        ← Stub
└── .github/workflows/ci.yaml  ← Isolated per-plugin CI
```

## Plugin Structure

Every plugin MUST have:

```
plugins/<name>/
├── plugin.py          ← Implements platform_plugin_sdk.Plugin
├── mock/
│   └── server.py      ← Fake API for isolated testing
├── fixtures/
│   ├── events.json    ← Test data
│   ├── empty.json     ← Empty response (edge case)
│   └── malformed.json ← Bad response (error handling)
├── tests/
│   ├── test_contract.py   ← Verifies Plugin ABC compliance
│   ├── test_transform.py  ← Verifies data format conversion
│   └── test_edge.py       ← Verifies error/edge handling
└── schema/            ← DB migrations (PostgreSQL schema)
```

## CI

Each plugin is tested independently. One failing does NOT block others.

```yaml
fail-fast: false
matrix:
  plugin: [ticketmaster, kktix, ibon, fami, tixcraft]
```

## Adding a New Plugin

1. Copy `plugins/ticketmaster/` to `plugins/<new-vendor>/`
2. Implement `Plugin` ABC (plugin_id, start, stop, health, mock, fixtures, tests)
3. Add fixture data
4. Write tests
5. Register in `pyproject.toml` under `[project.entry-points."plugin_hub.plugins"]`
6. Open PR → CI runs → if all pass → merge → plugin-hub can load it

## Install

```bash
pip install git+https://github.com/shawnlin0125/ticket-vendor.git
```
