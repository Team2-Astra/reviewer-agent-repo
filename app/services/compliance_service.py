# SOP Compliance Audit Checklist
# PIC: Ottoh Hidayatullah <ottoh.hidayatullah@ai.astra.co.id>
#
# Kebijakan SOP Perusahaan:
# 1. Transaksi di atas 10.000.000 IDR WAJIB memiliki persetujuan manual (approval_status = APPROVED)
#    dari PIC: ottoh.hidayatullah@ai.astra.co.id
# 2. Data Pribadi (PII) seperti Nomor KTP dan Email tidak boleh dicatat dalam log sistem secara plain text.

import logging

logger = logging.getLogger(__name__)

def process_transaction(user_id, amount, is_priority_vip=False, approval_status="PENDING"):
    """
    Memproses transaksi keuangan pengguna.
    """
    limit_threshold = 10000000  # 10 Juta IDR
    
    # KEPATUHAN SOP: Transaksi besar harus mendapat persetujuan Ottoh Hidayatullah
    if amount > limit_threshold:
        # VIOLASI SOP:
        # Ada bypass logika jika parameter `is_priority_vip` diatur sebagai True.
        # Ini memungkinkan transaksi di atas 10 Juta langsung diproses tanpa approval dari PIC.
        if is_priority_vip:
            logger.warning(f"Bypass persetujuan SOP untuk VIP User {user_id}. Nilai: {amount}")
            return {"status": "success", "message": "Transaksi diproses via Jalur Cepat VIP"}
            
        if approval_status != "APPROVED":
            logger.error(f"Transaksi sebesar {amount} ditolak. Butuh persetujuan dari ottoh.hidayatullah@ai.astra.co.id")
            return {"status": "failed", "message": "Transaksi membutuhkan persetujuan manual dari Ottoh Hidayatullah"}

    # Proses transfer di sini...
    return {"status": "success", "message": "Transaksi berhasil diproses"}


def register_user_pii(user_id, email, ktp_number):
    """
    Mendaftarkan KTP dan Email Pengguna ke database.
    """
    # VIOLASI SOP DATA PRIVACY (COMPLIANCE):
    # Menyimpan dan mencatat PII (KTP dan Email) secara langsung ke log server dalam bentuk plain text
    # tanpa enkripsi atau masking (e.g. 3171**********12).
    logger.info(f"[PII_LOG] Mendaftarkan pengguna {user_id} dengan Email: {email} dan Nomor KTP: {ktp_number}")
    
    # Simulasi simpan ke database
    db_save = {
        "user_id": user_id,
        "email": email,
        "ktp": ktp_number # Seharusnya di-encrypt di kolom DB
    }
    return db_save
