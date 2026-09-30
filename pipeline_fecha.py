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
RUTA_CSV = os.path.join(RUTA_ARCHIVOS, "DIM_FECHA.csv")




# 1. LEER EL ARCHIVO CSV


# El CSV utiliza ; como separador
fechas = pd.read_csv(
    RUTA_CSV,
    sep=";",
    encoding="utf-8"
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



# 3. RECORRER LAS FECHAS


for _, fecha in fechas.iterrows():

    fecha_id = fecha["FechaID"]
    fecha_valor = fecha["Fecha"]
    anio = fecha["Anio"]
    trimestre = fecha["Trimestre"]
    mes = fecha["Mes"]
    nombre_mes = fecha["NombreMes"]
    dia = fecha["Dia"]
    dia_semana = fecha["DiaSemana"]
    nombre_dia_semana = fecha["NombreDiaSemana"]
    es_fin_de_semana = fecha["EsFinDeSemana"]


  
    # 4. BUSCAR SI LA FECHA YA EXISTE
 

    cursor.execute(
        """
        SELECT
            Fecha,
            Anio,
            Trimestre,
            Mes,
            NombreMes,
            Dia,
            DiaSemana,
            NombreDiaSemana,
            EsFinDeSemana
        FROM DimFecha
        WHERE FechaID = %s
        """,
        (fecha_id,)
    )

    fecha_existente = cursor.fetchone()


  
    # 5. SI NO EXISTE, INSERTAR
   
    if fecha_existente is None:

        cursor.execute(
            """
            INSERT INTO DimFecha
            (
                FechaID,
                Fecha,
                Anio,
                Trimestre,
                Mes,
                NombreMes,
                Dia,
                DiaSemana,
                NombreDiaSemana,
                EsFinDeSemana
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                fecha_id,
                fecha_valor,
                anio,
                trimestre,
                mes,
                nombre_mes,
                dia,
                dia_semana,
                nombre_dia_semana,
                es_fin_de_semana
            )
        )

        insertados += 1



    # 6. SI EXISTE, COMPARAR LOS DATOS
  

    else:

        datos_nuevos = (
            fecha_valor,
            anio,
            trimestre,
            mes,
            nombre_mes,
            dia,
            dia_semana,
            nombre_dia_semana,
            es_fin_de_semana
        )

        # Si los datos son diferentes, actualizar
        if fecha_existente != datos_nuevos:

            cursor.execute(
                """
                UPDATE DimFecha
                SET
                    Fecha = %s,
                    Anio = %s,
                    Trimestre = %s,
                    Mes = %s,
                    NombreMes = %s,
                    Dia = %s,
                    DiaSemana = %s,
                    NombreDiaSemana = %s,
                    EsFinDeSemana = %s
                WHERE FechaID = %s
                """,
                (
                    fecha_valor,
                    anio,
                    trimestre,
                    mes,
                    nombre_mes,
                    dia,
                    dia_semana,
                    nombre_dia_semana,
                    es_fin_de_semana,
                    fecha_id
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
print("       PIPELINE DE FECHAS")
print("======================================")
print(f"Fechas insertadas: {insertados}")
print(f"Fechas actualizadas: {actualizados}")
print("Proceso terminado correctamente.")