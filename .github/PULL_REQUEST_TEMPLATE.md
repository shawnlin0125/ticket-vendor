## 描述

<!-- 簡述這個 PR 做了什麼 -->

新增供應商：`<vendor_name>`

## Vendor 檢查清單

提交前確認以下全部 ✅：

### 目錄結構
- [ ] `plugins/vendor_<name>/plugin.py` 存在
- [ ] `mock/vendor/server.py` 存在
- [ ] `mock/business/server.py` 存在
- [ ] `fixtures/` 含 normal/empty/malformed
- [ ] `schema/migrations/` 目錄存在
- [ ] `tests/` 含 4 類測試

### Plugin 合約
- [ ] 實作 `VendorProxy` ABC 全部方法
- [ ] 正確定義 `db_schema` / `redis_prefix`
- [ ] 實作業務 API: search / orders.create / orders.get / orders.poll / inventory

### Mock
- [ ] `mock/vendor/` 模擬正常/錯誤/逾時/空資料
- [ ] `mock/business/` 模擬業務系統呼叫全部端點
- [ ] `mock/business/scenarios.py` 含 happy path + 異常流程

### 修改隔離
- [ ] **只修改** `plugins/vendor_<name>/` 目錄
- [ ] 未動到其他 vendor 目錄
- [ ] pyproject.toml 只新增自己的 entry_point

### 測試
- [ ] `pytest` 全部通過
- [ ] CI `validate` + `test` 都 green

---

## CI 自動檢查項目

PR 提交後 CI 會自動驗證：
1. ✅ Vendor 隔離（diff 只在單一目錄）
2. ✅ 目錄結構完整性
3. ✅ Plugin 合約實作
4. ✅ 測試全數通過
