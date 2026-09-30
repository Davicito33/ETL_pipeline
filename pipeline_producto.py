import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv



# CARGAR CONFIGURACIÓN DEL ARCHIVO .env


load_dotenv()

RUTA_ARCHIVOS = os.getenv("RUTA_ARCHIVOS")
RUTA_DB = os.getenv("RUTA_DB")


# Crear las rutas completas
RUTA_CSV = os.path.join(RUTA_ARCHIVOS, "DIM_PRODUCTO.csv")


#
# 1. LEER EL ARCHIVO CSV


productos = pd.read_csv(
    RUTA_CSV,
    sep=";",
    encoding="utf-8"
)



# 2. LIMPIAR LOS DATOS


columnas_texto = [
    "ProductoID",
    "NombreProducto",
    "MarcaProducto",
    "NombreCategoria",
    "NombreProveedor",
    "PaisProveedor"
]

for columna in columnas_texto:
    productos[columna] = (
        productos[columna]
        .astype(str)
        .str.strip()
    )


# Convertir el precio a número
productos["PrecioListado"] = pd.to_numeric(
    productos["PrecioListado"],
    errors="coerce"
)



# 3. CONECTAR CON LA BASE DE DATOS


conexion = mysql.connector.connect(
    host=os.getenv("MYSQL_HOST"),
    port=int(os.getenv("MYSQL_PORT")),
    database=os.getenv("MYSQL_DATABASE"),
    user=os.getenv("MYSQL_USER"),
    password=os.getenv("MYSQL_PASSWORD")
)

cursor = conexion.cursor()


# Contadores
insertados = 0
actualizados = 0



# 4. RECORRER LOS PRODUCTOS


for _, producto in productos.iterrows():

    producto_id = producto["ProductoID"]
    nombre = producto["NombreProducto"]
    marca = producto["MarcaProducto"]
    categoria = producto["NombreCategoria"]
    proveedor = producto["NombreProveedor"]
    pais = producto["PaisProveedor"]
    precio = producto["PrecioListado"]


    
    # 5. BUSCAR SI EL PRODUCTO YA EXISTE
    

    cursor.execute(
        """
        SELECT
            NombreProducto,
            MarcaProducto,
            NombreCategoria,
            NombreProveedor,
            PaisProveedor,
            PrecioListado
        FROM DimProducto
        WHERE ProductoID = %s
        """,
        (producto_id,)
    )

    producto_existente = cursor.fetchone()


    
    # 6. SI NO EXISTE, INSERTAR
   

    if producto_existente is None:

        cursor.execute(
            """
            INSERT INTO DimProducto
            (
                ProductoID,
                NombreProducto,
                MarcaProducto,
                NombreCategoria,
                NombreProveedor,
                PaisProveedor,
                PrecioListado
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            """,
            (
                producto_id,
                nombre,
                marca,
                categoria,
                proveedor,
                pais,
                precio
            )
        )

        insertados += 1


    
    # 7. SI EXISTE, COMPARAR
    

    else:

        datos_nuevos = (
            nombre,
            marca,
            categoria,
            proveedor,
            pais,
            precio
        )

        # Si algún dato cambió, actualizar
        if producto_existente != datos_nuevos:

            cursor.execute(
                """
                UPDATE DimProducto
                SET
                    NombreProducto = %s,
                    MarcaProducto = %s,
                    NombreCategoria = %s,
                    NombreProveedor = %s,
                    PaisProveedor = %s,
                    PrecioListado = %s
                WHERE ProductoID = %s
                """,
                (
                    nombre,
                    marca,
                    categoria,
                    proveedor,
                    pais,
                    precio,
                    producto_id
                )
            )

            actualizados += 1



# 8. GUARDAR CAMBIOS


conexion.commit()
conexion.close()



# 9. MOSTRAR RESULTADO


print("======================================")
print("       PIPELINE DE PRODUCTOS")
print("======================================")
print(f"Productos insertados: {insertados}")
print(f"Productos actualizados: {actualizados}")
print("Proceso terminado correctamente.")