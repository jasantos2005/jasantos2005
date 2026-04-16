from fastapi import Request, HTTPException, status
from jose import jwt, JWTError
from app.config import settings

async def login_required(request: Request):
    """
    Middleware de dependência para proteger rotas.
    Verifica o token JWT nos cookies.
    """
    token = request.cookies.get("axiom_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Acesso negado. Faça login para continuar."
        )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sessão inválida ou expirada."
        )
