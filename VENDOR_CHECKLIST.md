# Vendor 新增檢查清單

> 新增 vendor plugin 時，逐項勾選確認。全部 ✅ 才能提交 PR。
> CI 會自動驗證標記 [CI] 的項目。

---

## A. 目錄結構 [CI]

- [ ] `plugins/<vendor_name>/plugin.py` 存在
- [ ] `plugins/<vendor_name>/mock/vendor/server.py` 存在
- [ ] `plugins/<vendor_name>/mock/business/server.py` 存在
- [ ] `plugins/<vendor_name>/fixtures/` 至少包含 3 個檔案：
  - `normal.json`（正常回應）
  - `empty.json`（空資料）
  - `malformed.json`（格式錯誤）
- [ ] `plugins/<vendor_name>/schema/migrations/` 目錄存在
- [ ] `plugins/<vendor_name>/tests/` 至少包含 4 個測試檔案：
  - `test_contract.py`
  - `test_vendor_mock.py`
  - `test_business_mock.py`
  - `test_integration.py`

---

## B. Plugin 實作 [CI]

- [ ] `plugin.py` 繼承 `platform_plugin_sdk.Plugin`
- [ ] 正確定義 `plugin_id`、`plugin_name`、`version`
- [ ] 實作所有抽象方法：
  - [ ] `async start()`
  - [ ] `async stop()`
  - [ ] `async health() -> HealthStatus`
  - [ ] `get_mock_server()` — 回傳 vendor mock server instance
  - [ ] `get_business_mock_server()` — 回傳 business mock server instance
  - [ ] `get_fixtures() -> list[Fixture]`
  - [ ] `async run_tests(mock_port) -> TestReport`
- [ ] 正確定義資料隔離屬性：
  - [ ] `db_schema` → `plugin_{vendor_id}`
  - [ ] `redis_prefix` → `plugin:{vendor_id}:`
  - [ ] `kafka_topic_prefix` → `plugin.{vendor_id}.`（若使用 Kafka）
- [ ] 實作統一業務 API 端點（參見 `specs/business-api.md`）：
  - [ ] `search` — 查詢商品
  - [ ] `orders.create` — 建立訂單
  - [ ] `orders.get` — 查詢訂單
  - [ ] `orders.poll` — 輪詢訂單
  - [ ] `inventory` — 查庫存

---

## C. Vendor Mock（下游：外部供應商）[CI]

- [ ] `mock/vendor/server.py` 可獨立啟動（`python mock/vendor/server.py`）
- [ ] 至少模擬以下情境：
  - [ ] 正常回應（回傳 fixtures 中的資料）
  - [ ] 錯誤回應（4xx / 5xx）
  - [ ] 逾時（timeout）
  - [ ] 空資料（empty）
- [ ] 支援分頁（若外部 API 有分頁）

---

## D. Business Mock（上游：業務系統）[CI]

- [ ] `mock/business/server.py` 可獨立啟動
- [ ] 模擬業務系統對統一 API 的呼叫：
  - [ ] `GET /api/v1/search` — 查詢商品
  - [ ] `POST /api/v1/orders` — 建立訂單
  - [ ] `GET /api/v1/orders/{id}` — 查詢訂單
  - [ ] `GET /api/v1/orders/{id}/poll` — 輪詢訂單
  - [ ] `GET /api/v1/inventory` — 查庫存
- [ ] `mock/business/scenarios.py` 包含至少 2 個業務情境：
  - [ ] 正常流程：查詢 → 下單 → 查單 → 完成
  - [ ] 異常流程：下單失敗 → 重試 / 逾時處理

---

## E. 測試覆蓋 [CI]

### test_contract.py — Plugin ABC 合約
- [ ] 驗證 `plugin_id` / `plugin_name` / `version` 正確定義
- [ ] 驗證 `db_schema` / `redis_prefix` 符合命名規範
- [ ] 驗證 `get_mock_server()` 回傳有效 instance
- [ ] 驗證 `get_business_mock_server()` 回傳有效 instance（NEW）
- [ ] 驗證 `get_fixtures()` 回傳至少 3 個 fixture

### test_vendor_mock.py — 下游供應商 Mock
- [ ] 測試正常 API 回應（events / tickets）
- [ ] 測試錯誤處理（404 / 500）
- [ ] 測試分頁
- [ ] 測試逾時處理

### test_business_mock.py — 上游業務系統 Mock（NEW）
- [ ] 測試 search 端點
- [ ] 測試 orders create 端點
- [ ] 測試 orders get 端點
- [ ] 測試 orders poll 端點
- [ ] 測試 inventory 端點

### test_integration.py — 雙向串接（NEW）
- [ ] 完整流程測試：business mock → proxy → vendor mock
- [ ] 異常流程測試：vendor 錯誤 → proxy 正確轉換錯誤格式

---

## F. 修改隔離 [CI]

- [ ] PR diff 只修改 `plugins/<vendor_name>/` 目錄
- [ ] 未修改 `plugins/<other_vendor>/` 的任何檔案
- [ ] `pyproject.toml` 只新增自己的 `entry_point`，未動其他 vendor
- [ ] 未修改 `AI_DEVELOPMENT_GUIDE.md`、`specs/`、`scripts/`（除非是改進規範本身）

---

## G. 註冊 [CI]

- [ ] `pyproject.toml` 的 `[project.entry-points."plugin_hub.plugins"]` 正確新增
- [ ] entry_point 的 import path 正確（`vendor_{name}.plugin:{ClassName}`）
- [ ] `plugins/<vendor_name>/` 目錄名稱與 `entry_point` 名稱一致
- [ ] `pip install -e ".[dev]"` 可成功安裝

---

## 通過標準

- A~G 全部項目 ✅ → PR 可提交
- 任一 ❌ → 先補齊再提交
- CI 的 `validate` job 會自動檢查標記 [CI] 的項目
