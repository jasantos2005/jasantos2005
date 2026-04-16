import sqlite3
import os
import bcrypt
from fastapi import APIRouter, Form, Response, HTTPException, status
from fastapi.responses import RedirectResponse
from jose import jwt
from datetime import datetime, timedelta

SECRET_KEY = "AXIOM_SUPER_SECRET_KEY"
ALGORITHM = "HS256"
DB_PATH = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/core/axiom_auth.db"

router = APIRouter(prefix="/auth", tags=["auth"])

def get_db_row(query, params=()):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute(query, params).fetchone()
    conn.close()
    return row

@router.post("/login")
async def login(response: Response, username: str = Form(...), password: str = Form(...)):
    user = get_db_row("SELECT * FROM users WHERE username = ?", (username,))
    
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user["password_hash"].encode('utf-8')):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    expire = datetime.utcnow() + timedelta(hours=8)
    token = jwt.encode({"sub": user["username"], "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)

    response.set_cookie(key="axiom_token", value=token, httponly=True, path="/")
    return {"status": "success", "redirect": "/dashboard/index"}

@router.get("/logout")
async def logout_router():
    response = RedirectResponse(url="/", status_code=303)
    response.delete_cookie(key="axiom_token", path="/")
    return response
