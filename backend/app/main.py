from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi.responses import Response
from pydantic import BaseModel
import io
import os
import shutil
import jwt 
import bcrypt 
import base64

# --- NUEVAS LIBRERÍAS PARA PDF (MÉTODO DE SUPERPOSICIÓN) ---
import io
import textwrap
from pypdf import PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib.utils import simpleSplit
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from app.database import engine, Base, get_db
from app import models, schemas

# 1. Inicialización y creación de tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus API Refactorizada")

# Esto es lo que le abre la puerta al frontend de Vue
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], # Tu frontend
    allow_credentials=True,
    allow_methods=["*"], # Permite GET, POST, OPTIONS, etc.
    allow_headers=["*"],
)

# --- CONFIGURACIÓN DE SEGURIDAD JWT ---
SECRET_KEY = "NEXUS_FIIIDT_SUPER_SECRETO_2026!" 
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login")

def verificar_password(plain_password, hashed_password):
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def encriptar_password(password):
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
# MOTOR DE ROLES (RBAC) - INYECTADO AQUÍ
# ==========================================
def asignar_rol_automatico(correo: str, cargos: list, centros: list) -> str:
    """Evalúa los parámetros del empleado y retorna su Rol en NEXUS"""
    correo_lower = correo.strip().lower()
    cargos_upper = [c.strip().upper() for c in cargos]
    centros_upper = [c.strip().upper() for c in centros]
    
    # 1. El Dios del Sistema
    if correo_lower == "admin@nexus.gob.ve":
        return "ADMIN GLOBAL"
        
    # 2. El Presidente
    if "PRESIDENTE" in cargos_upper:
        return "ADMIN GRAL"
        
    # 3. Gestión Humana (Maneja usuarios)
    if "OFICINA DE GESTIÓN HUMANA" in centros_upper or "OGH" in centros_upper:
        return "ADMIN USERS"
        
    # 4. Jefes, Coordinadores y Directores
    cargos_jefatura = [
        "JEFE DE CENTRO", "DIRECTOR TÉCNICO", "COORDINADOR", 
        "GERENTE", "CONSULTORA JURÍDICA", "AUDITORA INTERNA"
    ]
    if any(cargo in cargos_jefatura for cargo in cargos_upper):
        return "USER JEFE"
        
    # 5. Resto del personal
    return "USER NORMAL"
# ==========================================


UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# --- CONFIGURACIÓN DE DIRECTORIOS ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# -----------------------------------------------------------

@app.get("/")
def read_root():
    return {"mensaje": "¡El backend de Nexus está corriendo al 100%!"}

# ==========================================
# MÓDULO DE USUARIOS, RECUPERACIÓN Y PERFIL
# ==========================================

@app.post("/api/usuarios", response_model=schemas.UsuarioRespuesta)
def crear_usuario_completo(datos: schemas.RegistroCompletoCrear, db: Session = Depends(get_db)):
    
    # 1. Verificar si el correo ya lo está usando alguien más
    if db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first():
        raise HTTPException(status_code=400, detail="Este correo ya está registrado en otra cuenta.")
        
    # 2. Buscar al empleado pre-existente (inyectado por el seed)
    empleado_existente = db.query(models.Empleado).filter(models.Empleado.cedula == datos.cedula).first()
    if not empleado_existente:
        raise HTTPException(status_code=404, detail="No se encontró un empleado con esta cédula. Consulte con Recursos Humanos.")
        
    # 3. Verificar si este empleado ya reclamó su cuenta web
    if empleado_existente.usuario_id is not None:
        raise HTTPException(status_code=400, detail="Este empleado ya tiene una cuenta de usuario asignada en NEXUS.")

    fecha_expiracion = datetime.utcnow() + timedelta(days=datos.validez_dias)

    # --- ASIGNACIÓN DE ROL AUTOMÁTICO ---
    rol_calculado = asignar_rol_automatico(
        correo=datos.correo, 
        cargos=[datos.cargo], 
        centros=[datos.centro]
    )

    # 4. Crear las credenciales web (El objeto Usuario)
    nuevo_usuario = models.Usuario(
        correo=datos.correo,
        password=encriptar_password(datos.password), 
        fecha_expiracion_clave=fecha_expiracion,
        pregunta_seguridad_1=datos.pregunta_seguridad_1,
        respuesta_seguridad_1=datos.respuesta_seguridad_1,
        pregunta_seguridad_2=datos.pregunta_seguridad_2,
        respuesta_seguridad_2=datos.respuesta_seguridad_2,
        rol=rol_calculado # <--- EL SISTEMA LE ASIGNA EL ROL EXACTO AQUÍ
    )
    
    db.add(nuevo_usuario)
    db.flush() # Guardamos temporalmente para que PostgreSQL le genere su UUID

    # 5. ¡LA MAGIA RELACIONAL! Enlazamos el usuario web con el perfil de RRHH
    empleado_existente.usuario_id = nuevo_usuario.id
    
    db.commit()
    db.refresh(nuevo_usuario)
    
    return nuevo_usuario

@app.post("/api/login")
def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == form_data.username).first()
    # Verifica credenciales y también que el usuario no esté deshabilitado (is_active / estado)
    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
        
    if not getattr(usuario, 'estado', True): # Si el estado es False (Deshabilitado)
        raise HTTPException(status_code=403, detail="Su usuario ha sido deshabilitado. Contacte a Gestión Humana.")

    token_jwt = crear_token_acceso(
        data={"sub": usuario.correo, "rol": usuario.rol}, 
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": token_jwt, "token_type": "bearer", "rol": usuario.rol}

@app.get("/api/me")
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

@app.get("/api/usuarios/preguntas")
def obtener_preguntas_seguridad(correo: str, db: Session = Depends(get_db)):
    """Busca al usuario por correo y devuelve sus preguntas de seguridad institucionales."""
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == correo).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="El correo electrónico no se encuentra registrado en el sistema.")
        
    return {
        "pregunta_seguridad_1": usuario.pregunta_seguridad_1,
        "pregunta_seguridad_2": usuario.pregunta_seguridad_2
    }

@app.post("/api/usuarios/recuperar-clave")
def procesar_recuperacion_clave(datos: schemas.PeticionRecuperacion, db: Session = Depends(get_db)):
    """Valida las respuestas de seguridad y actualiza las credenciales del usuario."""
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first()
    
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado.")

    # Validación estricta de respuestas (insensible a mayúsculas/espacios para evitar bloqueos innecesarios)
    resp1_db = usuario.respuesta_seguridad_1.strip().lower()
    resp1_user = datos.respuesta_seguridad_1.strip().lower()
    
    resp2_db = usuario.respuesta_seguridad_2.strip().lower()
    resp2_user = datos.respuesta_seguridad_2.strip().lower()

    if resp1_db != resp1_user or resp2_db != resp2_user:
        raise HTTPException(status_code=400, detail="Las respuestas de seguridad ingresadas no coinciden con nuestros registros.")

    # Actualización de credenciales y periodo de validez
    usuario.password = encriptar_password(datos.nueva_password)
    usuario.fecha_expiracion_clave = datetime.utcnow() + timedelta(days=datos.validez_dias)
    
    db.commit()
    return {"mensaje": "Credenciales actualizadas exitosamente."}

# ==========================================
# RUTAS DE EMPLEADOS
# ==========================================
@app.get("/api/empleados")
def obtener_lista_empleados(db: Session = Depends(get_db)):
    """Devuelve la lista real de empleados ordenada alfabéticamente"""
    # Ordenamos alfabéticamente de la A a la Z
    empleados = db.query(models.Empleado).order_by(models.Empleado.nombres_apellidos.asc()).all()
    return [
        {
            "id": emp.id, 
            "nombre": emp.nombres_apellidos, 
            "cedula": emp.cedula
        } 
        for emp in empleados
    ]

@app.get("/api/empleados/buscar/{cedula}")
def buscar_empleado_por_cedula(cedula: str, db: Session = Depends(get_db)):
    """Busca un empleado pre-cargado por el seed para que reclame su cuenta"""
    empleado = db.query(models.Empleado).filter(models.Empleado.cedula == cedula).first()
    
    if not empleado:
        raise HTTPException(status_code=404, detail="Cédula no encontrada en la base de datos del personal.")
        
    if empleado.usuario_id is not None:
        raise HTTPException(status_code=400, detail="Este empleado ya tiene un usuario registrado en NEXUS.")

    # Retornamos los datos para auto-llenar el formulario de Vue
    return {
        "cedula": empleado.cedula,
        "nombres_apellidos": empleado.nombres_apellidos,
        "cargo": empleado.cargos[0].nombre if empleado.cargos else "Sin cargo asignado",
        "centro": empleado.centros[0].nombre if empleado.centros else "Sin centro asignado"
    }


# ==========================================
# RUTAS PARA DOCUMENTOS (Concurrencia y Correlativos)
# ==========================================
@app.post("/api/memorandums", response_model=schemas.MemorandumRespuesta)
def crear_memorandum_real(memo: schemas.MemorandumCrear, db: Session = Depends(get_db)):
    año_actual = datetime.utcnow().year

    emisor = db.query(models.Empleado).options(joinedload(models.Empleado.centros)).filter(models.Empleado.id == memo.emisor_id).first()
    
    if not emisor:
        raise HTTPException(status_code=404, detail="El empleado emisor no existe en la base de datos.")

    abreviatura_centro = emisor.centros[0].abreviatura if emisor.centros else "FIIIDT"

    prefijo = f"{abreviatura_centro}-{año_actual}-"
    
    ultimo_memo = db.query(models.Memorandum).filter(
        models.Memorandum.numero_documento.like(f"{prefijo}%")
    ).order_by(models.Memorandum.id.desc()).with_for_update().first()

    if ultimo_memo and ultimo_memo.numero_documento:
        try:
            correlativo_actual = int(ultimo_memo.numero_documento.split('-')[-1])
            nuevo_correlativo = correlativo_actual + 1
        except ValueError:
            nuevo_correlativo = 1
    else:
        nuevo_correlativo = 1

    numero_generado = f"{prefijo}{nuevo_correlativo:03d}"

    nuevo_memo = models.Memorandum(
        numero_documento=numero_generado,
        asunto=memo.asunto,
        descripcion=memo.descripcion,
        fecha=memo.fecha,
        emisor_id=memo.emisor_id,
        receptor_id=memo.receptor_id,
        anexos=memo.anexos,
        centro=emisor.centros[0].nombre if emisor.centros else "Sede Principal",
        status="CREADO" 
    )
    
    db.add(nuevo_memo)
    db.commit()
    db.refresh(nuevo_memo)
    
    return nuevo_memo

@app.get("/api/memorandums/emitidos")
def obtener_memos_emitidos(db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    """Busca todos los memorándums emitidos por el usuario que inició sesión"""
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == usuario_actual["sub"]).first()
    empleado = db.query(models.Empleado).filter(models.Empleado.usuario_id == usuario.id).first()
    
    if not empleado:
        raise HTTPException(status_code=404, detail="Perfil de empleado no encontrado.")

    # Buscamos los memos donde el emisor sea el usuario actual, ordenados del más nuevo al más viejo
    memos = db.query(models.Memorandum).filter(models.Memorandum.emisor_id == empleado.id).order_by(models.Memorandum.id.desc()).all()
    
    resultados = []
    for m in memos:
        resultados.append({
            "id": m.id,
            "correlativo": m.numero_documento,
            "presentador": empleado.nombres_apellidos,
            "cargo_presentador": empleado.cargos[0].nombre if empleado.cargos else "Sin cargo",
            "asunto": m.asunto,
            "decision": m.status,
            "fecha": m.fecha.strftime("%d/%m/%Y"),
            "anexos": m.anexos
        })
    return resultados

@app.get("/api/memorandums/{memo_id}/pdf")
def generar_pdf_memorandum(memo_id: int, db: Session = Depends(get_db)):
    """Genera el PDF con salto de página automático, encabezados, pie de página y metadatos"""
    
    # 1. Buscar los datos en PostgreSQL
    memo = db.query(models.Memorandum).filter(models.Memorandum.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="Memorándum no encontrado.")
        
    emisor = db.query(models.Empleado).filter(models.Empleado.id == memo.emisor_id).first()
    receptor = db.query(models.Empleado).filter(models.Empleado.id == memo.receptor_id).first()

    emisor_cargo = emisor.cargos[0].nombre if emisor.cargos else "Sin cargo"
    receptor_cargo = receptor.cargos[0].nombre if receptor.cargos else "Sin cargo"

    buffer = io.BytesIO()

    # 2. Configurar el Documento Inteligente
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=letter,
        rightMargin=50, 
        leftMargin=50, 
        topMargin=110, 
        bottomMargin=115, 
        title=f"Memorándum {memo.numero_documento}", 
        author=emisor.nombres_apellidos
    )

    # 3. Función que inyecta las imágenes de fondo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    cintillo_path = os.path.join(base_dir, "templates_pdf", "cintillo.png")
    
    pie_opcion_1 = os.path.join(base_dir, "templates_pdf", "pie_pagina.png")
    pie_opcion_2 = os.path.join(base_dir, "templates_pdf", "pie_de_pagina.png")
    pie_path = pie_opcion_2 if os.path.exists(pie_opcion_2) else pie_opcion_1

    def dibujar_fondos(canvas, doc):
        canvas.saveState()
        # Dibujar Cintillo arriba
        if os.path.exists(cintillo_path):
            canvas.drawImage(cintillo_path, 0, 792 - 90, width=612, height=90)
            
        # Dibujar Pie de Página abajo
        if os.path.exists(pie_path):
            canvas.drawImage(pie_path, 0, 0, width=612, height=115) 
        canvas.restoreState()

    # 4. Construir la "Historia"
    Story = []
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER)
    estilo_correlativo = ParagraphStyle('Correlativo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, alignment=TA_RIGHT)
    estilo_negrita = ParagraphStyle('Negrita', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
    estilo_normal = ParagraphStyle('Texto', parent=styles['Normal'], fontName='Helvetica', fontSize=11)
    estilo_cuerpo = ParagraphStyle('Cuerpo', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=15, alignment=TA_JUSTIFY)

    # --- A. TÍTULO Y CORRELATIVO ---
    data_cabecera = [
        ["", Paragraph("MEMORÁNDUM", estilo_titulo), Paragraph(str(memo.numero_documento), estilo_correlativo)]
    ]
    t_cabecera = Table(data_cabecera, colWidths=[100, 312, 100])
    Story.append(t_cabecera)
    Story.append(Spacer(1, 15))

    # --- B. BLOQUE DE CABECERAS ---
    data_info = [
        [Paragraph("PARA:", estilo_negrita), Paragraph(f"{receptor.nombres_apellidos} - {receptor_cargo}", estilo_normal)],
        [Paragraph("DE:", estilo_negrita), Paragraph(f"{emisor.nombres_apellidos} - {emisor_cargo}", estilo_normal)],
        [Paragraph("FECHA:", estilo_negrita), Paragraph(f"{memo.fecha.strftime('%d/%m/%Y')}", estilo_normal)],
        [Paragraph("ASUNTO:", estilo_negrita), Paragraph(f"{memo.asunto}", estilo_normal)]
    ]

    t_info = Table(data_info, colWidths=[70, 442])
    t_info.setStyle(TableStyle([
        ('LINEABOVE', (0,0), (-1,0), 2, colors.HexColor('#cc0000')),
        ('LINEBELOW', (0,-1), (-1,-1), 2, colors.HexColor('#cc0000')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 8),
        ('TOPPADDING', (0,0), (-1,-1), 8),
    ]))
    Story.append(t_info)
    Story.append(Spacer(1, 20))

    # --- C. DESCRIPCIÓN ---
    parrafos_brutos = memo.descripcion.split('\n')
    for p in parrafos_brutos:
        if p.strip():
            texto_formateado = f'<p align="justify">{p.strip()}</p>'
            Story.append(Paragraph(texto_formateado, estilo_cuerpo))
            Story.append(Spacer(1, 8))

    # 5. Generar el PDF final
    doc.build(Story, onFirstPage=dibujar_fondos, onLaterPages=dibujar_fondos)

    buffer.seek(0)
    
    # 6. Cabecera limpia y estricta para abrir en el navegador
    headers = {
        "Content-Disposition": "inline"
    }
    
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers=headers)

@app.post("/api/puntos-cuenta", response_model=schemas.PuntoCuentaRespuesta)
def crear_punto_cuenta(punto: schemas.PuntoCuentaCrear, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    nuevo_punto = models.PuntoCuenta(
        a_quien=punto.a_quien,
        asunto=punto.asunto,
        sintesis=punto.sintesis,
        presupuesto=punto.presupuesto,
        emisor_id=punto.emisor_id,
        autoridad_id=punto.autoridad_id,
        fecha=datetime.now(),
        status="CREADO"
    )
    db.add(nuevo_punto)
    db.commit()
    db.refresh(nuevo_punto)
    nuevo_punto.numero_documento = f"PUNTO-2026-{nuevo_punto.id}"
    db.commit()
    return nuevo_punto

@app.put("/api/documentos/{tipo_documento}/{doc_id}/estatus")
def cambiar_estatus_documento(tipo_documento: str, doc_id: int, datos: schemas.DocumentoEstadoActualizar, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    tipo = tipo_documento.strip().lower()
    if tipo == "memorandum": modelo = models.Memorandum
    elif tipo == "oficio": modelo = models.Oficio
    elif tipo == "punto_cuenta": modelo = models.PuntoCuenta
    else: raise HTTPException(status_code=400, detail="Tipo de documento inválido.")
    documento = db.query(modelo).filter(modelo.id == doc_id).first()
    if not documento: raise HTTPException(status_code=404, detail="Documento no encontrado.")
    documento.status = datos.status.strip().upper()
    if documento.status == "RECHAZADO" and datos.observaciones_rechazo:
        documento.observaciones_rechazo = datos.observaciones_rechazo
    elif documento.status == "APROBADO":
        documento.observaciones_rechazo = None 
    db.commit()
    return {"mensaje": f"El documento pasó a estatus: {documento.status}"}

@app.get("/api/bandeja/pendientes")
def obtener_bandeja_pendientes(db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == usuario_actual["sub"]).first()
    empleado = db.query(models.Empleado).filter(models.Empleado.usuario_id == usuario.id).first()
    if not empleado: raise HTTPException(status_code=404, detail="Perfil de empleado no encontrado.")
    estatus_pendientes = ["CREADO", "EN_REVISION"]
    memos = db.query(models.Memorandum).filter(models.Memorandum.autoridad_id == empleado.id, models.Memorandum.status.in_(estatus_pendientes)).all()
    puntos = db.query(models.PuntoCuenta).filter(models.PuntoCuenta.autoridad_id == empleado.id, models.PuntoCuenta.status.in_(estatus_pendientes)).all()
    return {"memorandums": memos, "puntos_cuenta": puntos, "total_pendientes": len(memos) + len(puntos)}

# ==========================================
# MOTOR UNIVERSAL DE GENERACIÓN DE PDFs (100% DINÁMICO)
# ==========================================
@app.get("/api/documentos/{tipo_documento}/{doc_id}/generar-pdf")
def generar_pdf_universal(tipo_documento: str, doc_id: int, db: Session = Depends(get_db)):
    tipo = tipo_documento.strip().lower()
    
    # 1. BUSCAR CONFIGURACIÓN EN LA BASE DE DATOS (Cero Hardcode)
    config_plantilla = db.query(models.PlantillaPDF).filter(models.PlantillaPDF.tipo_documento == tipo).first()
    
    if not config_plantilla:
        raise HTTPException(
            status_code=404, 
            detail=f"El documento '{tipo}' aún no tiene una plantilla ni coordenadas configuradas en el sistema."
        )
        
    mapa_coordenadas = config_plantilla.coordenadas # Esto extrae el JSON de la BD
    
    # 2. BUSCAR EL DOCUMENTO EN LA BASE DE DATOS
    datos_extraidos = {}
    if tipo == "memorandum":
        doc = db.query(models.Memorandum).filter(models.Memorandum.id == doc_id).first()
        if not doc: raise HTTPException(status_code=404, detail="Memorándum no encontrado")
        datos_extraidos = {
            "receptor": doc.receptor.nombres_apellidos,
            "emisor": doc.emisor.nombres_apellidos,
            "fecha": doc.fecha.strftime("%d/%m/%Y"),
            "asunto": doc.asunto,
            "correlativo": doc.numero_documento,
            "texto_largo": doc.descripcion
        }
        
    elif tipo == "punto_cuenta":
        doc = db.query(models.PuntoCuenta).filter(models.PuntoCuenta.id == doc_id).first()
        if not doc: raise HTTPException(status_code=404, detail="Punto de Cuenta no encontrado")
        datos_extraidos = {
            "receptor": doc.a_quien,
            "emisor": doc.emisor.nombres_apellidos,
            "fecha": doc.fecha.strftime("%d/%m/%Y"),
            "asunto": doc.asunto,
            "correlativo": doc.numero_documento,
            "texto_largo": doc.sintesis
        }
    else:
        raise HTTPException(status_code=400, detail="Estructura de datos no definida para este tipo de documento.")

    # 3. DIBUJAR LA CAPA DE TEXTO LEYENDO LA BASE DE DATOS
    packet = io.BytesIO()
    can = canvas.Canvas(packet, pagesize=letter)
    can.setFont("Helvetica", 11)

    # El ciclo lee el JSON de la BD: ej. {"receptor": {"x": 130, "y": 610, "align": "L"}}
    textos_cortos = mapa_coordenadas.get("textos", {})
    for clave_campo, reglas in textos_cortos.items():
        texto_a_dibujar = datos_extraidos.get(clave_campo, "")
        if texto_a_dibujar:
            if reglas.get("align") == "C":
                can.drawCentredString(reglas["x"], reglas["y"], str(texto_a_dibujar))
            else:
                can.drawString(reglas["x"], reglas["y"], str(texto_a_dibujar))

    # Párrafo largo
    cfg_parrafo = mapa_coordenadas.get("parrafo")
    if cfg_parrafo and datos_extraidos.get("texto_largo"):
        textobject = can.beginText(cfg_parrafo["x"], cfg_parrafo["y"])
        textobject.setFont("Helvetica", 11)
        lineas = textwrap.wrap(datos_extraidos["texto_largo"], width=cfg_parrafo.get("width", 90))
        for linea in lineas:
            textobject.textLine(linea)
        can.drawText(textobject)

    can.save()
    packet.seek(0)
    nuevo_pdf_datos = PdfReader(packet)

    # 4. CARGAR LA PLANTILLA FÍSICA DESDE LA RUTA GUARDADA EN LA BD
    ruta_plantilla = os.path.join(BASE_DIR, "templates_pdf", config_plantilla.nombre_archivo)
    if not os.path.exists(ruta_plantilla):
        raise HTTPException(status_code=500, detail=f"Falta el archivo físico: {config_plantilla.nombre_archivo}")
        
    plantilla_pdf = PdfReader(open(ruta_plantilla, "rb"))
    output = PdfWriter()

    pagina_base = plantilla_pdf.pages[0]
    pagina_base.merge_page(nuevo_pdf_datos.pages[0])
    output.add_page(pagina_base)

    # 5. GUARDAR Y ENTREGAR EL PDF
    pdf_filename = f"{doc.numero_documento}.pdf"
    pdf_path = os.path.join(UPLOAD_DIR, pdf_filename)
    
    with open(pdf_path, "wb") as f:
        output.write(f)

    return FileResponse(path=pdf_path, filename=pdf_filename, media_type='application/pdf')

    # ==========================================
# MÓDULO DE ADMINISTRACIÓN DE USUARIOS
# ==========================================
@app.get("/api/admin/usuarios")
def obtener_usuarios_admin(db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    """Devuelve la lista completa de empleados con sus cuentas de usuario para el panel de Gestión Humana"""
    
    # Seguridad: Solo los roles de administrador pueden ver esta lista
    if usuario_actual.get("rol") not in ["ADMIN USERS", "ADMIN GRAL", "ADMIN GLOBAL"]:
        raise HTTPException(status_code=403, detail="Acceso denegado. No tienes permisos de administrador.")

    empleados = db.query(models.Empleado).order_by(models.Empleado.nombres_apellidos.asc()).all()
    
    resultados = []
    for emp in empleados:
        # Buscamos si el empleado ya reclamó su cuenta web
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

@app.put("/api/admin/usuarios/{cedula}/deshabilitar")
def deshabilitar_usuario_admin(cedula: str, db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    """Apaga el acceso al sistema de un usuario específico"""
    
    if usuario_actual.get("rol") not in ["ADMIN USERS", "ADMIN GRAL", "ADMIN GLOBAL"]:
        raise HTTPException(status_code=403, detail="Acceso denegado.")

    empleado = db.query(models.Empleado).filter(models.Empleado.cedula == cedula).first()
    if not empleado or not empleado.usuario_id:
        raise HTTPException(status_code=404, detail="El usuario no existe o no tiene cuenta web.")
        
    usuario = db.query(models.Usuario).filter(models.Usuario.id == empleado.usuario_id).first()
    
    # Invertimos el estado (Si está activo lo apaga, si está apagado lo prende)
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
    genero: str      # <--- NUEVO
    titulo: str      # <--- NUEVO

@app.post("/api/admin/empleados")
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

    # === INYECTAMOS GÉNERO Y TÍTULO AL CREARLO ===
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