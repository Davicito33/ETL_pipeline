import pandas as pd
import sqlite3
import os
from dotenv import load_dotenv


# =========================================================
# CARGAR CONFIGURACIÓN DEL ARCHIVO .env
# =========================================================

load_dotenv()

RUTA_ARCHIVOS = os.getenv("RUTA_ARCHIVOS")
RUTA_DB = os.getenv("RUTA_DB")


# Crear las rutas completas
RUTA_CSV = os.path.join(RUTA_ARCHIVOS, "DIM_TIENDA.csv")
RUTA_BASE_DATOS = os.path.join(RUTA_DB, "datacaos_estrella.db")


# =========================================================
# 1. LEER EL ARCHIVO CSV
# =========================================================

tiendas = pd.read_csv(
    RUTA_CSV,
    sep=";",
    encoding="utf-8"
)


# =========================================================
# 2. CONECTAR CON LA BASE DE DATOS
# =========================================================

conexion = sqlite3.connect(RUTA_BASE_DATOS)
cursor = conexion.cursor()


# Contadores
insertados = 0
actualizados = 0


# =========================================================
# 3. RECORRER LAS TIENDAS
# =========================================================

for _, tienda in tiendas.iterrows():

    tienda_id = tienda["TiendaID"]
    nombre = tienda["NombreTienda"]
    ciudad = tienda["Ciudad"]
    region = tienda["Region"]
    fecha_apertura = tienda["FechaApertura"]


    # =====================================================
    # 4. BUSCAR SI LA TIENDA YA EXISTE
    # =====================================================

    cursor.execute(
        """
        SELECT
            NombreTienda,
            Ciudad,
            Region,
            FechaApertura
        FROM DimTienda
        WHERE TiendaID = ?
        """,
        (tienda_id,)
    )

    tienda_existente = cursor.fetchone()


    # =====================================================
    # 5. SI NO EXISTE, INSERTAR
    # =====================================================

    if tienda_existente is None:

        cursor.execute(
            """
            INSERT INTO DimTienda
            (
                TiendaID,
                NombreTienda,
                Ciudad,
                Region,
                FechaApertura
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                tienda_id,
                nombre,
                ciudad,
                region,
                fecha_apertura
            )
        )

        insertados += 1


    # =====================================================
    # 6. SI EXISTE, COMPARAR
    # =====================================================

    else:

        datos_nuevos = (
            nombre,
            ciudad,
            region,
            fecha_apertura
        )

        # Si algún dato cambió, actualizar
        if tienda_existente != datos_nuevos:

            cursor.execute(
                """
                UPDATE DimTienda
                SET
                    NombreTienda = ?,
                    Ciudad = ?,
                    Region = ?,
                    FechaApertura = ?
                WHERE TiendaID = ?
                """,
                (
                    nombre,
                    ciudad,
                    region,
                    fecha_apertura,
                    tienda_id
                )
            )

            actualizados += 1


# =========================================================
# 7. GUARDAR CAMBIOS
# =========================================================

conexion.commit()
conexion.close()


# =========================================================
# 8. MOSTRAR RESULTADO
# =========================================================

print("======================================")
print("       PIPELINE DE TIENDAS")
print("======================================")
print(f"Tiendas insertadas: {insertados}")
print(f"Tiendas actualizadas: {actualizados}")
print("Proceso terminado correctamente.")