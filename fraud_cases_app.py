from flask import Flask, request, jsonify
import time
import threading

app = Flask(__name__)

# Database in-memory sederhana untuk simulasi
accounts = {
    "ACC001": {"name": "Alice", "balance": 1000.0, "role": "user"},
    "ACC002": {"name": "Bob", "balance": 500.0, "role": "user"},
    "ACC_ADMIN": {"name": "Administrator", "balance": 10000.0, "role": "admin"},
    "ACC_DEV": {"name": "Developer Hidden Account", "balance": 0.0, "role": "user"}
}

products = {
    "PROD_LAPTOP": {"name": "Laptop Gaming", "price": 1200.0},
    "PROD_MOUSE": {"name": "Wireless Mouse", "price": 50.0}
}


# =====================================================================
# CASE 1: Fraud Nilai Negatif (Negative Value Transfer)
# =====================================================================
# Penjelasan: Fungsi transfer tidak memvalidasi apakah jumlah (amount) 
# yang dikirim bernilai positif. Penyerang bisa mengirimkan nilai negatif 
# untuk menyedot uang dari akun target ke akun mereka sendiri.
@app.route('/api/transfer', methods=['POST'])
def transfer_funds():
    data = request.get_json()
    from_acc = data.get("from_account")
    to_acc = data.get("to_account")
    amount = float(data.get("amount", 0))

    if from_acc not in accounts or to_acc not in accounts:
        return jsonify({"status": "failed", "message": "Akun tidak ditemukan"}), 404

    # FRAUD/BUG: Tidak ada validasi `if amount <= 0`
    # Jika amount = -500, maka:
    # balance Alice = 1000 - (-500) = 1500
    # balance Bob = 500 + (-500) = 0
    # Alice berhasil mencuri 500 dari Bob tanpa persetujuan Bob!
    if accounts[from_acc]["balance"] < amount:
         return jsonify({"status": "failed", "message": "Saldo tidak mencukupi"}), 400

    accounts[from_acc]["balance"] -= amount
    accounts[to_acc]["balance"] += amount

    return jsonify({
        "status": "success", 
        "message": f"Transfer sebesar {amount} berhasil",
        "sender_balance": accounts[from_acc]["balance"],
        "recipient_balance": accounts[to_acc]["balance"]
    })


# =====================================================================
# CASE 2: Parameter Tampering & IDOR (Insecure Direct Object Reference)
# =====================================================================
# Penjelasan: API untuk melihat detail akun hanya mengandalkan parameter 
# `account_id` yang dikirim oleh client tanpa memverifikasi apakah token 
# sesi milik akun tersebut. Penyerang dapat membaca saldo akun orang lain.
@app.route('/api/account/details', methods=['GET'])
def get_account_details():
    # Mengambil account_id langsung dari query parameter tanpa memvalidasi
    # session/cookie kepemilikan akun.
    account_id = request.args.get("account_id")
    
    # FRAUD/BUG: Langsung mengembalikan data akun tanpa otorisasi kepemilikan
    if account_id in accounts:
        return jsonify({
            "status": "success",
            "account": accounts[account_id]
        })
    return jsonify({"status": "failed", "message": "Akun tidak ditemukan"}), 404


# =====================================================================
# CASE 3: Manipulasi Harga Barang saat Checkout (Price Manipulation)
# =====================================================================
# Penjelasan: Aplikasi mempercayai harga (price) yang dikirim oleh client 
# di dalam request payload, bukan mengambil data harga valid dari database internal.
@app.route('/api/checkout', methods=['POST'])
def checkout_item():
    data = request.get_json()
    account_id = data.get("account_id")
    product_id = data.get("product_id")
    
    # FRAUD/BUG: Mengambil harga langsung dari input client (request payload)
    # Penyerang bisa mengirimkan payload: {"product_id": "PROD_LAPTOP", "price": 1.0}
    client_provided_price = float(data.get("price")) 

    if account_id not in accounts:
        return jsonify({"status": "failed", "message": "Akun tidak valid"}), 404
        
    if product_id not in products:
        return jsonify({"status": "failed", "message": "Produk tidak ditemukan"}), 404

    # Membayar menggunakan saldo wallet
    user_balance = accounts[account_id]["balance"]
    if user_balance < client_provided_price:
        return jsonify({"status": "failed", "message": "Saldo tidak mencukupi"}), 400

    accounts[account_id]["balance"] -= client_provided_price
    
    return jsonify({
        "status": "success",
        "message": f"Pembelian {products[product_id]['name']} berhasil seharga {client_provided_price}",
        "remaining_balance": accounts[account_id]["balance"]
    })


# =====================================================================
# CASE 4: Race Condition / Double Spending
# =====================================================================
# Penjelasan: Penarikan saldo atau pembayaran tidak menggunakan mekanisme 
# locking/atomic transaction. Jika request dikirim bersamaan secara multi-thread,
# user bisa menarik uang melebihi saldo yang mereka miliki.
@app.route('/api/withdraw', methods=['POST'])
def withdraw_funds():
    data = request.get_json()
    account_id = data.get("account_id")
    amount = float(data.get("amount", 0))

    if account_id not in accounts:
        return jsonify({"status": "failed", "message": "Akun tidak ditemukan"}), 404

    current_balance = accounts[account_id]["balance"]

    # FRAUD/BUG: Pengecekan saldo dan pengurangan tidak bersifat atomik (tidak di-lock)
    if current_balance >= amount:
        # Simulasi delay network/proses database agar memicu race condition
        time.sleep(0.5) 
        
        accounts[account_id]["balance"] -= amount
        return jsonify({
            "status": "success", 
            "amount_withdrawn": amount,
            "new_balance": accounts[account_id]["balance"]
        })
    else:
        return jsonify({"status": "failed", "message": "Saldo tidak cukup"}), 400


# =====================================================================
# CASE 5: Salami Slicing (Fraud Pembulatan Pecahan Uang)
# =====================================================================
# Penjelasan: Saat menghitung bagi hasil atau bunga pecahan desimal kecil, 
# nilai sisa pembulatan ke bawah dialihkan secara sengaja ke akun tertentu 
# (milik oknum developer/orang dalam) alih-alih dibuang atau masuk kas resmi.
@app.route('/api/calculate-interest', methods=['POST'])
def calculate_interest():
    data = request.get_json()
    account_id = data.get("account_id")
    
    if account_id not in accounts:
        return jsonify({"status": "failed", "message": "Akun tidak ditemukan"}), 404

    balance = accounts[account_id]["balance"]
    
    # Hitung bunga 1.25%
    raw_interest = balance * 0.0125
    
    # Ambil nilai yang dibulatkan ke bawah untuk user
    user_interest = round(raw_interest, 2)
    
    # FRAUD: Mengambil selisih desimal pembulatan (sisa pecahan)
    # Selisih dikumpulkan secara diam-diam dan dialihkan ke akun developer
    salami_slice = raw_interest - user_interest
    
    if salami_slice > 0:
        # Mengirimkan sisa pecahan uang secara diam-diam ke developer hidden account
        accounts["ACC_DEV"]["balance"] += salami_slice
        
    accounts[account_id]["balance"] += user_interest

    return jsonify({
        "status": "success",
        "interest_added": user_interest,
        "new_balance": accounts[account_id]["balance"],
        "developer_vault_balance": accounts["ACC_DEV"]["balance"] # Hanya untuk pembuktian POC
    })

if __name__ == '__main__':
    app.run(port=5000, debug=True)
