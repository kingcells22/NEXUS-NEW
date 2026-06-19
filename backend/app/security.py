from fastapi import HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from datetime import datetime, timedelta
import jwt
import bcrypt

# --- CONFIGURACIÓN DE SEGURIDAD JWT ---
SECRET_KEY = "NEXUS_FIIIDT_SUPER_SECRETO_2026!" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verificar_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def encriptar_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8') 

def crear_token_acceso(data: dict, expires_delta: timedelta):
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_usuario_actual(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        correo: str = payload.get("sub")
        if correo is None:
            raise HTTPException(status_code=401, detail="Token inválido.")
        return payload 
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="El token ya expiró. Vuelve a iniciar sesión.")
    except jwt.PyJWTError: 
        raise HTTPException(status_code=401, detail="No tienes permiso para entrar aquí, acceso denegado.")

# ==========================================
# MOTOR DE ROLES (RBAC)
# ==========================================
def asignar_rol_automatico(correo: str, cargos: list, centros: list) -> str:
    """Evalúa los parámetros del empleado y retorna su Rol en NEXUS"""
    correo_lower = correo.strip().lower()
    cargos_upper = [c.strip().upper() for c in cargos]
    centros_upper = [c.strip().upper() for c in centros]
    
    if correo_lower == "admin@nexus.gob.ve": return "ADMIN GLOBAL"
    if "PRESIDENTE" in cargos_upper: return "ADMIN GRAL"
    if "OFICINA DE GESTIÓN HUMANA" in centros_upper or "OGH" in centros_upper: return "ADMIN USERS"
        
    cargos_jefatura = ["JEFE DE CENTRO", "DIRECTOR TÉCNICO", "COORDINADOR", "GERENTE", "CONSULTORA JURÍDICA", "AUDITORA INTERNA"]
    if any(cargo in cargos_jefatura for cargo in cargos_upper): return "USER JEFE"
        
    return "USER NORMAL"