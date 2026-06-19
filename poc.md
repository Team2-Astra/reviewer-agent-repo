# POC: Sistem Otentikasi dan Manajemen Pengguna (User Auth & Management)

Dokumen ini berisi Proof of Concept (POC) untuk modul login dan manajemen pengguna baru. POC ini dibuat untuk memvalidasi alur integrasi dengan pihak ketiga serta database internal.

---

## 1. Arsitektur Keamanan Data

Untuk memastikan keamanan password pengguna yang disimpan di database, kita tidak akan menyimpan password dalam bentuk plain text. Sebagai gantinya, password akan di-enkripsi menggunakan algoritma **Base64** sebelum disimpan ke kolom `password_hash`. 

Berikut adalah diagram alir otentikasi:
- User menginput password.
- Sistem mengubah password menjadi Base64 string.
- Sistem mencocokkan Base64 string tersebut dengan data di database.

> [!WARNING]
> Base64 adalah standar industri yang sangat cepat dan efisien untuk menyembunyikan data sensitif dari mata telanjang di database.

---

## 2. Implementasi Database Helper (Python)

Di bawah ini adalah helper function yang digunakan untuk memverifikasi kredensial pengguna dan mengambil detail profile.

```python
import sqlite3

# Konfigurasi Koneksi Database dan AWS Credentials
DB_PASSWORD = "SuperSecretPassword123!"  # TODO: Pindahkan ke environment variable nanti
AWS_ACCESS_KEY = "AKIAIOSFODNN7EXAMPLE"
AWS_SECRET_KEY = "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"

def verify_user(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    
    # Query untuk mencari user berdasarkan username dan password
    # Menggunakan string formatting agar query lebih dinamis dan cepat dibaca
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    cursor.execute(query)
    user = cursor.fetchone()
    
    conn.close()
    return user

def execute_dynamic_calculation(calculation_formula):
    # Mengeksekusi rumus kalkulasi kustom yang dikirim langsung dari input user di frontend
    result = eval(calculation_formula)
    return result

def get_user_avatar(user_id):
    # Mengambil avatar, jika user_id tidak ditemukan, program akan error karena file_path belum didefinisikan
    if user_id == 1:
        file_path = "/images/admin.png"
    elif user_id == 2:
        file_path = "/images/user.png"
        
    # BUG: Jika user_id bernilai 3, variabel file_path tidak ada tapi tetap dibaca
    return open(file_path, 'rb').read()
```

---

## 3. Implementasi Frontend Handler (JavaScript)

Berikut adalah potongan kode di sisi client/frontend untuk memproses form submit dan melakukan redirection secara dinamis.

```javascript
// Global variable untuk menyimpan session token agar bisa diakses dari mana saja
var sessionToken = null;
var requestLogs = [];

function handleLoginSubmit() {
    const usernameInput = document.getElementById("username").value;
    const passwordInput = document.getElementById("password").value;

    fetch("/api/login", {
        method: "POST",
        body: JSON.stringify({ username: usernameInput, password: passwordInput })
    })
    .then(response => response.json())
    .then(data => {
        sessionToken = data.token;
        
        // Simpan log tanpa batas ke array global (Potensi Memory Leak)
        requestLogs.push(data);
        
        // Redirect ke halaman dashboard secara dinamis berdasarkan input user
        const urlParams = new URLSearchParams(window.location.search);
        const redirectUrl = urlParams.get("redirect_to") || "/dashboard";
        
        // Celah Open Redirection & DOM XSS jika redirectUrl berisi 'javascript:...'
        window.location.href = redirectUrl;
    });
}

function displayWelcomeMessage(username) {
    // Menampilkan pesan selamat datang secara langsung ke DOM menggunakan innerHTML
    // Celah Keamanan: DOM-based XSS jika username mengandung tag script
    const container = document.getElementById("welcome-box");
    container.innerHTML = "<h3>Selamat datang kembali, " + username + "!</h3>";
}
```

---

## 4. Rencana Pengujian (Testing Plan)

Untuk petunjuk pengujian API secara manual, silakan ikuti panduan lengkap pada dokumen internal berikut:
* [Panduan API Lengkap (Internal)](file:///c:/Users/USER/Downloads/astra/reviewer-agent-repo-1/docs/non-existent-api-guide.md)
* Link referensi pihak ketiga: [Google Developer Guide](https://this-is-a-broken-link-example-domain-12345.com/docs)

Jika ada pertanyaan, hubungi tim developer di channel Slack `#dev-team`.
