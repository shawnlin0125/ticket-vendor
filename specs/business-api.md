# 業務系統統一 API 規格

> 本文件定義代理系統對上游業務系統暴露的**統一 API 合約**。
> 所有 vendor plugin 必須實作這些端點。
> URL 透過路徑第一段指定 vendor，業務系統明確選擇使用哪個票券供應商。

---

## 設計原則

- **vendor 顯式路由**：vendor 在 URL 路徑中 (`/api/v1/{vendor}/...`)，語意清晰
- **統一合約**：不同 vendor 的 API 格式相同，業務系統只需換 vendor name
- **錯誤統一**：所有錯誤回應使用相同格式，不論下游供應商回傳什麼
- **可 mock**：每個 vendor 的 `mock/business/` 必須模擬這些端點的呼叫行為

```
業務系統                                   代理系統
┌──────────────────┐          GET /api/v1/ticketmaster/search?keyword=Coldplay
│ 選擇供應商:        │ ──────────────────────────────────────────────────────▶
│ ● TicketMaster    │
│ ○ KKTIX           │          GET /api/v1/kktix/search?keyword=五月天
│ ○ ibon            │ ──────────────────────────────────────────────────────▶
└──────────────────┘
```

---

## 通用規範

### 認證

```
Authorization: Bearer <business-system-token>
```

> 不再需要 `X-Vendor` header — vendor 已從 URL 路徑取得。

### 錯誤回應格式

```json
{
  "error": {
    "code": "VENDOR_TIMEOUT",
    "message": "外部供應商無回應",
    "vendor_code": "ETIMEDOUT",
    "retryable": true
  }
}
```

### 成功回應格式

```json
{
  "data": { ... },
  "meta": {
    "vendor": "ticketmaster",
    "request_id": "req_abc123",
    "timestamp": "2026-05-14T08:00:00Z"
  }
}
```

---

## 端點規格

### 1. 查詢商品結構 / 活動

```
GET /api/v1/{vendor}/search
```

**路徑參數:**

| 參數 | 說明 | 範例 |
|------|------|------|
| `vendor` | 供應商 ID | `ticketmaster`, `kktix`, `ibon` |

**Query Parameters:**

| 參數 | 類型 | 必要 | 說明 |
|------|------|------|------|
| `keyword` | string | 否 | 關鍵字搜尋（活動名稱、藝人） |
| `category` | string | 否 | 分類（concert, sports, theater...） |
| `date_from` | ISO 8601 | 否 | 活動起始日 |
| `date_to` | ISO 8601 | 否 | 活動結束日 |
| `page` | integer | 否 | 頁碼（default: 1） |
| `page_size` | integer | 否 | 每頁筆數（default: 20, max: 100） |

**範例請求:**
```
GET /api/v1/ticketmaster/search?keyword=Coldplay&page=1&page_size=20
```

**Response:**

```json
{
  "data": {
    "items": [
      {
        "id": "evt_001",
        "name": "Coldplay 2026 世界巡迴演唱會",
        "vendor_event_id": "TICKETMASTER_evt_001",
        "category": "concert",
        "venue": "台北小巨蛋",
        "date": "2026-07-15T19:30:00+08:00",
        "status": "on_sale",
        "price_range": {
          "min": 800,
          "max": 8800,
          "currency": "TWD"
        },
        "seat_categories": [
          {"id": "seat_a", "name": "搖滾區", "price": 8800},
          {"id": "seat_b", "name": "看台區", "price": 4800}
        ]
      }
    ],
    "total": 150,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 2. 建立訂單（下單）

```
POST /api/v1/{vendor}/orders
```

**範例請求:**
```
POST /api/v1/ticketmaster/orders
```

**Request Body:**

```json
{
  "event_id": "evt_001",
  "seat_category": "seat_a",
  "quantity": 2,
  "customer": {
    "name": "王小明",
    "email": "wang@example.com",
    "phone": "+886912345678"
  },
  "idempotency_key": "idem_20260514_001"
}
```

**Response (202 Accepted):**

```json
{
  "data": {
    "order_id": "ord_20260514_001",
    "vendor_order_id": "TM_ORDER_ABC123",
    "status": "pending",
    "created_at": "2026-05-14T08:00:00Z",
    "expires_at": "2026-05-14T08:10:00Z"
  }
}
```

**狀態說明：**
- `pending` — 已提交，等待供應商確認
- `confirmed` — 供應商已確認
- `failed` — 下單失敗
- `expired` — 逾時未付款

---

### 3. 查詢訂單狀態（查單）

```
GET /api/v1/{vendor}/orders/{order_id}
```

**範例請求:**
```
GET /api/v1/ticketmaster/orders/ord_20260514_001
```

**Response:**

```json
{
  "data": {
    "order_id": "ord_20260514_001",
    "vendor_order_id": "TM_ORDER_ABC123",
    "status": "confirmed",
    "event_name": "Coldplay 2026 世界巡迴演唱會",
    "seat_category": "搖滾區",
    "quantity": 2,
    "total_amount": 17600,
    "currency": "TWD",
    "created_at": "2026-05-14T08:00:00Z",
    "confirmed_at": "2026-05-14T08:02:00Z",
    "tickets": [
      {"ticket_no": "TKT001", "barcode": "BC123456"},
      {"ticket_no": "TKT002", "barcode": "BC123457"}
    ]
  }
}
```

---

### 4. 輪詢訂單狀態

```
GET /api/v1/{vendor}/orders/{order_id}/poll
```

> 與 `GET /orders/{id}` 相同，但設計意圖是用於輪詢（short polling）。
> 業務系統應使用此端點搭配定時輪詢，而非 webhook。

**範例請求:**
```
GET /api/v1/ticketmaster/orders/ord_20260514_001/poll
```

**Response:** 同 `GET /orders/{id}`

---

### 5. 查詢庫存

```
GET /api/v1/{vendor}/inventory
```

**Query Parameters:**

| 參數 | 類型 | 必要 | 說明 |
|------|------|------|------|
| `event_id` | string | 是 | 活動 ID |

**範例請求:**
```
GET /api/v1/ticketmaster/inventory?event_id=evt_001
```

**Response:**

```json
{
  "data": {
    "event_id": "evt_001",
    "updated_at": "2026-05-14T08:00:05Z",
    "seat_categories": [
      {
        "id": "seat_a",
        "name": "搖滾區",
        "available": 1200,
        "total": 5000
      },
      {
        "id": "seat_b",
        "name": "看台區",
        "available": 3400,
        "total": 8000
      }
    ]
  }
}
```

---

## Vendor 實作指引

### 每個 vendor plugin 必須：

1. **在 `plugin.py` 中定義對應的 API handler**
   ```python
   async def handle_search(self, params: dict) -> dict:
       """將統一的 search 參數轉換為 TicketMaster API 呼叫"""
       ...

   async def handle_create_order(self, order: dict) -> dict:
       """將統一訂單格式轉換為 TicketMaster 下單請求"""
       ...
   ```

2. **在 `mock/business/server.py` 中模擬業務系統呼叫這些端點**
   ```python
   # BusinessMockClient 建構時傳入 vendor name，URL 自動帶入
   client = BusinessMockClient(proxy_url="http://127.0.0.1:8080", vendor="ticketmaster")
   
   # 實際呼叫：GET /api/v1/ticketmaster/search?keyword=Coldplay
   result = await client.search(keyword="Coldplay")
   ```

3. **在 `mock/business/scenarios.py` 中定義業務情境**
   ```python
   SCENARIOS = {
       "happy_path": [
           ("search", {"keyword": "Coldplay"}),
           ("create_order", {"event_id": "evt_001", ...}),
           ("get_order", {"order_id": "..."}),
           ("poll_order", {"order_id": "..."}),
           ("check_inventory", {"event_id": "evt_001"}),
       ],
   }
   ```

---

## 錯誤碼對照

| 統一錯誤碼 | HTTP status | 說明 |
|-----------|-------------|------|
| `VENDOR_TIMEOUT` | 504 | 外部供應商逾時 |
| `VENDOR_ERROR` | 502 | 外部供應商錯誤 |
| `VENDOR_UNAVAILABLE` | 503 | 外部供應商不可用 |
| `INVALID_REQUEST` | 400 | 請求參數錯誤 |
| `ORDER_NOT_FOUND` | 404 | 訂單不存在 |
| `INSUFFICIENT_INVENTORY` | 409 | 庫存不足 |
| `DUPLICATE_ORDER` | 409 | 重複訂單（idempotency key） |
| `RATE_LIMITED` | 429 | 請求頻率限制 |
| `VENDOR_NOT_FOUND` | 404 | URL 中的 vendor 不存在或未啟用 |
