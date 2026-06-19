# Spesifikasi Teknis & Stack Aplikasi (Technical Specifications & Tech Stack)

Dokumen ini mendokumentasikan spesifikasi sistem, struktur direktori, detail endpoint API (input/output), serta stack teknologi yang diimplementasikan pada aplikasi **Astra Cash Finance** dan **Astra Procurement Hub**.

---

## 1. Struktur Direktori Workspace

Workspace ini dikonfigurasi dengan struktur multi-bahasa sebagai berikut:

```text
c:\Users\USER\Downloads\astra\reviewer-agent-repo-1/
├── app/
│   ├── config/
│   │   └── database_credentials.txt  # Plaintext db credentials committed to VCS
│   └── services/
│       ├── compliance_service.py     # SOP Compliance violations helper
│       └── budgeting_service.py      # Budgeting violations helper
├── docs/
│   ├── fraud_cases_poc.md            # Dokumentasi audit kasus fraud
│   ├── tech_stack.md                 # Deskripsi singkat stack teknologi
│   └── specifications_and_stack.md   # Spesifikasi teknis & detail API (Dokumen Ini)
├── node_express_app/
│   ├── package.json                  # Dependensi Node.js
│   ├── public/
│   │   └── index.html                # UI DOM XSS & Deceptive buttons
│   └── server.js                     # Backend Node.js (SSRF, API Spamming)
├── python_flask_app/
│   ├── config/
│   │   └── credentials.env.txt       # Plaintext AWS/API credentials
│   ├── logs/
│   │   └── pii_logs.txt              # Hasil log data sensitif (Email & KTP)
│   ├── reports/
│   │   ├── report_q1.txt             # Dummy report file
│   │   └── report_q2.txt             # Dummy report file
│   ├── templates/
│   │   └── index.html                # UI Flask & Dark patterns
│   ├── app.py                        # Backend Flask (SQLi, Path Traversal, SOP bypass)
│   └── finance.db                    # Database SQLite lokal
└── README.md
```

---

## 2. Spesifikasi Stack Teknologi

### A. Astra Cash Finance (Python Flask App)
* **Runtime**: Python 3.12+
* **Framework**: Flask v3.1.3 (Micro web framework)
* **Dependencies**:
  * `Werkzeug` v3.1.8 (WSGI request/response handling)
  * `Jinja2` v3.1.6 (HTML templating engine)
  * `itsdangerous` v2.2.0 (Cryptographic signing helper)
  * `click` v8.4.1 (Command-line interface builder)
  * `blinker` v1.9.0 (Fast signal programming utility)
* **Database**: SQLite3 (Local engine)

### B. Astra Procurement Hub (Node.js Express App)
* **Runtime**: Node.js v18+
* **Framework**: Express.js v4.19.2 (Minimalist web framework)
* **Dependencies**:
  * `express` v4.19.2
* **HTTP Client**: Built-in `http` & `https` core Node modules.

---

## 3. Spesifikasi Endpoint API (API Specification)

### A. Endpoints - Python Flask Application (`http://127.0.0.1:5000`)

#### 1. Transfer Dana
* **Path**: `/api/v1/transfer`
* **Method**: `POST`
* **Content-Type**: `application/json`
* **Payload Request**:
  ```json
  {
    "from_account": "ACC001",
    "to_account": "ACC002",
    "amount": 15000000.0,
    "email": "alice@ai.astra.co.id",
    "ktp": "3171020304050001",
    "is_priority_vip": true,
    "insurance_add_on": true
  }
  ```
* **Response Body (Success)**:
  ```json
  {
    "status": "success",
    "transferred": 15000000.0,
    "insurance_deducted": 1500000.0,
    "new_balance": 33500000.0,
    "message": "Transaksi berhasil diproses."
  }
  ```
* **Fraud/Vulnerability**: 
  * Bypasses Ottoh Hidayatullah's manual approval for transfers > 10M IDR via `is_priority_vip = true`.
  * Logs unencrypted `email` and `ktp` parameters in `logs/pii_logs.txt`.
  * Deducts hidden fee of 1,500,000 IDR if `insurance_add_on = true`.

#### 2. Cari Anggota (SQL Injection)
* **Path**: `/api/v1/users/search`
* **Method**: `GET`
* **Query Parameter**: `q` (string)
  * Contoh: `/api/v1/users/search?q=Alice`
* **Response Body (Success)**:
  ```json
  {
    "status": "success",
    "results": [
      {
        "id": 1,
        "username": "Alice",
        "balance": 50000000.0,
        "role": "user"
      }
    ]
  }
  ```
* **Fraud/Vulnerability**: SQL Injection. Input string `q` dilewatkan langsung ke interpreter SQLite.

#### 2B. Ubah Role Pengguna (SQL Injection - Multiple Statements)
* **Path**: `/api/v1/users/update-role-unsafe`
* **Method**: `POST`
* **Content-Type**: `application/json`
* **Payload Request**:
  ```json
  {
    "username": "Bob",
    "role": "admin"
  }
  ```
* **Response Body (Success)**:
  ```json
  {
    "status": "success",
    "message": "Role user Bob berhasil diupdate ke admin"
  }
  ```
* **Fraud/Vulnerability**: SQL Injection dengan Multi-Statements. Menggunakan `executescript` pada database SQLite yang memungkinkan eksekusi rangkaian query terpisah, misalnya payload: `Bob'; UPDATE users SET balance = 99999999 WHERE username = 'Bob';--`.

#### 2C. Ping Host Server (OS Command Injection)
* **Path**: `/api/v1/system/ping-host`
* **Method**: `GET`
* **Query Parameter**: `host` (string)
  * Contoh: `/api/v1/system/ping-host?host=127.0.0.1`
* **Response Body (Success)**:
  ```json
  {
    "status": "success",
    "output": "Pinging 127.0.0.1 with 32 bytes of data...\nReply from 127.0.0.1: bytes=32 time<1ms TTL=128\n"
  }
  ```
* **Fraud/Vulnerability**: OS Command Injection. Input parameter `host` digabungkan langsung ke string perintah command shell yang dijalankan oleh server tanpa validasi/sanitasi, memungkinkan eksekusi perintah OS eksternal (contoh payload: `127.0.0.1 & dir`).

#### 3. Unduh Laporan (Path Traversal)
* **Path**: `/api/v1/reports/download`
* **Method**: `GET`
* **Query Parameter**: `file` (string)
  * Contoh: `/api/v1/reports/download?file=report_q1.txt`
* **Response Body**: Berkas stream teks mentah.
* **Fraud/Vulnerability**: Path Traversal. Input parameter `file` tidak divalidasi, memungkinkan pembacaan berkas rahasia di luar folder `reports` via payload `../config/credentials.env.txt`.

#### 4. Pengajuan Reimbursement (Split Billing & Markup)
* **Path**: `/api/v1/reimbursement/submit`
* **Method**: `POST`
* **Content-Type**: `application/json`
* **Payload Request**:
  ```json
  {
    "amount": 30000000.0,
    "description": "Pembelian Software Server"
  }
  ```
* **Response Body (Success)**:
  ```json
  {
    "status": "success",
    "description": "Pembelian Software Server",
    "original_requested": 30000000.0,
    "approved_reimbursement_with_markup": 33000000.0,
    "note": "Reimbursement berhasil didaftarkan. Dana akan segera dikirim."
  }
  ```
* **Fraud/Vulnerability**: 
  * Split billing vulnerability: Tidak ada pengecekan akumulasi transaksi untuk membatasi bypass limit persetujuan Jeremia Paulus (> 50M IDR).
  * Markup fraud: Otomatis membesarkan total klaim sebesar 10% secara tidak sah.

---

### B. Endpoints - Node.js Express Application (`http://localhost:3000`)

#### 1. Fetch Data Supplier (SSRF)
* **Path**: `/api/v1/supplier/fetch`
* **Method**: `GET`
* **Query Parameter**: `url` (string)
  * Contoh: `/api/v1/supplier/fetch?url=http://localhost:5000/`
* **Response Body**: HTML / JSON output dari target URL.
* **Fraud/Vulnerability**: SSRF. Server langsung melakukan HTTP GET request ke URL yang diberikan client tanpa validasi IP lokal.

#### 2. AI Suggestion (API Billing Spamming)
* **Path**: `/api/v1/ai/generate-suggestion`
* **Method**: `GET`
* **Response Body**:
  ```json
  {
    "status": "success",
    "cost_incurred": "$0.05",
    "accumulated_cost": "$2.50",
    "suggestion": "Optimalkan inventaris kantor dengan membeli barang dalam jumlah grosir."
  }
  ```
* **Fraud/Vulnerability**: API Cost Spamming. Endpoint berbayar ini tidak membatasi request per menit (tanpa rate limiter) dan tidak memiliki mekanisme caching.

#### 3. Administrator Login (SOP & Audit Bypass)
* **Path**: `/api/v1/admin/login`
* **Method**: `POST`
* **Content-Type**: `application/json`
* **Payload Request**:
  ```json
  {
    "username": "admin",
    "password": "AstraSuperProcurementAdmin2026!"
  }
  ```
* **Response Body (Success)**:
  ```json
  {
    "status": "success",
    "token": "session_3h9skd9fj2s"
  }
  ```
* **Fraud/Vulnerability**: 
  * Password admin di-hardcode dalam file server.js.
  * Ketiadaan log audit trail (audit logging) saat administrator melakukan login.
