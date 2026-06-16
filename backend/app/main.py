from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, File, UploadFile, HTTPException, Depends, Form
from typing import List, Optional
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import func
from datetime import datetime, timedelta
from fastapi.responses import Response
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
from reportlab.pdfgen import canvas
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
SECRET_KEY = "NEXUS_FIIIDT_SUPER_SECRETO_2026" 
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
    if db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first():
        raise HTTPException(status_code=400, detail="Este correo ya está registrado.")
    if db.query(models.Empleado).filter(models.Empleado.cedula == datos.cedula).first():
        raise HTTPException(status_code=400, detail="Esta cédula ya está registrada.")

    fecha_expiracion = datetime.utcnow() + timedelta(days=datos.validez_dias)

    nuevo_usuario = models.Usuario(
        correo=datos.correo,
        password=encriptar_password(datos.password), 
        fecha_expiracion_clave=fecha_expiracion,
        pregunta_seguridad_1=datos.pregunta_seguridad_1,
        respuesta_seguridad_1=datos.respuesta_seguridad_1,
        pregunta_seguridad_2=datos.pregunta_seguridad_2,
        respuesta_seguridad_2=datos.respuesta_seguridad_2,
        rol="USER"
    )
    db.add(nuevo_usuario)
    db.flush() 

    centro_limpio = datos.centro.strip().upper()
    centro_db = db.query(models.Centro).filter(models.Centro.nombre == centro_limpio).first()
    if not centro_db:
        centro_db = models.Centro(nombre=centro_limpio, abreviatura=centro_limpio)
        db.add(centro_db)
        db.flush()

    cargo_limpio = datos.cargo.strip().upper()
    cargo_db = db.query(models.Cargo).filter(models.Cargo.nombre == cargo_limpio).first()
    if not cargo_db:
        cargo_db = models.Cargo(nombre=cargo_limpio)
        db.add(cargo_db)
        db.flush()

    nuevo_empleado = models.Empleado(
        usuario_id=nuevo_usuario.id,
        cedula=datos.cedula,
        nombres_apellidos=datos.nombres_apellidos,
        fecha_ingreso=datetime.utcnow() 
    )
    nuevo_empleado.centros.append(centro_db)
    nuevo_empleado.cargos.append(cargo_db)
    db.add(nuevo_empleado)
    
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario

@app.post("/api/login")
def iniciar_sesion(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == form_data.username).first()
    if not usuario or not verificar_password(form_data.password, usuario.password):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")

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
    """Devuelve la lista real de empleados con cédula para el Frontend"""
    empleados = db.query(models.Empleado).all()
    return [
        {
            "id": emp.id, 
            "nombre": emp.nombres_apellidos, 
            "cedula": emp.cedula # Agregamos la cédula aquí
        } 
        for emp in empleados
    ]


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
    """Genera el PDF fusionando la data con la plantilla PDF oficial"""
    
    # 1. Buscar el documento y sus actores
    memo = db.query(models.Memorandum).filter(models.Memorandum.id == memo_id).first()
    if not memo:
        raise HTTPException(status_code=404, detail="Memorándum no encontrado.")
        
    emisor = db.query(models.Empleado).filter(models.Empleado.id == memo.emisor_id).first()
    receptor = db.query(models.Empleado).filter(models.Empleado.id == memo.receptor_id).first()

    # 2. Crear la capa transparente SOLO con el texto dinámico (ReportLab)
    capa_texto = io.BytesIO()
    c = canvas.Canvas(capa_texto, pagesize=letter)
    
    c.setFont("Helvetica-Bold", 11)
    # Correlativo (Esquina superior derecha)
    c.drawString(450, 680, str(memo.numero_documento))
    
    # Bloque de Cabeceras
    c.drawString(120, 640, f"{receptor.nombres_apellidos}") # PARA
    c.setFont("Helvetica", 10)
    c.drawString(120, 625, f"{receptor.cargos[0].nombre if receptor.cargos else 'Sin cargo'}") 
    
    c.setFont("Helvetica-Bold", 11)
    c.drawString(120, 595, f"{emisor.nombres_apellidos}") # DE
    c.setFont("Helvetica", 10)
    c.drawString(120, 580, f"{emisor.cargos[0].nombre if emisor.cargos else 'Sin cargo'}")
    
    c.setFont("Helvetica", 11)
    c.drawString(120, 550, f"{memo.fecha.strftime('%d de %B de %Y')}") # FECHA
    c.drawString(120, 520, f"{memo.asunto}") # ASUNTO
    
    # Descripción con saltos de línea
    c.setFont("Helvetica", 11)
    textobject = c.beginText(50, 470)
    lineas_descripcion = memo.descripcion.split('\n')
    for linea in lineas_descripcion:
        textobject.textLine(linea)
    c.drawText(textobject)
    
    # Firma simulada
    c.setFont("Helvetica-Bold", 10)
    c.drawCentredString(letter[0]/2, 100, f"{emisor.nombres_apellidos}")
    c.setFont("Helvetica", 9)
    c.drawCentredString(letter[0]/2, 85, "Fundacion Instituto de Ingenieria")
    c.drawCentredString(letter[0]/2, 70, f"{memo.fecha.strftime('%Y-%m-%d')} 15:59:19")
    
    c.save()
    capa_texto.seek(0)

    # 3. Buscar la plantilla PDF original en tu sistema
    base_dir = os.path.dirname(os.path.abspath(__file__))
    ruta_plantilla = os.path.join(base_dir, "templates_pdf", "plantilla_memorandum.pdf")
    
    try:
        # 4. Fusionar la plantilla con la capa de texto
        plantilla_pdf = PdfReader(open(ruta_plantilla, "rb"))
        texto_pdf = PdfReader(capa_texto)
        
        # Tomamos la primera página de la plantilla y le estampamos el texto
        pagina_resultado = plantilla_pdf.pages[0]
        pagina_resultado.merge_page(texto_pdf.pages[0])
        
        # Guardar el resultado final
        salida = PdfWriter()
        salida.add_page(pagina_resultado)
        
        buffer_salida = io.BytesIO()
        salida.write(buffer_salida)
        buffer_salida.seek(0)
        
        # 5. Devolver al navegador
        return Response(content=buffer_salida.getvalue(), media_type="application/pdf")
        
    except FileNotFoundError:
        raise HTTPException(status_code=500, detail=f"No se encontró la plantilla en: {ruta_plantilla}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fusionando PDF: {str(e)}")

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