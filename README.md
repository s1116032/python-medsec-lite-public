# MedSec-Lite — 醫療級微服務 POC (Proof of Concept)

![Python](https://img.shields.io/badge/Python-3.10%2B-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688?logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-v2-E91E63?logo=pydantic&logoColor=white)
![JWT](https://img.shields.io/badge/JWT-Authentication-black?logo=json-web-tokens&logoColor=white)

這是一個基於 **FastAPI** 核心架構開發的醫療級微服務概念驗證 (POC) 專案。本專案專為滿足醫療產業對**高安全性 API 控管**、**自動化合規文件協作**，以及**高效能地端 AI 模型整合**等核心痛點而設計。

---

## 🎯 為什麼選擇 FastAPI？ (技術選型論述)

針對醫療微服務與地端 AI 整合的嚴苛需求，本專案捨棄傳統的 Flask/Django，選擇 FastAPI 作為核心框架，其關鍵技術考量如下：

### 1. 安全性第一道防線 (Data Integrity)
醫療資料不容許任何注入攻擊。FastAPI 原生嚴格整合 **Pydantic**，在資料進入業務邏輯層（Business Logic）前，即在網關邊界進行嚴格的型別與格式驗證。
* **實作亮點**：利用 Pydantic 結合正規表達式（Regex），在最外層直接阻斷不符合規範的異常病歷號輸入，有效防堵惡意注入。

### 2. 原生非同步高效能 (Async Architecture)
醫療院所常需於地端部署 AI 模型（如 ASR 語音轉文字、影像辨識、LLM 文本去識別化等），這些任務通常伴隨高延遲。
* **實作亮點**：基於 ASGI 的 `async`/`await` 架構。在執行模擬地端 AI 推論等高延遲任務時，系統能有效釋放控制權、不阻塞主執行緒（Non-blocking I/O），確保其他常規 API 請求（如掛號、檢驗資料查詢）維持高吞吐量，效能大幅優於傳統同步框架。

### 3. 自動化互動式文件與流暢協作 (OpenAPI)
在醫療資訊系統（HIS）整合中，跨團隊溝通成本極高。
* **實作亮點**：FastAPI 基於 Type Hints 自動生成符合 **OpenAPI (Swagger UI)** 標準的互動式文件，並原生支援 OAuth2 認證流程。前後端工程師或內部測試人員可直接在網頁上模擬登入、取得 Token 並調用 API，達成合規與高效協作。

---

## 📂 專案檔案結構 (關注點分離)

雖然本專案為極簡 POC，但仍嚴格遵循**關注點分離（Separation of Concerns, SoC）**與**模組化**原則，確保未來正式擴展或替換模組（如由 Mock DB 切換至實體 PostgreSQL/MongoDB）時，核心主邏輯不受影響：

```text
MedSec-Lite/
├── main.py           # 應用程式入口：初始化 FastAPI、註冊 API 路由、實作非同步 AI 模擬
├── models.py         # 資料模型層：Pydantic Models (實作病歷嚴格驗證、去識別化欄位篩選模型)
├── security.py       # 安全機制層：JWT 生成與解析、OAuth2 流程、RBAC 角色權限依賴注入
├── mock_db.py        # 模擬資料庫：Mock 帳號與結構化病歷資料
├── requirements.txt  # 依賴套件清單
└── README.md         # 專案說明與面試技術論述重點

```

---

## 🛠️ 核心功能展示 (Core APIs)

本 POC 共實作 **4 個核心 API 端點**，全方位展示資安控管與高效能非阻塞設計：

### 1. `POST /token`

* **功能說明**：用戶登入驗證，取得存取憑證。
* **技術亮點**：密碼採用 **Bcrypt 雜湊演算法** 進行驗證，驗證成功後回傳符合安全規範的無狀態（Stateless）**JWT (JSON Web Token)**。

### 2. `GET /patients/{id}`

* **功能說明**：讀取敏感病歷資料。
* **技術亮點【RBAC 資料級別動態控管】**：
* **醫師角色 (doctor)**：系統回傳包含身分證字號、詳細病史及精確年齡的完整病歷。
* **研究員角色 (researcher)**：系統內部自動調用去識別化模型，**自動隱藏身分證與病史，並將年齡模糊化區間化**，符合醫療隱私合規法規。



### 3. `DELETE /patients/{id}`

* **功能說明**：刪除病歷資料。
* **技術亮點【RBAC 端點級別權限控管】**：利用 FastAPI 的依賴注入（Dependency Injection）機制進行防禦。僅限 `doctor` 角色有權呼叫；若 `researcher` 嘗試呼叫，系統將在路由層直接攔截並返回 `403 Forbidden`。

### 4. `POST /ai/predict`

* **功能說明**：模擬整合地端 AI 推論任務。
* **技術亮點【非阻塞設計 (Non-blocking IO)】**：使用 `asyncio.sleep(1)` 模擬 AI 推論的高延遲。在高併發測試下，該端點不會影響其他常規 API 的響應速度，實證系統具備整合高耗能地端模型之能力。

---

## 👥 測試帳號與權限矩陣

| 帳號 (Username) | 密碼 (Password) | 角色 (Role) | 權限範圍 (Scope) |
| --- | --- | --- | --- |
| **doctor** | `password` | 醫師 | 可讀取完整病歷、可執行刪除、可呼叫 AI 推論 |
| **researcher** | `password` | 研究員 | 僅能讀取**去識別化**病歷、無刪除權限、可呼叫 AI 推論 |

---

## 🚀 如何執行與動態演示

### 1. 環境準備

建議使用 **Python 3.10 或以上** 版本：

```bash
# 複製或進入專案目錄
cd MedSec-Lite

# 安裝必備依賴套件
pip install -r requirements.txt

```

### 2. 啟動服務

使用高效能 ASGI 伺服器 `uvicorn` 啟動應用：

```bash
python main.py
# 或者使用命令列啟動：uvicorn main:app --reload

```

### 3. 透過 Swagger UI 進行重點演示 🎯

服務啟動後，請開啟瀏覽器前往：[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

💡 **流程：**

1. 點擊 Swagger UI 右上角的 **"Authorize"** 按鈕。
2. **測試點一（權限攔截）**：輸入 `researcher` / `password` 登入。呼叫 `DELETE /patients/PT-123456`，觀察系統回傳 `403 Forbidden`。再呼叫 `GET /patients/PT-123456`，**可以親眼觀察到系統動態進行「資料級別去識別化控管」**：身分證字號被隱藏、年齡自動模糊化。
3. **測試點二（完整授權）**：點擊登出，重新輸入 `doctor` / `password` 登入。呼叫同一個 `GET /patients/PT-123456` 端點，此時將能順利取得無遮蔽的完整病歷敏感欄位。

## License
Copyright © 2026 hanwu910514.

詳情請參閱[Apache License 2.0](LICENSE)檔案