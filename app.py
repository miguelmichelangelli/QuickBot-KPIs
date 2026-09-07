from fastapi import FastAPI, BackgroundTasks
from pydantic import BaseModel
from contextlib import asynccontextmanager

# Importaciones modulares limpias
from database import pool_conexiones
import create_uuid
import postgre as kpis_repository

@asynccontextmanager
async def lifespan(app: FastAPI):
    await pool_conexiones.conectar_db()
    await kpis_repository.crear_tabla_kpis()
    yield
    await pool_conexiones.cerrar_db()

app = FastAPI(title="Microservicio de KPIs", lifespan=lifespan)

# Modelos para Swagger / Postman
class PayloadInicio(BaseModel):
    telefono: str
    contrato_cliente: str
    area_principal: str
    subcategoria: str

class PayloadCierre(BaseModel):
    id_interaccion: str
    resultado_final: str

@app.post("/api/kpi/iniciar")
async def api_iniciar_kpi(datos: PayloadInicio, background_tasks: BackgroundTasks):
    nuevo_id = create_uuid.generate_uuid()
    
    # Encolamos la inserción para responder inmediatamente
    background_tasks.add_task(
        kpis_repository.registrar_inicio_interaccion,
        nuevo_id,
        datos.telefono,
        datos.contrato_cliente,
        datos.area_principal,
        datos.subcategoria
    )
    return {"status": "success", "id_generado": nuevo_id}

@app.post("/api/kpi/cerrar")
async def api_cerrar_kpi(datos: PayloadCierre, background_tasks: BackgroundTasks):
    background_tasks.add_task(
        kpis_repository.cerrar_interaccion,
        datos.id_interaccion,
        datos.resultado_final
    )
    return {"status": "success", "mensaje": "Cierre encolado correctamente"}