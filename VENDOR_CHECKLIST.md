# Vendor 新增檢查清單

> 新增 vendor plugin 時，逐項勾選確認。全部 ✅ 才能提交 PR。
> CI 會自動驗證標記 [CI] 的項目。

---

## A. 目錄結構 [CI]

- [ ] `plugins/<vendor_name>/plugin.py` 存在
- [ ] `plugins/<vendor_name>/mock/vendor/server.py` 存在
- [ ] `plugins/<vendor_name>/mock/business/server.py` 存在
- [ ] `plugins/<vendor_name>/mock/business/scenarios.py` 存在
- [ ] `plugins/<vendor_name>/fixtures/` 至少包含 3 個檔案：
  - `normal.json`（正常回應）
  - `empty.json`（空資料）
  - `malformed.json`（格式錯誤）
- [ ] `plugins/<vendor_name>/schema/migrations/` 目錄存在
- [ ] `plugins/<vendor_name>/tests/` 包含 3 個測試檔案：
  - `test_contract.py` — Plugin ABC 合約測試
  - `test_vendor_mock.py` — Vendor 隔離測試
  - `test_business_mock.py` — Business 隔離測試

---

## B. Plugin 實作 [CI]

- [ ] `plugin.py` 繼承 `platform_plugin_sdk.Plugin`
- [ ] 正確定義 `plugin_id`、`plugin_name`、`version`
- [ ] 實作所有抽象方法：
  - [ ] `async start()`
  - [ ] `async stop()`
  - [ ] `async health() -> HealthStatus`
  - [ ] `get_mock_server()` — 回傳 vendor mock server instance
  - [ ] `get_business_mock_server()` — 回傳 BusinessMockClient class
  - [ ] `get_fixtures() -> list[Fixture]`
  - [ ] `async run_tests(mock_port) -> TestReport`
- [ ] 正確定義資料隔離屬性：
  - [ ] `db_schema` → `plugin_{vendor_id}`
  - [ ] `redis_prefix` → `plugin:{vendor_id}:`
  - [ ] `kafka_topic_prefix` → `plugin.{vendor_id}.`（若使用 Kafka）
- [ ] 實作統一業務 API 端點（參見 `specs/business-api.md`），vendor 由 URL path 指定：
  - [ ] `search` — GET `/api/v1/{vendor}/search`
  - [ ] `orders.create` — POST `/api/v1/{vendor}/orders`
  - [ ] `orders.get` — GET `/api/v1/{vendor}/orders/{id}`
  - [ ] `orders.poll` — GET `/api/v1/{vendor}/orders/{id}/poll`
  - [ ] `inventory` — GET `/api/v1/{vendor}/inventory`

---

## C. Vendor Mock（下游：外部供應商）[CI]

- [ ] `mock/vendor/server.py` 可獨立啟動
- [ ] 至少模擬以下情境：
  - [ ] 正常回應（回傳 fixtures 中的資料）
  - [ ] 錯誤回應（4xx / 5xx）
  - [ ] 逾時（timeout）
  - [ ] 空資料（empty）
- [ ] 支援分頁（若外部 API 有分頁）

---

## D. Business Mock（上游：業務系統）[CI]

- [ ] `BusinessMockClient` 建構時接受 `vendor` 參數
- [ ] URL 自動產生為 `/api/v1/{vendor}/...` 格式
- [ ] 模擬業務系統對統一 API 的呼叫：
  - [ ] `search(keyword, ...)` → GET `/api/v1/{vendor}/search`
  - [ ] `create_order(...)` → POST `/api/v1/{vendor}/orders`
  - [ ] `get_order(order_id)` → GET `/api/v1/{vendor}/orders/{id}`
  - [ ] `poll_order(order_id)` → GET `/api/v1/{vendor}/orders/{id}/poll`
  - [ ] `check_inventory(event_id)` → GET `/api/v1/{vendor}/inventory`
- [ ] `scenarios.py` 包含至少 2 個業務情境：
  - [ ] 正常流程：查詢 → 下單 → 查單 → 完成
  - [ ] 異常流程：下單失敗 → 重試 / 逾時處理

---

## E. 測試覆蓋 [CI]

### test_contract.py — Plugin ABC 合約
- [ ] 驗證 `plugin_id` / `plugin_name` / `version` 正確定義
- [ ] 驗證 `db_schema` / `redis_prefix` 符合命名規範
- [ ] 驗證 `get_mock_server()` 回傳有效 instance
- [ ] 驗證 `get_business_mock_server()` 回傳有效 class
- [ ] 驗證 `get_fixtures()` 回傳至少 3 個 fixture

### test_vendor_mock.py — Vendor 隔離測試
- [ ] 啟動 vendor mock server，測試正常 API 回應
- [ ] 測試錯誤處理（404 / 500）
- [ ] 測試分頁
- [ ] 測試逾時處理

### test_business_mock.py — Business 隔離測試
- [ ] 驗證 `BusinessMockClient` 存在所有必要方法
- [ ] 驗證 URL prefix 格式為 `/api/v1/{vendor}`
- [ ] 驗證所有 scenarios 存在（happy_path / vendor_timeout / empty_results...）
- [ ] 驗證 happy_path 涵蓋全部 5 個端點

---

## F. 修改隔離 [CI]

- [ ] PR diff 只修改 `plugins/<vendor_name>/` 目錄
- [ ] 未修改 `plugins/<other_vendor>/` 的任何檔案
- [ ] `pyproject.toml` 只新增自己的 `entry_point`，未動其他 vendor
- [ ] 未修改共用規範文件（`AI_DEVELOPMENT_GUIDE.md`、`specs/`、`scripts/`）

---

## G. 註冊 [CI]

- [ ] `pyproject.toml` 的 `[project.entry-points."plugin_hub.plugins"]` 正確新增
- [ ] entry_point 的 import path 正確（`vendor_{name}.plugin:{ClassName}`）
- [ ] `plugins/<vendor_name>/` 目錄名稱與 `entry_point` 名稱一致

---

## 通過標準

- A~G 全部項目 ✅ → PR 可提交
- 任一 ❌ → 先補齊再提交
- CI 的 `validate` job 會自動檢查標記 [CI] 的項目
