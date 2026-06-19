from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from app.database import get_db
from app import models, schemas
from app.security import (
    verificar_password, encriptar_password, crear_token_acceso, 
    get_usuario_actual, asignar_rol_automatico, ACCESS_TOKEN_EXPIRE_MINUTES
)

# Creamos la "extensión" para las rutas de autenticación
router = APIRouter(
    prefix="/api",
    tags=["Autenticación y Cuentas"]
)

@router.post("/usuarios", response_model=schemas.UsuarioRespuesta)
def crear_usuario_completo(datos: schemas.RegistroCompletoCrear, db: Session = Depends(get_db)):
    if db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first():
        raise HTTPException(status_code=400, detail="Este correo ya está registrado en otra cuenta.")
        
    empleado_existente = db.query(models.Empleado).filter(models.Empleado.cedula == datos.cedula).first()
    if not empleado_existente:
        raise HTTPException(status_code=404, detail="No se encontró un empleado con esta cédula. Consulte con Recursos Humanos.")
        
    if empleado_existente.usuario_id is not None:
        raise HTTPException(status_code=400, detail="Este empleado ya tiene una cuenta de usuario asignada en NEXUS.")

    fecha_expiracion = datetime.utcnow() + timedelta(days=datos.validez_dias)
    rol_calculado = asignar_rol_automatico(correo=datos.correo, cargos=[datos.cargo], centros=[datos.centro])

    nuevo_usuario = models.Usuario(
        correo=datos.correo,
        password=encriptar_password(datos.password), 
        fecha_expiracion_clave=fecha_expiracion,
        pregunta_seguridad_1=datos.pregunta_seguridad_1,
        respuesta_seguridad_1=datos.respuesta_seguridad_1,
        pregunta_seguridad_2=datos.pregunta_seguridad_2,
        respuesta_seguridad_2=datos.respuesta_seguridad_2,
        rol=rol_calculado
    )
    
    db.add(nuevo_usuario)
    db.flush()
    empleado_existente.usuario_id = nuevo_usuario.id
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@router.post("/login")
def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == form_data.username).first()
    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
        
    if not getattr(usuario, 'estado', True):
        raise HTTPException(status_code=403, detail="Su usuario ha sido deshabilitado. Contacte a Gestión Humana.")

    token_jwt = crear_token_acceso(
        data={"sub": usuario.correo, "rol": usuario.rol}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token_jwt, "token_type": "bearer", "rol": usuario.rol}

@router.get("/me")
def obtener_perfil_actual(db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == usuario_actual["sub"]).first()
    empleado = db.query(models.Empleado).filter(models.Empleado.usuario_id == usuario.id).first()
    nombre_cargo = empleado.cargos[0].nombre if empleado.cargos else "Sin cargo"
    nombre_centro = empleado.centros[0].nombre if empleado.centros else "Sin centro"
    
    return {
        "usuario_id": usuario.id,
        "empleado_id": empleado.id,
        "correo": usuario.correo,
        "rol": usuario.rol,
        "cedula": empleado.cedula,
        "nombres_apellidos": empleado.nombres_apellidos,
        "cargo": nombre_cargo,
        "centro": nombre_centro
    }

@router.get("/usuarios/preguntas")
def obtener_preguntas_seguridad(correo: str, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="El correo electrónico no se encuentra registrado en el sistema.")
    return {
        "pregunta_seguridad_1": usuario.pregunta_seguridad_1,
        "pregunta_seguridad_2": usuario.pregunta_seguridad_2
    }

@router.post("/usuarios/recuperar-clave")
def procesar_recuperacion_clave(datos: schemas.PeticionRecuperacion, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    resp1_db = usuario.respuesta_seguridad_1.strip().lower()
    resp1_user = datos.respuesta_seguridad_1.strip().lower()
    resp2_db = usuario.respuesta_seguridad_2.strip().lower()
    resp2_user = datos.respuesta_seguridad_2.strip().lower()

    if resp1_db != resp1_user or resp2_db != resp2_user:
        raise HTTPException(status_code=400, detail="Las respuestas de seguridad ingresadas no coinciden con nuestros registros.")

    usuario.password = encriptar_password(datos.nueva_password)
    usuario.fecha_expiracion_clave = datetime.utcnow() + timedelta(days=datos.validez_dias)
    
    db.commit()
    return {"mensaje": "Credenciales actualizadas exitosamente."}