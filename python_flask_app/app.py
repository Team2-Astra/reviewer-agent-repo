import os
import sqlite3
from flask import Flask, request, jsonify, render_template, send_file

app = Flask(__name__)

# Directory setup
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'finance.db')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')
REPORTS_DIR = os.path.join(BASE_DIR, 'reports')

os.makedirs(LOGS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)

# Create dummy reports
with open(os.path.join(REPORTS_DIR, 'report_q1.txt'), 'w') as f:
    f.write("Astra Cash Finance Report Q1: Total Revenue = 150B IDR.")
with open(os.path.join(REPORTS_DIR, 'report_q2.txt'), 'w') as f:
    f.write("Astra Cash Finance Report Q2: Total Revenue = 180B IDR.")

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT,
            balance REAL,
            role TEXT
        )
    ''')
    cursor.execute('DELETE FROM users')
    cursor.execute("INSERT INTO users (username, balance, role) VALUES ('Alice', 50000000.0, 'user')")
    cursor.execute("INSERT INTO users (username, balance, role) VALUES ('Bob', 20000000.0, 'user')")
    cursor.execute("INSERT INTO users (username, balance, role) VALUES ('ottoh_admin', 999999999.0, 'admin')")
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

# =====================================================================
# 1. SOP COMPLIANCE (Ottoh Hidayatullah) & PII Logging
# =====================================================================
@app.route('/api/v1/transfer', methods=['POST'])
def transfer():
    data = request.get_json()
    from_acc = data.get('from_account')
    to_acc = data.get('to_account')
    amount = float(data.get('amount', 0))
    email = data.get('email')
    ktp = data.get('ktp')
    is_priority_vip = data.get('is_priority_vip', False)
    insurance_add_on = data.get('insurance_add_on', False)

    # SOP VIOLATION: Logging PII data (KTP and Email) to a plaintext file
    log_file_path = os.path.join(LOGS_DIR, 'pii_logs.txt')
    with open(log_file_path, 'a') as f:
        f.write(f"USER_ID: {from_acc} | Email: {email} | KTP: {ktp} | Amount: {amount}\n")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Check sender balance
    cursor.execute("SELECT balance FROM users WHERE username = ?", (from_acc,))
    sender = cursor.fetchone()
    if not sender:
        return jsonify({"status": "failed", "message": "Sender account not found"}), 404
        
    sender_balance = sender[0]
    total_deduction = amount

    # STYLE & DESIGN VIOLATION: Dark Pattern (Hidden Fees)
    # Jika insurance_add_on di-check (yang di-check secara default di UI), potong saldo 1.5 Juta IDR tambahan secara paksa.
    if insurance_add_on:
        total_deduction += 1500000.0

    if sender_balance < total_deduction:
        return jsonify({"status": "failed", "message": "Saldo tidak mencukupi"}), 400

    # SOP COMPLIANCE VIOLATION (Ottoh Hidayatullah Approval check bypass):
    # Otorisasi Ottoh Hidayatullah <ottoh.hidayatullah@ai.astra.co.id>
    # Transaksi di atas 10.000.000 IDR harus disetujui. Namun dibypass jika status `is_priority_vip` bernilai True.
    if amount > 10000000.0 and not is_priority_vip:
        return jsonify({
            "status": "failed", 
            "message": "Transaksi > 10 Juta IDR memerlukan persetujuan dari PIC SOP: ottoh.hidayatullah@ai.astra.co.id"
        }), 403

    # Deduct & Add
    cursor.execute("UPDATE users SET balance = balance - ? WHERE username = ?", (total_deduction, from_acc))
    cursor.execute("UPDATE users SET balance = balance + ? WHERE username = ?", (amount, to_acc))
    conn.commit()

    # Get updated balance
    cursor.execute("SELECT balance FROM users WHERE username = ?", (from_acc,))
    new_balance = cursor.fetchone()[0]
    conn.close()

    return jsonify({
        "status": "success",
        "transferred": amount,
        "insurance_deducted": 1500000.0 if insurance_add_on else 0.0,
        "new_balance": new_balance,
        "message": "Transaksi berhasil diproses."
    })

# =====================================================================
# 2. SECURITY: SQL Injection
# =====================================================================
@app.route('/api/v1/users/search', methods=['GET'])
def search_users():
    query = request.args.get('q', '')
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # SECURITY VIOLATION: SQL Injection
    # Menyisipkan query string langsung ke SQL execution
    sql = f"SELECT id, username, balance, role FROM users WHERE username = '{query}'"
    try:
        cursor.execute(sql)
        results = cursor.fetchall()
        user_list = []
        for r in results:
            user_list.append({
                "id": r[0],
                "username": r[1],
                "balance": r[2],
                "role": r[3]
            })
        conn.close()
        return jsonify({"status": "success", "results": user_list})
    except Exception as e:
        conn.close()
        return jsonify({"status": "error", "message": str(e)}), 500

# =====================================================================
# 3. SECURITY: Path Traversal
# =====================================================================
@app.route('/api/v1/reports/download', methods=['GET'])
def download_report():
    file_name = request.args.get('file', '')
    
    # SECURITY VIOLATION: Path Traversal
    # Menggabungkan nama file secara langsung tanpa validasi direktori / path sanitization
    target_file = os.path.join(REPORTS_DIR, file_name)
    
    if os.path.exists(target_file):
        # Penyerang dapat mengunduh berkas kredensial sensitif:
        # http://127.0.0.1:5000/api/v1/reports/download?file=../config/credentials.env.txt
        return send_file(target_file)
    else:
        return jsonify({"status": "failed", "message": f"File {file_name} tidak ditemukan di direktori reports"}), 404

# =====================================================================
# 4. BUDGETING: Split Billing & Reimbursement Fraud
# =====================================================================
@app.route('/api/v1/reimbursement/submit', methods=['POST'])
def submit_reimbursement():
    data = request.get_json()
    amount = float(data.get('amount', 0))
    description = data.get('description', '')

    # BUDGETING LIMIT (Jeremia Johanes Mikhael Paulus):
    # Pengeluaran di atas 50.000.000 IDR harus melalui persetujuan Jeremia.
    # BUDGETING VIOLATION: Kerentanan Split Billing.
    # Sistem tidak membatasi beberapa klaim berurutan di bawah 50 Juta IDR dalam waktu singkat.
    if amount > 50000000.0:
        return jsonify({
            "status": "failed", 
            "message": "Pengajuan di atas 50 Juta IDR harus disetujui secara manual oleh jeremia.paulus@ai.astra.co.id"
        }), 403

    # BUDGETING VIOLATION: Fraud biaya markup otomatis 10%
    # Jumlah klaim yang diproses diam-diam ditambahkan markup 10% untuk "keuntungan admin"
    final_amount = amount * 1.10

    return jsonify({
        "status": "success",
        "description": description,
        "original_requested": amount,
        "approved_reimbursement_with_markup": final_amount,
        "note": "Reimbursement berhasil didaftarkan. Dana akan segera dikirim."
    })

# CODE WRITING & DIRECTORY STRUCTURE VIOLATIONS:
# Spasi berantakan, kode tidak terstruktur, import diletakkan di tengah script (jika ada),
# dan file database diletakkan di root folder project.

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)
