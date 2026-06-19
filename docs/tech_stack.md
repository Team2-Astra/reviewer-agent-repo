# Dokumentasi Stack Teknologi Aplikasi (Tech Stack)

Dokumen ini menjelaskan daftar teknologi, framework, pustaka (libraries), dan konfigurasi yang digunakan dalam pembuatan aplikasi simulasi audit internal (**Astra Cash Finance** dan **Astra Procurement Hub**).

---

## 1. Aplikasi 1: Astra Cash Finance Portal (Python Flask)

Aplikasi pertama dibangun menggunakan ekosistem Python untuk mensimulasikan backend perbankan/fintech internal.

### A. Backend Stack
* **Bahasa Pemrograman**: Python 3.x
* **Web Framework**: **Flask (v3.1.x)**
  * Dipilih karena bersifat mikro (micro-framework), ringan, dan mudah dikonfigurasi untuk membuat rute API RESTful dan merender halaman HTML sederhana secara cepat tanpa konfigurasi boilerplate yang berat.
* **WSGI Utility Library**: **Werkzeug**
  * Server pengembangan bawaan Flask yang menangani request/response HTTP di level WSGI.
* **Template Engine**: **Jinja2**
  * Mesin templating yang digunakan untuk merender file HTML dinamis (`templates/index.html`) dari sisi server.

### B. Database Stack
* **Engine**: **SQLite3**
  * Database relasional berbasis file lokal (`finance.db`). Sangat cocok untuk POC karena tidak memerlukan setup server database eksternal (seperti PostgreSQL/MySQL) namun tetap mendukung query SQL standar yang rentan terhadap SQL Injection.

### C. Frontend Stack
* **Markup**: HTML5
* **Styling**: Vanilla CSS3 (Inline & internal style sheets).
* **Interaktivitas**: Vanilla JavaScript (ES6) menggunakan Fetch API untuk berkomunikasi secara asinkron (AJAX) dengan backend API Flask.

---

## 2. Aplikasi 2: Astra Procurement & Supplier Hub (Node.js Express)

Aplikasi kedua dibangun menggunakan ekosistem JavaScript sisi server (Node.js) untuk mensimulasikan sistem pengadaan barang.

### A. Backend Stack
* **Runtime Environment**: **Node.js**
  * Runtime JavaScript berbasis mesin V8 Google Chrome untuk mengeksekusi kode JS di sisi server.
* **Web Framework**: **Express.js (v4.19.x)**
  * Web framework standar industri yang minimalis untuk Node.js guna mengelola routing, middleware, dan static files.
* **HTTP Client**: Node.js Native HTTP & HTTPS Modules
  * Digunakan untuk mengimplementasikan fitur fetching dokumen eksternal yang sengaja dikonfigurasi rentan terhadap Server-Side Request Forgery (SSRF).

### B. Frontend Stack
* **Markup & UI**: HTML5 dengan struktur form terintegrasi.
* **Styling**: Vanilla CSS3 dengan penekanan pada visualisasi manipulatif (deceptive UI / button mismatch).
* **Interaktivitas**: Vanilla JavaScript (ES6) untuk manipulasi DOM dinamis (DOM-based XSS) dan pelacakan interaksi real-time tanpa debounce (API spamming).

---

## 3. Matriks Perbandingan & Tujuan Pengujian

Kedua stack ini dipilih sengaja untuk merepresentasikan dua arsitektur pemrograman yang paling sering digunakan di lingkungan internal Astra:

| Aspek Pengujian | Python Flask App | Node.js Express App |
| :--- | :--- | :--- |
| **Utama** | Keamanan Data & Transaksi Finansial | Integrasi Pihak Ketiga & Input DOM |
| **Simulasi Database** | SQLite (SQL Injection) | In-Memory Object State |
| **Kerentanan Keamanan** | SQLi, Path Traversal | SSRF, DOM XSS |
| **Celah Logika / Fraud** | VIP Bypass (SOP), Split Billing, Markup | API Billing Leak, Session Token leak |
| **Pelanggaran Desain** | Biaya Tersembunyi (2px font), Kontras Buruk | Deceptive Buttons (Warna terbalik) |
