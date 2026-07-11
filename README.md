# Restaurant API

這是一個以 FastAPI 建立的餐廳管理後端，提供前台查詢、後台管理與使用者登入註冊功能。

## 功能

- 前台餐廳查詢
- 後台餐廳新增、修改、刪除
- 後台使用者列表、權限管理、刪除
- 使用者註冊、登入、登出
- 餐廳圖片上傳與 `/assets` 靜態檔案存取
- Redis session 驗證

## 技術棧

- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis
- bcrypt
- python-jose
- aiofiles

## 啟動方式

### 1. 安裝相依套件

```bash
uv sync
```

### 2. 確認資料庫與 Redis

預設連線設定寫在 `sys.ini`：

- PostgreSQL: `localhost:5432`
- Database: `restaurant`
- Redis: `localhost:6379`

### 3. 啟動服務

```bash
uv run python src/main.py
```

服務預設啟動在：

- `http://127.0.0.1:8888`
- Swagger UI: `http://127.0.0.1:8888/docs`

## 路由概覽

### 前台 API

| Method | Path | 說明 | 驗證 |
| --- | --- | --- | --- |
| GET | `/front/restaurant/all` | 查詢餐廳列表 | 需要 `session_id` cookie |

### 後台餐廳 API

| Method | Path | 說明 | 驗證 |
| --- | --- | --- | --- |
| GET | `/end/restaurant/all` | 查詢餐廳列表 | 管理員 |
| GET | `/end/restaurant/category` | 查詢餐廳分類 | 管理員 |
| POST | `/end/restaurant` | 新增餐廳 | 管理員 |
| PUT | `/end/restaurant` | 更新餐廳 | 管理員 |
| DELETE | `/end/restaurant` | 刪除餐廳 | 管理員 |

### 後台使用者 API

| Method | Path | 說明 | 驗證 |
| --- | --- | --- | --- |
| GET | `/end/user/all` | 查詢使用者列表 | 管理員 |
| PUT | `/end/user/update_access` | 更新使用者管理員權限 | 管理員 |
| DELETE | `/end/user` | 刪除使用者 | 管理員 |

### 一般使用者 API

| Method | Path | 說明 |
| --- | --- | --- |
| GET | `/user/check_name_existed` | 檢查使用者名稱是否可用 |
| GET | `/user/check_email_existed` | 檢查 Email 是否可用 |
| POST | `/user/signup` | 註冊 |
| POST | `/user/login` | 登入 |
| POST | `/user/logout` | 登出 |

## 驗證方式

- 登入成功後，系統會寫入 `session_id` cookie
- Session 資料儲存在 Redis
- 後台 API 需要管理員權限
- 前台餐廳查詢與登入後的 session 驗證也依賴 `session_id`

## 回傳格式

餐廳與使用者列表 API 會回傳二元組：

```json
[
  [/* 資料陣列 */],
  123
]
```

第二個值是總筆數，用於分頁。

## 餐廳圖片

上傳的餐廳圖片會存到專案內的 `uploads/`，並透過 `/assets` 對外提供：

- 檔案路徑範例：`/assets/example.jpg`

## 專案結構

```text
db/
src/
  main.py
  dependencies/
  exception_handle/
  router/
  service/
  tool/
  vm/
  test/
uploads/
```

## 備註

- 預設 CORS 只允許 `http://localhost:5173`
- 預設埠號是 `8888`
- `sys.ini` 內含資料庫、Redis 與 JWT 相關預設設定
