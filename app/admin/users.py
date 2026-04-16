from fastapi import APIRouter, Depends, HTTPException, Form
from app.auth.dependencies import login_required
from app.config import settings
import sqlite3

router = APIRouter(prefix="/admin/api", tags=["admin"])

@router.post("/permissao/toggle")
async def toggle_permission(
    user_id: int = Form(...), 
    dashboard_id: int = Form(...),
    admin=Depends(login_required)
):
    if not admin.get("is_admin"):
        raise HTTPException(status_code=403, detail="Acesso negado")
    
    conn = sqlite3.connect(settings.DB_LOCAL_PATH)
    cursor = conn.cursor()
    
    # Verifica se a permissão já existe
    exists = cursor.execute(
        "SELECT 1 FROM user_dashboards WHERE user_id = ? AND dashboard_id = ?",
        (user_id, dashboard_id)
    ).fetchone()
    
    if exists:
        cursor.execute("DELETE FROM user_dashboards WHERE user_id = ? AND dashboard_id = ?", (user_id, dashboard_id))
        msg = "Permissão removida"
    else:
        cursor.execute("INSERT INTO user_dashboards (user_id, dashboard_id) VALUES (?, ?)", (user_id, dashboard_id))
        msg = "Permissão concedida"
        
    conn.commit()
    conn.close()
    return {"status": "success", "message": msg}
