import asyncpg
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv(override=True)

# Esta es la variable global que retendrá las conexiones vivas.
# Tus otros archivos (memoria, historial, kpis) importan ESTA variable.
pool = None

async def conectar_db():
    """
    Inicializa el pool de conexiones.
    Se ejecuta una sola vez al arrancar FastAPI (en el lifespan).
    """
    global pool
    db_url = os.getenv('DB_URL')
    
    if not db_url:
        print("❌ Error: No se encontró la variable DB_URL en el archivo .env")
        return
        
    try:
        print("⏳ Inicializando el pool de conexiones a PostgreSQL...")
        # Configuración del pool:
        # min_size: Mantiene siempre al menos 5 conexiones abiertas listas para usar.
        # max_size: Limita a 20 conexiones simultáneas para no saturar PostgreSQL.
        pool = await asyncpg.create_pool(
            dsn=db_url,
            min_size=5,
            max_size=20,
            command_timeout=60 # Tiempo máximo (en segundos) antes de cancelar una consulta lenta
        )
        print("✅ Pool de conexiones creado y listo para recibir peticiones.")
    except Exception as e:
        print(f"❌ Error crítico al crear el pool de conexiones: {e}")

async def cerrar_db():
    """
    Cierra todas las conexiones del pool ordenadamente.
    Se ejecuta al apagar el servidor FastAPI para liberar recursos.
    """
    global pool
    if pool is not None:
        print("⏳ Cerrando el pool de conexiones a PostgreSQL...")
        await pool.close()
        print("✅ Pool de conexiones cerrado correctamente.")