from datetime import datetime
from contextlib import asynccontextmanager
from database import pool_conexiones # Tu pool de conexiones actual

@asynccontextmanager
async def _obtener_conexion():
    """Toma una conexión disponible del pool."""
    if pool_conexiones.pool is None:
        raise Exception('El pool de conexiones no ha sido inicializado')
    async with pool_conexiones.pool.acquire() as conexion:
        yield conexion

async def crear_tabla_kpis():
    """
    Crea la tabla plana para extraer KPIs hacia los dashboards.
    Se ejecuta al arrancar FastAPI.
    """
    query = """
    CREATE TABLE IF NOT EXISTS kpis_interacciones (
        id VARCHAR(12) PRIMARY KEY,
        fecha_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        fecha_fin TIMESTAMP,
        telefono VARCHAR(25) NOT NULL,
        contrato_cliente VARCHAR(50),
        area_principal VARCHAR(50),
        subcategoria VARCHAR(50),
        resultado_final VARCHAR(50)
    );
    """
    try:
        async with _obtener_conexion() as conexion:
            print('Inicializando tabla de KPIs para Dashboards...')
            await conexion.execute(query)
            print('Tabla kpis_interacciones lista.')
    except Exception as e:
        print(f'Error al inicializar BD de KPIs: {e}')

# ==========================================
# FUNCIONES PARA REGISTRAR LOS EVENTOS
# ==========================================

async def registrar_inicio_interaccion(id_generado: str, telefono: str, contrato: str, area: str, subcategoria: str):
    """
    Inserta la fila cuando el cliente inicia una consulta.
    El 'id_generado' es tu UUID de 12 dígitos.
    """
    query = """
    INSERT INTO kpis_interacciones (id, telefono, contrato_cliente, area_principal, subcategoria)
    VALUES ($1, $2, $3, $4, $5)
    """
    try:
        async with _obtener_conexion() as conexion:
            await conexion.execute(query, id_generado, telefono, contrato, area, subcategoria)
    except Exception as e:
        print(f'Error al registrar inicio de KPI: {e}')

async def cerrar_interaccion(id_generado: str, resultado: str):
    """
    Actualiza la fila con la fecha de fin y el resultado exacto cuando el caso termina.
    """
    query = """
    UPDATE kpis_interacciones
    SET fecha_fin = $1, resultado_final = $2
    WHERE id = $3
    """
    try:
        async with _obtener_conexion() as conexion:
            hora_actual = datetime.now()
            await conexion.execute(query, hora_actual, resultado, id_generado)
    except Exception as e:
        print(f'Error al cerrar KPI: {e}')