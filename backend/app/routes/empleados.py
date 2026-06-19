from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models

router = APIRouter(
    prefix="/api/empleados",
    tags=["Búsqueda de Empleados"]
)

@router.get("/")
def obtener_lista_empleados(db: Session = Depends(get_db)):
    """Devuelve la lista real de empleados ordenada alfabéticamente"""
    empleados = db.query(models.Empleado).order_by(models.Empleado.nombres_apellidos.asc()).all()
    return [{"id": emp.id, "nombre": emp.nombres_apellidos, "cedula": emp.cedula} for emp in empleados]

@router.get("/buscar/{cedula}")
def buscar_empleado_por_cedula(cedula: str, db: Session = Depends(get_db)):
    """Busca un empleado pre-cargado por el seed para que reclame su cuenta"""
    empleado = db.query(models.Empleado).filter(models.Empleado.cedula == cedula).first()
    
    if not empleado:
        raise HTTPException(status_code=404, detail="Cédula no encontrada en la base de datos del personal.")
        
    if empleado.usuario_id is not None:
        raise HTTPException(status_code=400, detail="Este empleado ya tiene un usuario registrado en NEXUS.")

    return {
        "cedula": empleado.cedula,
        "nombres_apellidos": empleado.nombres_apellidos,
        "cargo": empleado.cargos[0].nombre if empleado.cargos else "Sin cargo asignado",
        "centro": empleado.centros[0].nombre if empleado.centros else "Sin centro asignado"
    }