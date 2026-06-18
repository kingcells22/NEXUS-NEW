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

    # 4. Insertar Empleados (ACTUALIZADA CON GÉNERO Y TÍTULOS)
    empleados = [
        {"cedula": "9999999", "nombres_apellidos": "ADMINISTRADOR DEL SISTEMA", "fecha_ingreso": datetime(1997, 12, 31), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Centro de Seguridad Informática y Certificación Electrónica"], "genero": "M", "titulo": "ING."},
        {"cedula": "4117178", "nombres_apellidos": "JACKSON MONASTERIO, YAURI CONCEPCION", "fecha_ingreso": datetime(1993, 5, 16), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina De Gestión Administrativa"], "genero": "F", "titulo": "LIC."},
        {"cedula": "4856684", "nombres_apellidos": "UZCATEGUI OSTOS, JOSE FELIX", "fecha_ingreso": datetime(2022, 8, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Presidencia Ejecutiva"], "genero": "M", "titulo": "ING."},
        {"cedula": "5113332", "nombres_apellidos": "NIÑO BASTIDAS, CARMEN MARISOL", "fecha_ingreso": datetime(2015, 4, 13), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Presidencia Ejecutiva"], "genero": "F", "titulo": "LIC."},
        {"cedula": "5891171", "nombres_apellidos": "MONTOYA LIZARDO, JOSE RAFAEL", "fecha_ingreso": datetime(2011, 4, 26), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina Planificación y Presupuesto"], "genero": "M", "titulo": "ING."},
        {"cedula": "6126546", "nombres_apellidos": "MENDEZ SIRA, LUIS ENRIQUE", "fecha_ingreso": datetime(2005, 4, 4), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina Gestión Comunicacional"], "genero": "M", "titulo": "LIC."},
        {"cedula": "6428821", "nombres_apellidos": "DURAN COLMENARES, FRANCISCO ANTONIO", "fecha_ingreso": datetime(2015, 1, 12), "tipoNomina": "ALTO NIVEL", "cargos": ["PRESIDENTE"], "centros": ["Presidencia Ejecutiva"], "genero": "M", "titulo": "ING."},
        {"cedula": "7663980", "nombres_apellidos": "SUAREZ SANCHEZ, MIRIAM DEL CARMEN", "fecha_ingreso": datetime(2006, 6, 1), "tipoNomina": "FIJO", "cargos": ["JEFE DE CENTRO"], "centros": ["Centro de Tecnología de Materiales"], "genero": "F", "titulo": "ING."},
        {"cedula": "9465377", "nombres_apellidos": "PARRA VALENCIA, GLENDA NAYLEE", "fecha_ingreso": datetime(2015, 4, 1), "tipoNomina": "FIJO", "cargos": ["CONSULTORA JURÍDICA"], "centros": ["Consultoría Jurídica"], "genero": "F", "titulo": "ABG."},
        {"cedula": "9480491", "nombres_apellidos": "TORRES CONTRERAS, JUAN JOSE", "fecha_ingreso": datetime(2019, 10, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina De Gestión Administrativa"], "genero": "M", "titulo": "LIC."},
        {"cedula": "10480510", "nombres_apellidos": "MARTINEZ, CRISMARA MATILDE", "fecha_ingreso": datetime(1993, 8, 13), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina De Gestión Administrativa"], "genero": "F", "titulo": "LIC."},
        {"cedula": "10627121", "nombres_apellidos": "SALAS APONTE, JONATHAN DANIEL", "fecha_ingreso": datetime(2021, 9, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Centro de Seguridad Informática y Certificación Electrónica"], "genero": "M", "titulo": "ING."},
        {"cedula": "10782532", "nombres_apellidos": "BLANCO PALOMINO, LILIANA COROMOTO", "fecha_ingreso": datetime(2019, 2, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina De Gestión Administrativa"], "genero": "F", "titulo": "LIC."},
        {"cedula": "10823354", "nombres_apellidos": "MORENO CAZORLA, DANIEL ALEXANDER", "fecha_ingreso": datetime(2024, 1, 22), "tipoNomina": "FIJO", "cargos": ["JEFE DE CENTRO"], "centros": ["Centro Nacional de Teledetección"], "genero": "M", "titulo": "ING."},
        {"cedula": "11201561", "nombres_apellidos": "ARRIECHI GARCIA, DANKALI GRISCEIS", "fecha_ingreso": datetime(2018, 7, 9), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["SERVICIOS GENERALES"], "genero": "F", "titulo": "LIC."},
        {"cedula": "11232958", "nombres_apellidos": "PALACIOS DE DIAZ, MICHELLE NATHALI", "fecha_ingreso": datetime(2024, 1, 22), "tipoNomina": "COMISIÓN DE SERVICIO", "cargos": ["JEFE DE CENTRO"], "centros": ["Centro de Ingeniería Eléctrica y Sistemas"], "genero": "F", "titulo": "ING."},
        {"cedula": "12059501", "nombres_apellidos": "COLMENARES RENGIFO, JESUS RAMSES", "fecha_ingreso": datetime(2011, 4, 25), "tipoNomina": "FIJO", "cargos": ["DIRECTOR TÉCNICO"], "centros": ["Centro de Seguridad Informática y Certificación Electrónica"], "genero": "M", "titulo": "ING."},
        {"cedula": "12833035", "nombres_apellidos": "CANO PACHECO, VICTOR HUGO", "fecha_ingreso": datetime(2024, 1, 17), "tipoNomina": "FIJO", "cargos": ["DIRECTOR TÉCNICO"], "centros": ["Dirección Técnica"], "genero": "M", "titulo": "ING."},
        {"cedula": "13260631", "nombres_apellidos": "AGUILAR MEDINA, ANTONIO RAMÓN", "fecha_ingreso": datetime(2024, 5, 15), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Dirección Técnica"], "genero": "M", "titulo": "ING."},
        {"cedula": "15306557", "nombres_apellidos": "CUAURO REA, DIOCELIN JOSEPH", "fecha_ingreso": datetime(2024, 2, 14), "tipoNomina": "FIJO", "cargos": ["AUDITORA INTERNA"], "centros": ["Unidad de Auditoría"], "genero": "F", "titulo": "LIC."},
        {"cedula": "15505001", "nombres_apellidos": "SALAZAR ACOSTA, JESÚS JOSÉ", "fecha_ingreso": datetime(2024, 6, 3), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina Planificación y Presupuesto"], "genero": "M", "titulo": "LIC."},
        {"cedula": "15569757", "nombres_apellidos": "PEÑA ORONOZ, MARISELYS ALINE", "fecha_ingreso": datetime(2024, 1, 17), "tipoNomina": "COMISIÓN DE SERVICIO", "cargos": ["COORDINADOR"], "centros": ["Presidencia Ejecutiva"], "genero": "F", "titulo": "LIC."},
        {"cedula": "16309273", "nombres_apellidos": "PADILLA MARCANO, JOSE ALBERTO", "fecha_ingreso": datetime(2024, 3, 13), "tipoNomina": "FIJO", "cargos": ["JEFE DE CENTRO"], "centros": ["Centro de Ingeniería Mecánica y Diseño Industrial"], "genero": "M", "titulo": "ING."},
        {"cedula": "16564850", "nombres_apellidos": "MOLINA ADJUNTAS, MANUEL ALBERTO", "fecha_ingreso": datetime(2020, 8, 16), "tipoNomina": "FIJO", "cargos": ["GERENTE"], "centros": ["Oficina De Gestión Humana"], "genero": "M", "titulo": "LIC."},
        {"cedula": "17641958", "nombres_apellidos": "GUZMAN PARRA, YULY", "fecha_ingreso": datetime(2023, 9, 1), "tipoNomina": "FIJO", "cargos": ["GERENTE"], "centros": ["Oficina Planificación y Presupuesto"], "genero": "F", "titulo": "LIC."},
        {"cedula": "17966052", "nombres_apellidos": "CORREA BELEÑO, CARLOS MANUEL", "fecha_ingreso": datetime(2006, 9, 13), "tipoNomina": "FIJO", "cargos": ["GERENTE"], "centros": ["Oficina De Gestión Administrativa"], "genero": "M", "titulo": "LIC."},
        {"cedula": "20489975", "nombres_apellidos": "SALAS RODRIGUEZ, DANIEL WILDERMIS", "fecha_ingreso": datetime(2022, 11, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Centro de Seguridad Informática y Certificación Electrónica"], "genero": "M", "titulo": "ING."},
        {"cedula": "26327730", "nombres_apellidos": "HERNANDEZ LOPEZ, BRANYER ANTONIO", "fecha_ingreso": datetime(2018, 12, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina De Gestión Administrativa"], "genero": "M", "titulo": "ING."},
        {"cedula": "16658754", "nombres_apellidos": "NAVARRO, KENMERRY", "fecha_ingreso": datetime(2023, 1, 1), "tipoNomina": "FIJO", "cargos": ["COORDINADOR"], "centros": ["Oficina de Tecnología de la Información y la Comunicación"], "genero": "M", "titulo": "ING."}
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