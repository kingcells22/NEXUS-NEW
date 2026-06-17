import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.database import SessionLocal, engine
from app import models

# Asegurar que las tablas existan
models.Base.metadata.create_all(bind=engine)

def poblar_bd():
    db: Session = SessionLocal()

    print("Iniciando inyección de datos (Seed)...")

    # 1. Insertar Tipos de Nómina
    tipos_nomina = ['FIJO', 'COMISIÓN DE SERVICIO', 'CONTRATADO', 'AD HONOREM', 'ALTO NIVEL']
    for nombre in tipos_nomina:
        if not db.query(models.TipoNomina).filter_by(nombre=nombre).first():
            db.add(models.TipoNomina(nombre=nombre))
    
    # 2. Insertar Cargos
    cargos = ['JEFE DE CENTRO', 'CONSULTORA JURÍDICA', 'COORDINADOR', 'DIRECTOR TÉCNICO', 'GERENTE', 'PRESIDENTE', 'AUDITORA INTERNA']
    for nombre in cargos:
        if not db.query(models.Cargo).filter_by(nombre=nombre).first():
            db.add(models.Cargo(nombre=nombre))

    # 3. Insertar Centros (AQUÍ APLICAMOS LA INTELIGENCIA PARA EVITAR CHOQUES)
    centros = [
        {'nombre': 'Centro Nacional de Teledetección', 'abreviatura': 'CENATEL'},
        {'nombre': 'Centro de Procesamiento Digital de Imágenes', 'abreviatura': 'CPDI'},
        {'nombre': 'Centro de Ingeniería Eléctrica y Sistemas', 'abreviatura': 'CIES'},
        {'nombre': 'Centro de Ingeniería Mecánica y Diseño Industrial', 'abreviatura': 'CIMECDI'},
        {'nombre': 'Consultoría Jurídica', 'abreviatura': 'CONSULTORIA'},
        {'nombre': 'Centro de Seguridad Informática y Certificación Electrónica', 'abreviatura': 'CSICE'},
        {'nombre': 'Oficina de Tecnología de la Información y la Comunicación', 'abreviatura': 'OTIC'},
        {'nombre': 'Centro de Tecnología de Materiales', 'abreviatura': 'CTM'},
        {'nombre': 'Dirección Técnica', 'abreviatura': 'DT'},
        {'nombre': 'Oficina De Gestión Administrativa', 'abreviatura': 'OGA'},
        {'nombre': 'Oficina Planificación y Presupuesto', 'abreviatura': 'OPP'},
        {'nombre': 'Oficina De Gestión Humana', 'abreviatura': 'OGH'},
        {'nombre': 'Oficina Gestión Comunicacional', 'abreviatura': 'OGC'},
        {'nombre': 'Presidencia Ejecutiva', 'abreviatura': 'PRESIDENCIA'},
        {'nombre': 'Unidad de Auditoría', 'abreviatura': 'AUDITORIA'},
        {'nombre': 'SERVICIOS GENERALES', 'abreviatura': 'SERVICIOS GENERALES'}
    ]
    for c in centros:
        # 1. Buscamos primero por abreviatura para ver si ya existe la clave única
        centro_db = db.query(models.Centro).filter_by(abreviatura=c['abreviatura']).first()
        
        if not centro_db:
            # 2. Si no existe por abreviatura, buscamos por el nombre exacto
            centro_db = db.query(models.Centro).filter_by(nombre=c['nombre']).first()
            
        if not centro_db:
            # 3. Si definitivamente no existe, lo creamos limpio
            db.add(models.Centro(nombre=c['nombre'], abreviatura=c['abreviatura']))
        else:
            # 4. Si ya existía por las pruebas manuales (ej: OTIC), le corregimos el nombre al oficial
            centro_db.nombre = c['nombre']
            
    db.commit() # Guardamos catálogos primero

    # 4. Insertar Empleados
    empleados = [
        {"cedula": "10782532", "nombres_apellidos": "BLANCO PALOMINO, LILIANA COROMOTO", "fecha_ingreso": datetime(2019, 2, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina De Gestión Administrativa"]},
        {"cedula": "6428821", "nombres_apellidos": "DURAN COLMENARES, FRANCISCO ANTONIO", "fecha_ingreso": datetime(2015, 1, 12), "tipoNomina": "ALTO NIVEL", "cargos": ["PRESIDENTE"], "centros": ["Presidencia Ejecutiva"]},
        {"cedula": "16658754", "nombres_apellidos": "NAVARRO, KENMERRY", "fecha_ingreso": datetime(2023, 1, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina de Tecnología de la Información y la Comunicación"]}
    ]

    for emp_data in empleados:
        if not db.query(models.Empleado).filter_by(cedula=emp_data["cedula"]).first():
            tipo_nom = db.query(models.TipoNomina).filter_by(nombre=emp_data["tipoNomina"]).first()
            
            nuevo_emp = models.Empleado(
                cedula=emp_data["cedula"],
                nombres_apellidos=emp_data["nombres_apellidos"],
                fecha_ingreso=emp_data["fecha_ingreso"],
                tipo_nomina_id=tipo_nom.id if tipo_nom else None
            )
            
            # Asociar cargos y centros
            for c_nombre in emp_data["cargos"]:
                cargo = db.query(models.Cargo).filter_by(nombre=c_nombre).first()
                if cargo: nuevo_emp.cargos.append(cargo)
                
            for c_nombre in emp_data["centros"]:
                centro = db.query(models.Centro).filter_by(nombre=c_nombre).first()
                if centro: nuevo_emp.centros.append(centro)
                
            db.add(nuevo_emp)

    db.commit()
    print("¡Base de datos NEXUS poblada exitosamente!")
    db.close()

if __name__ == "__main__":
    poblar_bd()