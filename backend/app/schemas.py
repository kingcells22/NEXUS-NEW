from pydantic import BaseModel, EmailStr, validator
from datetime import datetime
from typing import Optional, Dict, Any
import re

# ==========================================
# ESQUEMAS DE SEGURIDAD Y REGISTRO
# ==========================================
class UsuarioCrear(BaseModel):
    correo: EmailStr 
    password: str
    rol: str = "USER"

class RegistroCompletoCrear(BaseModel):
    correo: EmailStr
    password: str
    validez_dias: int
    pregunta_seguridad_1: str
    respuesta_seguridad_1: str
    pregunta_seguridad_2: str
    respuesta_seguridad_2: str
    cedula: str
    nombres_apellidos: str
    centro: str
    cargo: str

    @validator('password')
    def validar_password_fuerte(cls, value):
        patron = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[.\-*_$@!%&])[A-Za-z\d.\-*_$@!%&]{8,}$"
        if not re.match(patron, value):
            raise ValueError("CLAVE NO CUMPLE CON REQUISITOS, REINTENTE")
        return value

    @validator('validez_dias')
    def validar_dias(cls, value):
        if value not in [30, 60, 90, 180]:
            raise ValueError("Periodo de validez inválido.")
        return value


# ==========================================
# ESQUEMAS PARA RECUPERAR CONTRASEÑA
# ==========================================
class RecuperarClavePreguntas(BaseModel):
    correo: EmailStr

class RecuperarClavePreguntasRespuesta(BaseModel):
    pregunta_seguridad_1: str
    pregunta_seguridad_2: str

class RecuperarClaveReset(BaseModel):
    correo: EmailStr
    respuesta_seguridad_1: str
    respuesta_seguridad_2: str
    nueva_password: str
    validez_dias: int 

    @validator('nueva_password')
    def validar_nueva_clave_fuerte(cls, value):
        patron = r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[.\-*_$@!%&])[A-Za-z\d.\-*_$@!%&]{8,}$"
        if not re.match(patron, value):
            raise ValueError("LA NUEVA CLAVE NO CUMPLE CON REQUISITOS, REINTENTE")
        return value

    @validator('validez_dias')
    def validar_dias_reset(cls, value): 
        if value not in [30, 60, 90, 180]:
            raise ValueError("Periodo de validez inválido.")
        return value

class UsuarioRespuesta(BaseModel):
    id: str
    correo: str
    rol: str
    estado: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ==========================================
# ESQUEMAS DE EMPLEADOS
# ==========================================
class EmpleadoCrear(BaseModel):
    usuario_id: str 
    cedula: str
    nombres_apellidos: str
    fecha_ingreso: datetime

class EmpleadoRespuesta(BaseModel):
    id: str
    usuario_id: str
    cedula: str
    nombres_apellidos: str
    fecha_ingreso: datetime

    class Config:
        from_attributes = True


# ==========================================
# ESQUEMAS DE MÁQUINA DE ESTADOS (NUEVO)
# ==========================================
class DocumentoEstadoActualizar(BaseModel):
    status: str # Se enviará: EN_REVISION, RECHAZADO o APROBADO
    observaciones_rechazo: Optional[str] = None


# ==========================================
# ESQUEMAS DE MEMORÁNDUMS
# ==========================================
class MemorandumCrear(BaseModel):
    asunto: str
    descripcion: str
    emisor_id: str   
    receptor_id: str 
    autoridad_id: Optional[str] = None # A quién se le envía para revisar
    centro: Optional[str] = "Sede Principal"

class MemorandumRespuesta(BaseModel):
    id: int
    numero_documento: Optional[str]
    asunto: str
    fecha: datetime
    descripcion: str
    emisor_id: str
    receptor_id: str
    centro: str
    
    # --- Datos de Máquina de Estados ---
    status: str
    autoridad_id: Optional[str]
    observaciones_rechazo: Optional[str]
    firma_emisor_url: Optional[str]
    firma_autoridad_url: Optional[str]

    class Config:
        from_attributes = True

class MemorandumActualizar(BaseModel):
    asunto: Optional[str] = None
    descripcion: Optional[str] = None


# ==========================================
# ESQUEMAS DE PUNTOS DE CUENTA (NUEVO)
# ==========================================
class PuntoCuentaCrear(BaseModel):
    a_quien: str
    asunto: str
    sintesis: str
    presupuesto: Optional[str] = None
    emisor_id: str
    autoridad_id: Optional[str] = None

class PuntoCuentaRespuesta(BaseModel):
    id: int
    numero_documento: Optional[str]
    fecha: datetime
    a_quien: str
    asunto: str
    sintesis: str
    presupuesto: Optional[str]
    decision: Optional[str]
    observaciones_presidente: Optional[str]
    
    # --- Datos de Máquina de Estados ---
    emisor_id: str
    status: str
    autoridad_id: Optional[str]
    observaciones_rechazo: Optional[str]
    firma_emisor_url: Optional[str]
    firma_autoridad_url: Optional[str]

    class Config:
        from_attributes = True

# ==========================================
# ESQUEMAS DE PLANTILLAS PDF (100% DINÁMICO)
# ==========================================
class PlantillaPDFCrear(BaseModel):
    tipo_documento: str
    nombre_archivo: str
    coordenadas: Dict[str, Any] # Recibirá el JSON con los X, Y que el admin configure

class PlantillaPDFRespuesta(BaseModel):
    id: int
    tipo_documento: str
    nombre_archivo: str
    coordenadas: Dict[str, Any]

    class Config:
        from_attributes = True

        # ==========================================
# ESQUEMAS PARA MEMORÁNDUM
# ==========================================

class MemorandumCrear(BaseModel):
    asunto: str
    descripcion: str
    fecha: datetime
    receptor_id: str
    emisor_id: str
    anexos: Optional[bool] = False
    centro: Optional[str] = "Sede Principal" 

class MemorandumRespuesta(BaseModel):
    id: int
    numero_documento: Optional[str] = None
    asunto: str
    descripcion: str
    fecha: datetime
    emisor_id: str
    receptor_id: str
    status: str
    anexos: bool

    class Config:
        from_attributes = True

class PeticionRecuperacion(BaseModel):
    correo: str
    respuesta_seguridad_1: str
    respuesta_seguridad_2: str
    nueva_password: str
    validez_dias: int