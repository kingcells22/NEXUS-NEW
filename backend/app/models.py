from sqlalchemy import Column, String, Boolean, DateTime, Integer, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
from app.database import Base

# --- TABLAS INTERMEDIAS (Para relaciones muchos-a-muchos) ---
empleado_cargo = Table(
    'empleado_cargo', Base.metadata,
    Column('empleado_id', String, ForeignKey('empleados.id', ondelete="CASCADE"), primary_key=True),
    Column('cargo_id', Integer, ForeignKey('cargos.id', ondelete="CASCADE"), primary_key=True)
)

empleado_centro = Table(
    'empleado_centro', Base.metadata,
    Column('empleado_id', String, ForeignKey('empleados.id', ondelete="CASCADE"), primary_key=True),
    Column('centro_id', Integer, ForeignKey('centros.id', ondelete="CASCADE"), primary_key=True)
)

# --- MODELOS PRINCIPALES ---

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    correo = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    estado = Column(Boolean, default=True)
    rol = Column(String, default="USER") 
    
    # --- CAMPOS DE SEGURIDAD INSTITUCIONAL ---
    fecha_expiracion_clave = Column(DateTime, nullable=True) 
    pregunta_seguridad_1 = Column(String, nullable=True)     
    respuesta_seguridad_1 = Column(String, nullable=True)
    pregunta_seguridad_2 = Column(String, nullable=True)     
    respuesta_seguridad_2 = Column(String, nullable=True)
    # ------------------------------------------------

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relación 1 a 1: Un usuario es un empleado
    empleado = relationship("Empleado", back_populates="usuario", uselist=False)


class Cargo(Base):
    __tablename__ = "cargos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)
    
    empleados = relationship("Empleado", secondary=empleado_cargo, back_populates="cargos")


class Centro(Base):
    __tablename__ = "centros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String, unique=True, nullable=False)
    abreviatura = Column(String, unique=True, nullable=False)
    
    empleados = relationship("Empleado", secondary=empleado_centro, back_populates="centros")


class Empleado(Base):
    __tablename__ = "empleados"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    usuario_id = Column(String, ForeignKey("usuarios.id", ondelete="CASCADE"), unique=True) # Enlace al login
    cedula = Column(String, unique=True, nullable=False)
    nombres_apellidos = Column(String, nullable=False)
    fecha_ingreso = Column(DateTime, nullable=False)

    # --- NUEVO: FIRMA VISUAL (Soporta jpg, png, jpeg, img) ---
    firma_visual_url = Column(String(500), nullable=True)

    # Relaciones
    usuario = relationship("Usuario", back_populates="empleado")
    cargos = relationship("Cargo", secondary=empleado_cargo, back_populates="empleados")
    centros = relationship("Centro", secondary=empleado_centro, back_populates="empleados")


# --- MODELOS DE DOCUMENTOS Y ARCHIVOS ---

class ArchivoDocumento(Base):
    __tablename__ = "archivos_documento"

    id = Column(Integer, primary_key=True, autoincrement=True)
    url = Column(String(500), nullable=False) 
    tipo = Column(String(20), nullable=False)
    nombre = Column(String(100), nullable=False)
    documento_id = Column(Integer, nullable=False) 
    tipo_documento = Column(String(30), nullable=False) 
    firmado = Column(Boolean, default=False)
    firmado_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Memorandum(Base):
    __tablename__ = "memorandums"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_documento = Column(String(20), nullable=True)
    asunto = Column(String(255), nullable=False)
    fecha = Column(DateTime, nullable=False)
    descripcion = Column(String, nullable=False) 
    anexos = Column(Boolean, default=False)
    centro = Column(String(100), default="registro_anterior")

    # Claves Foráneas
    emisor_id = Column(String, ForeignKey("empleados.id", ondelete="RESTRICT"), nullable=False)
    receptor_id = Column(String, ForeignKey("empleados.id", ondelete="RESTRICT"), nullable=False)

    # --- CAMPOS MÁQUINA DE ESTADOS ---
    status = Column(String(50), default="CREADO") # CREADO, EN_REVISION, RECHAZADO, APROBADO
    autoridad_id = Column(String, ForeignKey("empleados.id", ondelete="RESTRICT"), nullable=True)
    observaciones_rechazo = Column(String, nullable=True)
    firma_emisor_url = Column(String(500), nullable=True)
    firma_autoridad_url = Column(String(500), nullable=True)
    # ---------------------------------

    # Relaciones
    emisor = relationship("Empleado", foreign_keys=[emisor_id])
    receptor = relationship("Empleado", foreign_keys=[receptor_id])
    autoridad = relationship("Empleado", foreign_keys=[autoridad_id])


class Oficio(Base):
    __tablename__ = "oficios"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_documento = Column(String(20), nullable=True)
    asunto = Column(String(255), nullable=False)
    fecha = Column(DateTime, nullable=False)
    descripcion = Column(String, nullable=False)
    anexos = Column(Boolean, default=False)
    centro = Column(String(100), default="registro_anterior")

    # Claves Foráneas
    emisor_id = Column(String, ForeignKey("empleados.id", ondelete="RESTRICT"), nullable=False)
    receptor_id = Column(String, ForeignKey("empleados.id", ondelete="RESTRICT"), nullable=False)

    # --- CAMPOS MÁQUINA DE ESTADOS ---
    status = Column(String(50), default="CREADO")
    autoridad_id = Column(String, ForeignKey("empleados.id", ondelete="RESTRICT"), nullable=True)
    observaciones_rechazo = Column(String, nullable=True)
    firma_emisor_url = Column(String(500), nullable=True)
    firma_autoridad_url = Column(String(500), nullable=True)
    # ---------------------------------

    # Relaciones
    emisor = relationship("Empleado", foreign_keys=[emisor_id])
    receptor = relationship("Empleado", foreign_keys=[receptor_id])
    autoridad = relationship("Empleado", foreign_keys=[autoridad_id])


# --- NUEVO: PUNTO DE CUENTA ---
class PuntoCuenta(Base):
    __tablename__ = "puntos_cuenta"

    id = Column(Integer, primary_key=True, autoincrement=True)
    numero_documento = Column(String(20), nullable=True)
    fecha = Column(DateTime, nullable=False)
    
    # Campos específicos del formato FIIIDT
    a_quien = Column(String(255), nullable=False)
    asunto = Column(String(255), nullable=False)
    sintesis = Column(String, nullable=False)
    presupuesto = Column(String(255), nullable=True)
    decision = Column(String(50), nullable=True) # APROBADO, NEGADO, VISTO, DIFERIDO, OTRO
    observaciones_presidente = Column(String, nullable=True)
    fecha_aprobacion = Column(DateTime, nullable=True)
    anexos = Column(Boolean, default=False)

    # Clave Foránea de quién lo elabora/presenta
    emisor_id = Column(String, ForeignKey("empleados.id", ondelete="RESTRICT"), nullable=False)
    
    # --- CAMPOS MÁQUINA DE ESTADOS ---
    status = Column(String(50), default="CREADO") 
    autoridad_id = Column(String, ForeignKey("empleados.id", ondelete="RESTRICT"), nullable=True)
    observaciones_rechazo = Column(String, nullable=True)
    firma_emisor_url = Column(String(500), nullable=True)
    firma_autoridad_url = Column(String(500), nullable=True)
    # ---------------------------------

    # Relaciones
    emisor = relationship("Empleado", foreign_keys=[emisor_id])
    autoridad = relationship("Empleado", foreign_keys=[autoridad_id])


# ==========================================
# NUEVO: PLANTILLAS PDF (100% DINÁMICO)
# ==========================================
class PlantillaPDF(Base):
    __tablename__ = "plantillas_pdf"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tipo_documento = Column(String(50), unique=True, index=True, nullable=False) 
    nombre_archivo = Column(String(100), nullable=False) 
    coordenadas = Column(JSON, nullable=False)