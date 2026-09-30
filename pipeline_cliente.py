import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv



# CARGAR CONFIGURACIÓN DEL ARCHIVO .env


load_dotenv()

RUTA_ARCHIVOS = os.getenv("RUTA_ARCHIVOS")
RUTA_DB = os.getenv("RUTA_DB")


# Crear las rutas completas
RUTA_CSV = os.path.join(RUTA_ARCHIVOS, "DIM_CLIENTE.csv")




# 1. LEER EL ARCHIVO CSV



clientes = pd.read_csv(
    RUTA_CSV,
    sep=";",
    encoding="utf-8"
)





conexion = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    database=os.getenv("MYSQL_DATABASE"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD")
)

cursor = conexion.cursor()


# Contadores para saber qué hizo el pipeline
insertados = 0
actualizados = 0






for _, cliente in clientes.iterrows():

    cliente_id = cliente["ClienteID"]
    nombre = cliente["NombreCliente"]
    genero = cliente["Genero"]
    rango_edad = cliente["RangoEdad"]
    ciudad = cliente["Ciudad"]
    segmento = cliente["SegmentoCliente"]



 

    cursor.execute(
        """
        SELECT
            NombreCliente,
            Genero,
            RangoEdad,
            Ciudad,
            SegmentoCliente
        FROM DimCliente
        WHERE ClienteID = %s
        """,
        (cliente_id,)
    )

    cliente_existente = cursor.fetchone()


  
  
   
    if cliente_existente is None:

        cursor.execute(
            """
            INSERT INTO DimCliente
            (
                ClienteID,
                NombreCliente,
                Genero,
                RangoEdad,
                Ciudad,
                SegmentoCliente
            )
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                cliente_id,
                nombre,
                genero,
                rango_edad,
                ciudad,
                segmento
            )
        )

        insertados += 1
  

    else:

        datos_nuevos = (
            nombre,
            genero,
            rango_edad,
            ciudad,
            segmento
        )

        # Si los datos son diferentes, actualizar
        if cliente_existente != datos_nuevos:

            cursor.execute(
                """
                UPDATE DimCliente
                SET
                    NombreCliente = %s,
                    Genero = %s,
                    RangoEdad = %s,
                    Ciudad = %s,
                    SegmentoCliente = %s
                WHERE ClienteID = %s
                """,
                (
                    nombre,
                    genero,
                    rango_edad,
                    ciudad,
                    segmento,
                    cliente_id
                )
            )

            actualizados += 1


#
# 7. GUARDAR CAMBIOS
#

conexion.commit()
conexion.close()


#
# 8. MOSTRAR RESULTADO
#

print("======================================")
print("       PIPELINE DE CLIENTES")
print("======================================")
print(f"Clientes insertados: {insertados}")
print(f"Clientes actualizados: {actualizados}")
print("Proceso terminado correctamente.")