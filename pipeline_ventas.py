import pandas as pd
import mysql.connector
import os
from dotenv import load_dotenv


#
# CARGAR CONFIGURACIÓN DEL ARCHIVO .env
#

load_dotenv()

RUTA_ARCHIVOS = os.getenv("RUTA_ARCHIVOS")


# Crear las rutas completas
RUTA_CSV = os.path.join(RUTA_ARCHIVOS, "VENTAS_FACT.csv")




# 1. LEER EL ARCHIVO CSV


# El CSV utiliza ; como separador
ventas = pd.read_csv(
    RUTA_CSV,
    sep=";",
    encoding="utf-8"
)

ventas["Descuento"] = (
    ventas["Descuento"]
    .astype(str)
    .str.replace(",", ".", regex=False)
)

ventas["Descuento"] = pd.to_numeric(
    ventas["Descuento"],
    errors="coerce"
)



# 2. CONECTAR CON LA BASE DE DATOS


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



# 3. RECORRER LAS VENTAS


for _, venta in ventas.iterrows():

    venta_id = venta["VentaID"]
    fecha_id = venta["FechaID"]
    tienda_id = venta["TiendaID"]
    producto_id = venta["ProductoID"]
    cliente_id = venta["ClienteID"]
    unidades = venta["Unidades"]
    precio_unitario = venta["PrecioUnitario"]
    descuento = venta["Descuento"]
    valor_venta = venta["ValorVenta"]


  
    # 4. BUSCAR SI LA VENTA YA EXISTE
 

    cursor.execute(
        """
        SELECT
            FechaID,
            TiendaID,
            ProductoID,
            ClienteID,
            Unidades,
            PrecioUnitario,
            Descuento,
            ValorVenta
        FROM VentasFact
        WHERE VentaID = %s
        """,
        (venta_id,)
    )

    venta_existente = cursor.fetchone()


  
    # 5. SI NO EXISTE, INSERTAR
   
    if venta_existente is None:

        cursor.execute(
            """
            INSERT INTO VentasFact
            (
                VentaID,
                FechaID,
                TiendaID,
                ProductoID,
                ClienteID,
                Unidades,
                PrecioUnitario,
                Descuento,
                ValorVenta
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                venta_id,
                fecha_id,
                tienda_id,
                producto_id,
                cliente_id,
                unidades,
                precio_unitario,
                descuento,
                valor_venta
            )
        )

        insertados += 1



    # 6. SI EXISTE, COMPARAR LOS DATOS
  

    else:

        datos_nuevos = (
            fecha_id,
            tienda_id,
            producto_id,
            cliente_id,
            unidades,
            precio_unitario,
            descuento,
            valor_venta
        )

        # Si los datos son diferentes, actualizar
        if venta_existente != datos_nuevos:

            cursor.execute(
                """
                UPDATE VentasFact
                SET
                    FechaID = %s,
                    TiendaID = %s,
                    ProductoID = %s,
                    ClienteID = %s,
                    Unidades = %s,
                    PrecioUnitario = %s,
                    Descuento = %s,
                    ValorVenta = %s
                WHERE VentaID = %s
                """,
                (
                    fecha_id,
                    tienda_id,
                    producto_id,
                    cliente_id,
                    unidades,
                    precio_unitario,
                    descuento,
                    valor_venta,
                    venta_id
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
print("       PIPELINE DE VENTAS")
print("======================================")
print(f"Ventas insertadas: {insertados}")
print(f"Ventas actualizadas: {actualizados}")
print("Proceso terminado correctamente.")