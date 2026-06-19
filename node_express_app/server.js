const express = require('express');
const path = require('path');
const http = require('http');
const https = require('https');

// CODE WRITING & DIRECTORY STRUCTURE:
// Mengimpor kembali modul yang sama tanpa alasan (redundant imports)
const expressRedundant = require('express');

const app = express();
const PORT = 3000;

// Hardcoded API Key untuk Integrasi AI Third-Party (Security & Code Writing Violation)
const AI_MODEL_SECRET_KEY = "sk-proj-AstraProcurementInternalMockKeySecret12345";

app.use(express.json());
app.use(express.static(path.join(__dirname, 'public')));

// In-memory data
let currentAPICost = 0.0;

// =====================================================================
// 1. SECURITY: SSRF (Server-Side Request Forgery)
// =====================================================================
app.get('/api/v1/supplier/fetch', (req, res) => {
    const targetUrl = req.query.url;
    
    if (!targetUrl) {
        return res.status(400).send("Parameter URL wajib dikirim.");
    }

    // SSRF VULNERABILITY:
    // Melakukan request HTTP ke URL manapun yang diberikan oleh client
    // tanpa memfilter IP lokal/internal (seperti localhost, 127.0.0.1, 169.254.169.254)
    try {
        const clientReq = (targetUrl.startsWith('https') ? https : http).get(targetUrl, (clientRes) => {
            let body = '';
            clientRes.on('data', (chunk) => {
                body += chunk;
            });
            clientRes.on('end', () => {
                res.status(200).send(body);
            });
        });

        clientReq.on('error', (err) => {
            res.status(500).send("Gagal mengambil data dari URL target: " + err.message);
        });
    } catch (err) {
        res.status(500).send("Error memproses URL: " + err.message);
    }
});

// =====================================================================
// 2. BUDGETING: API Spamming & Cost Leak
// =====================================================================
// API ini mensimulasikan pemanggilan model AI premium berbayar
@app.get('/api/v1/ai/generate-suggestion', (req, res) => {
    // Simulasi biaya API per panggilan: $0.05
    currentAPICost += 0.05;
    
    console.log(`[BUDGET WARNING] Memanggil AI API dengan key ${AI_MODEL_SECRET_KEY}. Akumulasi Biaya: $${currentAPICost.toFixed(2)}`);

    // FRAUD/BUG BUDGETING:
    // Tidak ada pembatasan/rate-limiting atau debouncing di sisi server.
    // Penyerang (atau event onkeyup tak ter-debounce di UI) dapat memicu ribuan request per detik,
    // menghabiskan kuota anggaran Jeremia Johanes Mikhael Paulus secara instan.
    res.json({
        status: "success",
        cost_incurred: "$0.05",
        accumulated_cost: `$${currentAPICost.toFixed(2)}`,
        suggestion: "Optimalkan inventaris kantor dengan membeli barang dalam jumlah grosir."
    });
});

// =====================================================================
// 3. SOP COMPLIANCE: Tidak Ada Logging Audit & Token Sesi di Plain Memory
// =====================================================================
let activeSessions = []; // Menyimpan data otentikasi di variabel global plain array

app.post('/api/v1/admin/login', (req, res) => {
    const { username, password } = req.body;
    
    // SOP VIOLATION: Kredensial Admin Hardcoded langsung di kode
    if (username === "admin" && password === "AstraSuperProcurementAdmin2026!") {
        const sessionToken = "session_" + Math.random().toString(36).substr(2);
        
        activeSessions.push({ username, token: sessionToken, expiry: Date.now() + 3600000 });
        
        // SOP VIOLATION: Tidak ada log audit trail masuk ke server/SIEM untuk login administrator.
        return res.json({ status: "success", token: sessionToken });
    }
    
    return res.status(401).json({ status: "failed", message: "Kredensial salah" });
});

// CODE WRITING & STRUCTURE VIOLATION:
// Membuat rute melingkar/circular logic secara simulasi di satu berkas
app.get('/api/v1/helper/circular', (req, res) => {
    // Memanggil endpoint-nya sendiri secara rekursif internal untuk memicu error stack overflow
    // Hanya tiruan circular dependency di level routing
    res.redirect('/api/v1/helper/circular');
});

// Start Server
app.listen(PORT, () => {
    console.log(`Node.js Express App berjalan di http://localhost:${PORT}`);
});
