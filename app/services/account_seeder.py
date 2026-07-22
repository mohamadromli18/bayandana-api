DEFAULT_PSAK109_ACCOUNTS = [
    # 1. ASET
    {"account_code": "1110", "account_name": "Kas Kecil", "account_type": "Asset", "is_active": True},
    {"account_code": "1120", "account_name": "Kas Bank", "account_type": "Asset", "is_active": True},
    {"account_code": "1210", "account_name": "Aset Tetap", "account_type": "Asset", "is_active": True},
    
    # 2. KEWAJIBAN
    {"account_code": "2110", "account_name": "Hutang Jangka Pendek", "account_type": "Liability", "is_active": True},
    
    # 3. SALDO DANA
    {"account_code": "3110", "account_name": "Saldo Dana Amil", "account_type": "Equity", "is_active": True},
    {"account_code": "3120", "account_name": "Saldo Dana Zakat", "account_type": "Equity", "is_active": True},
    {"account_code": "3130", "account_name": "Saldo Dana Infaq Terikat", "account_type": "Equity", "is_active": True},
    {"account_code": "3140", "account_name": "Saldo Dana Infaq Tidak Terikat", "account_type": "Equity", "is_active": True},
    
    # 4. PENERIMAAN
    {"account_code": "4110", "account_name": "Penerimaan Zakat", "account_type": "Revenue", "is_active": True},
    {"account_code": "4120", "account_name": "Penerimaan Infaq Terikat", "account_type": "Revenue", "is_active": True},
    {"account_code": "4130", "account_name": "Penerimaan Infaq Tidak Terikat", "account_type": "Revenue", "is_active": True},
    {"account_code": "4140", "account_name": "Pendapatan Lain-lain", "account_type": "Revenue", "is_active": True},
    
    # 5. PENYALURAN & BEBAN
    {"account_code": "5110", "account_name": "Penyaluran Program Zakat", "account_type": "Expense", "is_active": True},
    {"account_code": "5120", "account_name": "Penyaluran Program Infaq", "account_type": "Expense", "is_active": True},
    {"account_code": "5130", "account_name": "Beban Operasional Masjid", "account_type": "Expense", "is_active": True},
    {"account_code": "5140", "account_name": "Beban Kafalah (Honor/Gaji)", "account_type": "Expense", "is_active": True},
]