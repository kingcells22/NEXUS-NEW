from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import Response, FileResponse
from sqlalchemy.orm import Session, joinedload
from datetime import datetime
import io
import os
import textwrap
import shutil # <--- NUEVO: Para guardar archivos en el disco

# --- LIBRERÍAS PARA PDF ---
from pypdf import PdfReader, PdfWriter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER, TA_RIGHT
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter

from app.database import get_db
from app import models, schemas
from app.security import get_usuario_actual

router = APIRouter(
    prefix="/api",
    tags=["Documentos y Bandeja"]
)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
ANEXOS_DIR = os.path.join(UPLOAD_DIR, "anexos") # <--- NUEVO: Carpeta para los adjuntos
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(ANEXOS_DIR, exist_ok=True)

# === AHORA RECIBE FORM DATA Y ARCHIVOS EN VEZ DE JSON ===
@router.post("/memorandums", response_model=schemas.MemorandumRespuesta)
def crear_memorandum_real(
    emisor_id: str = Form(...),
    receptor_id: str = Form(...),
    asunto: str = Form(...),
    fecha: str = Form(...),
    descripcion: str = Form(...),
    anexos: str = Form(...),
    archivo: UploadFile = File(None), 
    db: Session = Depends(get_db)
):
    año_actual = datetime.utcnow().year
    emisor = db.query(models.Empleado).options(joinedload(models.Empleado.centros)).filter(models.Empleado.id == emisor_id).first()
    
    if not emisor: raise HTTPException(status_code=404, detail="El empleado emisor no existe.")

    abreviatura_centro = emisor.centros[0].abreviatura if emisor.centros else "FIIIDT"
    prefijo = f"{abreviatura_centro}-{año_actual}-"
    
    ultimo_memo = db.query(models.Memorandum).filter(
        models.Memorandum.numero_documento.like(f"{prefijo}%")
    ).order_by(models.Memorandum.id.desc()).with_for_update().first()

    if ultimo_memo and ultimo_memo.numero_documento:
        try: nuevo_correlativo = int(ultimo_memo.numero_documento.split('-')[-1]) + 1
        except ValueError: nuevo_correlativo = 1
    else:
        nuevo_correlativo = 1

    numero_generado = f"{prefijo}{nuevo_correlativo:03d}"

    # --- CORRECCIÓN CLAVE: CONVERTIMOS EL TEXTO A BOOLEANO ---
    anexos_bool = True if anexos == "Sí" else False

    nuevo_memo = models.Memorandum(
        numero_documento=numero_generado,
        asunto=asunto, descripcion=descripcion, fecha=fecha,
        emisor_id=emisor_id, receptor_id=receptor_id, 
        anexos=anexos_bool,  # <--- AQUÍ PASAMOS EL BOOLEANO
        centro=emisor.centros[0].nombre if emisor.centros else "Sede Principal",
        status="CREADO" 
    )
    db.add(nuevo_memo)
    db.commit()
    db.refresh(nuevo_memo)

    # --- LÓGICA DE GUARDADO DEL ARCHIVO FÍSICO ---
    if anexos == "Sí" and archivo and archivo.filename:
        ext = os.path.splitext(archivo.filename)[1]
        nombre_archivo = f"{numero_generado}_anexo{ext}"
        ruta_guardado = os.path.join(ANEXOS_DIR, nombre_archivo)
        
        with open(ruta_guardado, "wb") as buffer:
            shutil.copyfileobj(archivo.file, buffer)
    # ---------------------------------------------

    return nuevo_memo

@router.get("/memorandums/emitidos")
def obtener_memos_emitidos(db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == usuario_actual["sub"]).first()
    empleado = db.query(models.Empleado).filter(models.Empleado.usuario_id == usuario.id).first()
    
    memos = db.query(models.Memorandum).filter(models.Memorandum.emisor_id == empleado.id).order_by(models.Memorandum.id.desc()).all()
    
    resultados = []
    for m in memos:
        resultados.append({
            "id": m.id, "correlativo": m.numero_documento,
            "presentador": empleado.nombres_apellidos,
            "cargo_presentador": empleado.cargos[0].nombre if empleado.cargos else "Sin cargo",
            "asunto": m.asunto, "decision": m.status, "fecha": m.fecha.strftime("%d/%m/%Y"), "anexos": m.anexos
        })
    return resultados

@router.get("/memorandums/recibidos")
def obtener_memos_recibidos(db: Session = Depends(get_db), usuario_actual: dict = Depends(get_usuario_actual)):
    usuario = db.query(models.Usuario).filter(models.Usuario.correo == usuario_actual["sub"]).first()
    empleado = db.query(models.Empleado).filter(models.Empleado.usuario_id == usuario.id).first()
    
    if not empleado: raise HTTPException(status_code=404, detail="Perfil de empleado no encontrado.")

    memos = db.query(models.Memorandum).filter(models.Memorandum.receptor_id == empleado.id).order_by(models.Memorandum.id.desc()).all()
    
    resultados = []
    for m in memos:
        emisor = db.query(models.Empleado).filter(models.Empleado.id == m.emisor_id).first()
        cargo_emisor = emisor.cargos[0].nombre if emisor and emisor.cargos else "Sin cargo"
        
        resultados.append({
            "id": m.id, "correlativo": m.numero_documento,
            "remitente": emisor.nombres_apellidos if emisor else "Desconocido",
            "cargo_remitente": cargo_emisor,
            "asunto": m.asunto, "decision": m.status, "fecha": m.fecha.strftime("%d/%m/%Y"), "anexos": m.anexos
        })
    return resultados

@router.get("/memorandums/{memo_id}/pdf")
def generar_pdf_memorandum(memo_id: int, db: Session = Depends(get_db)):
    memo = db.query(models.Memorandum).filter(models.Memorandum.id == memo_id).first()
    if not memo: raise HTTPException(status_code=404, detail="Memorándum no encontrado.")
        
    emisor = db.query(models.Empleado).filter(models.Empleado.id == memo.emisor_id).first()
    receptor = db.query(models.Empleado).filter(models.Empleado.id == memo.receptor_id).first()

    emisor_cargo = emisor.cargos[0].nombre if emisor.cargos else "Sin cargo"
    receptor_cargo = receptor.cargos[0].nombre if receptor.cargos else "Sin cargo"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=letter, rightMargin=50, leftMargin=50, topMargin=110, bottomMargin=115, 
        title=f"Memorándum {memo.numero_documento}", author=emisor.nombres_apellidos
    )

    cintillo_path = os.path.join(BASE_DIR, "templates_pdf", "cintillo.png")
    pie_opcion_1 = os.path.join(BASE_DIR, "templates_pdf", "pie_pagina.png")
    pie_opcion_2 = os.path.join(BASE_DIR, "templates_pdf", "pie_de_pagina.png")
    pie_path = pie_opcion_2 if os.path.exists(pie_opcion_2) else pie_opcion_1

    def dibujar_fondos(canvas, doc):
        canvas.saveState()
        if os.path.exists(cintillo_path): canvas.drawImage(cintillo_path, 0, 792 - 90, width=612, height=90)
        if os.path.exists(pie_path): canvas.drawImage(pie_path, 0, 0, width=612, height=115) 
        canvas.restoreState()

    Story = []
    styles = getSampleStyleSheet()
    
    estilo_titulo = ParagraphStyle('Titulo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=12, alignment=TA_CENTER)
    estilo_correlativo = ParagraphStyle('Correlativo', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, alignment=TA_RIGHT)
    estilo_negrita = ParagraphStyle('Negrita', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11)
    estilo_normal = ParagraphStyle('Texto', parent=styles['Normal'], fontName='Helvetica', fontSize=11)
    estilo_cuerpo = ParagraphStyle('Cuerpo', parent=styles['Normal'], fontName='Helvetica', fontSize=11, leading=15, alignment=TA_JUSTIFY)

    data_cabecera = [["", Paragraph("MEMORÁNDUM", estilo_titulo), Paragraph(str(memo.numero_documento), estilo_correlativo)]]
    t_cabecera = Table(data_cabecera, colWidths=[100, 312, 100])
    Story.append(t_cabecera)
    Story.append(Spacer(1, 15))

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

    html_limpio = memo.descripcion
    html_limpio = html_limpio.replace("<br>", "<br/>")
    html_limpio = html_limpio.replace("<p>", "").replace("</p>", "<br/>\n")
    html_limpio = html_limpio.replace("<ul>", "").replace("</ul>", "")
    html_limpio = html_limpio.replace("<ol>", "").replace("</ol>", "")
    html_limpio = html_limpio.replace("<li>", "&bull; ").replace("</li>", "<br/>\n")
    html_limpio = html_limpio.replace("<strong>", "<b>").replace("</strong>", "</b>")
    html_limpio = html_limpio.replace("<em>", "<i>").replace("</em>", "</i>")

    parrafos_brutos = html_limpio.split('\n')
    for p in parrafos_brutos:
        texto_final = p.strip()
        if texto_final:
            while texto_final.endswith("<br/>"): 
                texto_final = texto_final[:-5].strip()
            if texto_final:
                Story.append(Paragraph(f'<p align="justify">{texto_final}</p>', estilo_cuerpo))
                Story.append(Spacer(1, 8))

    doc.build(Story, onFirstPage=dibujar_fondos, onLaterPages=dibujar_fondos)
    buffer.seek(0)
    
    return Response(content=buffer.getvalue(), media_type="application/pdf", headers={"Content-Disposition": "inline"})