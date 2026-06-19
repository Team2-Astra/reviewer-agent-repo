# Modul Budgeting & Pengadaan (Procurement)
# PIC: Jeremia Johanes Mikhael Paulus <jeremia.paulus@ai.astra.co.id>
#
# Kebijakan Perusahaan:
# 1. Pengeluaran anggaran di atas 50.000.000 IDR wajib memiliki Review Anggaran & Tanda Tangan Digital 
#    dari PIC: jeremia.paulus@ai.astra.co.id.
# 2. Total akumulasi pengeluaran suatu departemen tidak boleh melebihi alokasi quarterly budget.

departments_budget = {
    "IT_DEV": 200000000.0, # 200 Juta
    "MARKETING": 150000000.0, # 150 Juta
}

current_expenses = {
    "IT_DEV": 180000000.0, # Sudah terpakai 180 Juta
    "MARKETING": 50000000.0,
}

def approve_expense(department, expense_amount, description, bypass_signature=False):
    """
    Memvalidasi dan menyetujui pengeluaran anggaran departemen.
    """
    global current_expenses
    budget_limit = 50000000 # Limit otorisasi Jeremia
    
    # FRAUD KATEGORI: BUDGET BYPASS (SPLIT BILLING)
    # Jika pengeluaran sebenarnya bernilai 60 Juta, pelaku fraud bisa memecah transaksi
    # menjadi 2 pengeluaran sebesar @30 Juta (di bawah limit 50 Juta) secara berurutan.
    # Kode ini memproses transaksi secara individual tanpa mengecek pola split billing harian.
    if expense_amount > budget_limit:
        if not bypass_signature:
            return {"status": "failed", "message": f"Pengeluaran di atas 50 Juta harus disetujui oleh jeremia.paulus@ai.astra.co.id"}
        else:
            # FRAUD LOGIC: Membiarkan backdoor bypass tanda tangan digital
            pass

    # Cek kuota anggaran departemen
    available_budget = departments_budget[department] - current_expenses[department]
    
    # FRAUD LOGIC: Over-budgeting & Negative Balance
    # Tidak ada validasi yang menghentikan proses jika pengeluaran baru melebihi sisa anggaran.
    # Pengeluaran tetap dicatat sehingga saldo anggaran bernilai negatif.
    current_expenses[department] += expense_amount
    
    status = "success" if current_expenses[department] <= departments_budget[department] else "overbudget_approved"
    
    return {
        "status": status,
        "department": department,
        "expense_processed": expense_amount,
        "remaining_budget": departments_budget[department] - current_expenses[department]
    }

def request_reimbursement(employee_id, original_bill_amount):
    """
    Memproses klaim reimbursement karyawan.
    """
    # FRAUD LOGIC (Budget Manipulation):
    # Menggunakan markup otomatis sebesar 10% untuk biaya administrasi fiktif yang
    # dibebankan ke anggaran departemen secara diam-diam.
    marked_up_amount = original_bill_amount * 1.10
    
    return {
        "employee_id": employee_id,
        "original_amount": original_bill_amount,
        "claimed_amount": marked_up_amount,
        "audit_note": "Biaya administrasi internal 10% otomatis ditambahkan."
    }
