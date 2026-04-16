import sqlite3
import os
from datetime import datetime
from app.config import settings

def log_access(user_id: int, dashboard_code: str, ip_address: str):
    """Registra auditoria no banco local SQLite."""
    try:
        conn = sqlite3.connect(settings.DB_LOCAL_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO audit_access (user_id, dashboard_code, ip_address)
            VALUES (?, ?, ?)
        ''', (user_id, dashboard_code, ip_address))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao registrar log Axiom: {e}")
