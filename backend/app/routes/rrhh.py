from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime
from pydantic import BaseModel

from app.database import get_db
from app import models, schemas
from app.security import get_usuario_actual

# Aquí creamos el "Router" (La extensión eléctrica)
# Le decimos que TODAS estas rutas empezarán automáticamente con "/api/admin"
router = APIRouter(
    prefix="/api/admin",
    tags=["Recursos Humanos"]
)

@router.get("/usuarios")
def obtener_usuarios_admin(db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    """Devuelve la lista completa de empleados con sus cuentas de usuario para el panel de Gestión Humana"""
    if usuario_actual.get("rol") not in ["ADMIN USERS", "ADMIN GRAL", "ADMIN GLOBAL"]:
        raise HTTPException(status_code=403, detail="Acceso denegado. No tienes permisos de administrador.")

    empleados = db.query(models.Empleado).order_by(models.Empleado.nombres_apellidos.asc()).all()
    
    resultados = []
    for emp in empleados:
        user = db.query(models.Usuario).filter(models.Usuario.id == emp.usuario_id).first()
        resultados.append({
            "cedula": emp.cedula,
            "nombres_apellidos": emp.nombres_apellidos,
            "fecha_ingreso": emp.fecha_ingreso.strftime("%d/%m/%Y") if emp.fecha_ingreso else "N/A",
            "correo": user.correo if user else "Sin cuenta web",
            "estado": user.estado if user else False,
            "tiene_cuenta": bool(user)
        })
    return resultados

@router.put("/usuarios/{cedula}/deshabilitar")
def deshabilitar_usuario_admin(cedula: str, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    """Apaga el acceso al sistema de un usuario específico"""
    if usuario_actual.get("rol") not in ["ADMIN USERS", "ADMIN GRAL", "ADMIN GLOBAL"]:
        raise HTTPException(status_code=403, detail="Acceso denegado.")

    empleado = db.query(models.Empleado).filter(models.Empleado.cedula == cedula).first()
    if not empleado or not empleado.usuario_id:
        raise HTTPException(status_code=404, detail="El usuario no existe o no tiene cuenta web.")
        
    usuario = db.query(models.Usuario).filter(models.Usuario.id == empleado.usuario_id).first()
    usuario.estado = not usuario.estado 
    
    db.commit()
    accion = "habilitado" if usuario.estado else "deshabilitado"
    return {"mensaje": f"El usuario ha sido {accion} exitosamente."}


class EmpleadoRRHH(BaseModel):
    cedula: str
    nombres_apellidos: str
    fecha_ingreso: str
    cargo: str
    centro: str
    tipo_nomina: str
    genero: str      
    titulo: str      

@router.post("/empleados")
def registrar_empleado_nomina(datos: EmpleadoRRHH, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    """Ingresa un nuevo trabajador a la base de datos para que luego pueda reclamar su cuenta web"""
    if usuario_actual.get("rol") not in ["ADMIN USERS", "ADMIN GRAL", "ADMIN GLOBAL"]:
        raise HTTPException(status_code=403, detail="Acceso denegado. Solo Recursos Humanos puede ingresar personal.")

    if db.query(models.Empleado).filter(models.Empleado.cedula == datos.cedula).first():
        raise HTTPException(status_code=400, detail="Esta cédula ya está registrada en la nómina de la FIIIDT.")

    tipo_nom = db.query(models.TipoNomina).filter(models.TipoNomina.nombre == datos.tipo_nomina.upper()).first()
    if not tipo_nom:
        tipo_nom = models.TipoNomina(nombre=datos.tipo_nomina.upper())
        db.add(tipo_nom)
        db.flush()

    cargo_db = db.query(models.Cargo).filter(models.Cargo.nombre == datos.cargo.upper()).first()
    if not cargo_db:
        cargo_db = models.Cargo(nombre=datos.cargo.upper())
        db.add(cargo_db)
        db.flush()

    centro_db = db.query(models.Centro).filter(models.Centro.nombre == datos.centro.upper()).first()
    if not centro_db:
        centro_db = models.Centro(nombre=datos.centro.upper(), abreviatura=datos.centro.upper()[:15])
        db.add(centro_db)
        db.flush()

    try:
        fecha_obj = datetime.strptime(datos.fecha_ingreso, "%Y-%m-%d")
    except ValueError:
        fecha_obj = datetime.utcnow()

    nuevo_emp = models.Empleado(
        cedula=datos.cedula,
        nombres_apellidos=datos.nombres_apellidos.upper(),
        fecha_ingreso=fecha_obj,
        tipo_nomina_id=tipo_nom.id,
        genero=datos.genero.upper(),
        titulo=datos.titulo.upper()
    )
    nuevo_emp.cargos.append(cargo_db)
    nuevo_emp.centros.append(centro_db)

    db.add(nuevo_emp)
    db.commit()

    return {"mensaje": "Personal ingresado a nómina exitosamente. Ya puede registrar su cuenta web."}