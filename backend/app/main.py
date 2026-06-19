from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base

# === IMPORTACIÓN DE NUESTROS ENRUTADORES MODULARES ===
from app.routes import auth, rrhh, empleados, documentos

# 1. Inicialización y creación de tablas
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Nexus API Refactorizada y Modular")

# 2. Configuración de CORS (Conexión con Vue)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],
)

# 3. === ENCHUFAMOS TODOS LOS MÓDULOS DEL SISTEMA ===
app.include_router(auth.router)
app.include_router(rrhh.router)
app.include_router(empleados.router)
app.include_router(documentos.router)

# 4. Ruta de prueba de salud del servidor
@app.get("/")
def read_root():
    return {"mensaje": "¡El backend de Nexus está corriendo al 100% con Arquitectura Modular Avanzada!"}