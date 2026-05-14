# AI 開發規範 — Ticket Vendor Plugin

> 本文檔供 **AI agent** 和 **人類開發者** 共同遵循。
> 所有新增 / 修改 vendor 必須通過本規範的條件檢查。

---

## 架構角色定位

```
┌──────────────────────────────────────────┐
│         業務系統（主系統 / Upstream）        │
│    統一呼叫: /api/v1/search, /orders ...  │
└──────────────┬───────────────────────────┘
               │ 本 repo 對外合約（不可變更）
               ▼
┌──────────────────────────────────────────┐
│   票券供應商代理系統（本 repo / Proxy）      │
│   - 轉發下單、查單、輪詢、查商品結構          │
│   - 每個 vendor plugin 實作 VendorProxy ABC │
└──────────────┬───────────────────────────┘
               │ 各 vendor 自有 API
               ▼
┌──────────────────────────────────────────┐
│   外部票券供應商（Downstream）               │
│   TicketMaster / KKTIX / ibon / ...       │
└──────────────────────────────────────────┘
```

**核心規則：**
- 本 repo **是上游業務系統的 proxy**，不是終端應用
- 對上游（業務系統）：暴露**統一 API**（search, orders, inventory...）
- 對下游（外部供應商）：每個 vendor 有自己的 API 格式，由 plugin 內部轉換
- 修改任何 vendor 時，**只能動到該 vendor 的目錄**，不可跨 vendor 修改

---

## 目錄結構規範

```
plugins/<vendor_name>/          ← 唯一允許修改的範圍
├── plugin.py                   ← 實作 VendorProxy ABC（必要）
├── mock/
│   ├── vendor/                 ← 下游：模擬外部票券供應商 API（必要）
│   │   ├── server.py           ←  Mock API server
│   │   └── routes.py           ←  端點定義
│   └── business/               ← 上游：模擬業務系統呼叫（必要）
│       ├── server.py           ←  模擬業務系統對統一 API 的呼叫
│       └── scenarios.py        ←  業務情境流程（下單→查詢→輪詢）
├── fixtures/                   ← 測試資料（必要）
│   ├── normal.json             ←  正常回應
│   ├── empty.json              ←  空資料
│   └── malformed.json          ←  格式錯誤
├── schema/
│   └── migrations/             ← 獨立 DB schema（必要，不可動其他 vendor）
└── tests/                      ← 測試（必要，4 類測試缺一不可）
    ├── test_contract.py        ←  Plugin ABC 合約測試
    ├── test_vendor_mock.py     ←  下游：對外部供應商 mock 測試
    ├── test_business_mock.py   ←  上游：對業務系統 mock 測試
    └── test_integration.py     ←  雙向串接：業務 mock → proxy → vendor mock
```

---

## VendorProxy ABC 合約

每個 vendor plugin 必須實作以下介面（繼承自 `platform_plugin_sdk.Plugin`）：

### 繼承方法（必須 override）

| 方法 | 說明 |
|------|------|
| `async start()` | 啟動：連接外部 API、啟動排程 |
| `async stop()` | 停止：關閉連接、停止排程 |
| `async health() -> HealthStatus` | 健康檢查 |
| `get_mock_server()` | 回傳下游 vendor mock |
| `get_business_mock_server()` | 回傳上游業務系統 mock（NEW） |
| `get_fixtures() -> list[Fixture]` | 測試資料清單 |
| `async run_tests(mock_port) -> TestReport` | 執行全部測試 |

### 統一代辦業務 API（plugin 對外暴露）

每個 vendor plugin **必須實作以下業務端點**，這是代理系統對業務系統的統一合約：

| 端點 | 方法 | 說明 |
|------|------|------|
| `/api/v1/search` | GET | 查詢商品（活動、票種） |
| `/api/v1/orders` | POST | 建立訂單（下單） |
| `/api/v1/orders/{id}` | GET | 查詢訂單狀態（查單） |
| `/api/v1/orders/{id}/poll` | GET | 輪詢訂單最新狀態 |
| `/api/v1/inventory` | GET | 查庫存 / 商品結構 |

> 詳細規格參見 [`specs/business-api.md`](specs/business-api.md)

### 資料隔離屬性（必須正確定義）

```python
@property
def db_schema(self) -> str:
    return f"plugin_{self.plugin_id}"   # PostgreSQL schema 名稱

@property
def redis_prefix(self) -> str:
    return f"plugin:{self.plugin_id}:"  # Redis key 前綴

@property
def kafka_topic_prefix(self) -> str:    # 若使用 Kafka
    return f"plugin.{self.plugin_id}."  # Kafka topic 前綴
```

---

## 新增 Vendor 必要條件

> 詳細清單參見 [`VENDOR_CHECKLIST.md`](VENDOR_CHECKLIST.md)

### 最小必要條件（7 項）

1. ✅ `plugin.py` 實作 VendorProxy ABC 所有抽象方法
2. ✅ `mock/vendor/server.py` 存在且可啟動（至少模擬正常/錯誤/逾時/空資料）
3. ✅ `mock/business/server.py` 存在且可啟動（至少模擬 search/orders 呼叫）
4. ✅ `tests/` 包含 4 類測試：contract / vendor-mock / business-mock / integration
5. ✅ `fixtures/` 包含 normal / empty / malformed 三種測試資料
6. ✅ `schema/migrations/` 目錄存在，migration 只操作 `plugin_{vendor_id}` schema
7. ✅ `pyproject.toml` 註冊 `[project.entry-points."plugin_hub.plugins"]`

### 修改隔離規則（強制）

- **只能修改 `plugins/<vendor_name>/` 目錄內的檔案**
- 不可修改其他 `plugins/<other_vendor>/` 的任何檔案
- 不可修改 `pyproject.toml` 中其他 vendor 的 entry_point
- 不可修改 repo 根層級的共用設定（除非是新增自己的 entry_point）
- CI 會自動檢查 PR diff 是否只落在單一 vendor 目錄

### 禁止事項

- ❌ 在 plugin.py 中 import 其他 vendor 的 plugin
- ❌ 在 mock 中直接引用其他 vendor 的 fixtures
- ❌ hardcode 其他 vendor 的設定（API key、endpoint）
- ❌ 修改其他 vendor 的 schema/migration
- ❌ 跨 vendor 共用 Redis prefix 或 Kafka topic

---

## CI 自動化檢查

PR 提交後，CI 會自動執行：

| 檢查項目 | 階段 |
|----------|------|
| Vendor 隔離檢查（diff 只在單一目錄） | `validate` job |
| Plugin ABC 合約測試 | `test` job（矩陣） |
| Vendor mock 測試 | `test` job（矩陣） |
| Business mock 測試 | `test` job（矩陣） |
| Integration 雙向串接測試 | `test` job（矩陣） |

任一檢查失敗 → PR 無法 merge。

---

## 相關文件

| 文件 | 用途 |
|------|------|
| [`VENDOR_CHECKLIST.md`](VENDOR_CHECKLIST.md) | 新增 vendor 逐項檢查清單 |
| [`specs/business-api.md`](specs/business-api.md) | 業務系統統一 API 規格 |
| [`scripts/validate-vendor.py`](scripts/validate-vendor.py) | CI 自動驗證腳本 |
| [plugin-platform-architecture (skill)](https://github.com/shawnlin0125/plugin-hub) | 完整架構設計文檔 |
