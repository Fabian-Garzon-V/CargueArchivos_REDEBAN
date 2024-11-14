import os
import sys
import pandas as pd
import zipfile
import logging
from tkinter import messagebox
from db_utils import registrar_archivo_cargado
from config import cargar_filtros

# Función para obtener la ruta de recursos, compatible con .py y .exe
def recurso_path(relative_path):
    if getattr(sys, 'frozen', False):  # Detecta si el script está empaquetado en un .exe
        base_path = sys._MEIPASS  # PyInstaller utiliza esta variable para archivos temporales
    else:
        base_path = os.path.abspath(".")  # Directorio actual si no es .exe
    return os.path.join(base_path, relative_path)

# Cambiar `log_path` para escribir en la ubicación actual del ejecutable
log_path = os.path.join(os.path.abspath("."), "procesamiento.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def descomprimir_archivos(config, conexion, verificar_archivo_cargado):
    source_path = config["source_path"]
    destination_path = config["destination_path"]
    file_keyword = config["file_keyword"]
    table_control_descompresion = config["db_config"]["table_control_descompresion"]

    archivos_descomprimidos = 0

    # Validar existencia del directorio de origen y crear el de destino si no existe
    if not os.path.exists(source_path):
        messagebox.showerror("Error", f"La ruta de origen '{source_path}' no existe.")
        return
    os.makedirs(destination_path, exist_ok=True)

    # Recorrer todas las carpetas y subcarpetas dentro de source_path
    for root, _, files in os.walk(source_path):
        for archivo in files:
            archivo_path = os.path.join(root, archivo)

            # Verificar si el archivo es un zip y contiene la palabra clave
            if zipfile.is_zipfile(archivo_path) and file_keyword in archivo:
                nombre_archivo = os.path.basename(archivo)

                # Verificar si el archivo ya fue descomprimido
                if verificar_archivo_cargado(conexion, nombre_archivo, table_control_descompresion):
                    continue  # Saltar archivos ya procesados

                # Intentar descomprimir el archivo
                try:
                    with zipfile.ZipFile(archivo_path, 'r') as zip_ref:
                        zip_ref.extractall(destination_path)
                        archivos_descomprimidos += 1
                        registrar_archivo_cargado(conexion, nombre_archivo, table_control_descompresion)
                except Exception as e:
                    logging.error(f"Error al descomprimir el archivo {nombre_archivo}: {e}")

    # Mostrar mensaje final si hubo archivos descomprimidos
    if archivos_descomprimidos > 0:
        messagebox.showinfo("Descompresión Completa", f"Se descomprimieron {archivos_descomprimidos} archivos nuevos.")
    else:
        messagebox.showinfo("Descompresión Completa", "No se encontraron archivos nuevos para descomprimir.")

def aplicar_filtros(data):
    # Normalizar nombres de columnas a mayúsculas y sin espacios para consistencia
    data.columns = data.columns.str.strip().str.upper().str.replace(" ", " ")
    filtros = cargar_filtros()

    columna_tipo_producto = "TIPO DE PRODUCTO"

    # Verificar que las columnas necesarias para los filtros existen
    if columna_tipo_producto not in data.columns or "PRIVADA" not in data.columns or "TIPO OPERACION" not in data.columns:
        logging.warning("Advertencia: Falta una o más columnas necesarias para los filtros en el DataFrame.")
        return pd.DataFrame()

    # Aplicar los filtros basados en los valores definidos en `filtros`
    filtro_1 = (data[columna_tipo_producto] == filtros["filtro_1_tipo_producto"]) & \
               (data["PRIVADA"].isin(filtros["filtro_1_privada"]))

    filtro_2 = (data[columna_tipo_producto] == filtros["filtro_2_tipo_producto"]) & \
               (data["TIPO OPERACION"] == filtros["filtro_2_tipo_operacion"])

    # Filtrar los datos y combinar los resultados
    data_filtrado_1 = data[filtro_1]
    data_filtrado_2 = data[filtro_2]
    data_final = pd.concat([data_filtrado_1, data_filtrado_2])
    
    return data_final
