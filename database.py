import os
import sys
import pyodbc
import logging
import pandas as pd
from tkinter import simpledialog, messagebox
from config import obtener_columnas_esperadas
from db_utils import registrar_archivo_cargado
from file_processing import aplicar_filtros

# Función para obtener la ruta de recursos independientemente de si es .py o .exe
def recurso_path(relative_path):
    if getattr(sys, 'frozen', False):  # Para ejecutable
        base_path = os.path.dirname(sys.executable)
    else:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# Configurar logging
log_path = recurso_path("procesamiento.log")
logging.basicConfig(
    filename=log_path,
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def conectar_sql_server(server, database, username, password):
    """Establece una conexión con SQL Server."""
    try:
        conexion = pyodbc.connect(
            f'DRIVER={{ODBC Driver 17 for SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}',
            timeout=30
        )
        return conexion
    except pyodbc.Error as e:
        messagebox.showerror("Error de Conexión", f"No se pudo conectar a SQL Server: {e}")
        return None

def solicitar_credenciales(db_config):
    """Solicita al usuario sus credenciales para conectarse a SQL Server."""
    username = simpledialog.askstring("Credenciales", "Ingrese el usuario de SQL Server:")
    password = simpledialog.askstring("Credenciales", "Ingrese la contraseña de SQL Server:", show="*")
    if username and password:
        conexion = conectar_sql_server(db_config["server"], db_config["database"], username, password)
        if conexion:
            return conexion
        else:
            messagebox.showerror("Error", "Credenciales incorrectas o problemas de conexión.")
            return solicitar_credenciales(db_config)
    else:
        messagebox.showerror("Error", "Debe ingresar usuario y contraseña.")
        return solicitar_credenciales(db_config)

def archivo_ya_cargado(conexion, nombre_archivo, table_control):
    """Verifica si el archivo ya ha sido registrado en la tabla de control."""
    cursor = conexion.cursor()
    cursor.execute(f"SELECT 1 FROM {table_control} WHERE NombreArchivo = ?", nombre_archivo)
    return cursor.fetchone() is not None


def cargar_archivos_descomprimidos(conexion, ruta_destino, table_data, table_control, progress_bar):
    """Procesa y carga todos los archivos de texto en la carpeta de destino."""
    resultados = []
    archivos = [archivo for archivo in os.listdir(ruta_destino) if archivo.endswith(".txt")]
    total_archivos = len(archivos)
    
    # Establecer el progreso máximo para los archivos
    if total_archivos > 0:
        progress_bar.set(0)
        progress_step = 1 / total_archivos  # Paso de progreso por archivo

    archivos_cargados_exitosamente = 0  # Contador para archivos cargados correctamente
    archivos_con_error = 0  # Contador para archivos que no se pudieron cargar

    for i, archivo in enumerate(archivos):
        archivo_path = os.path.join(ruta_destino, archivo)
        
        # Llamar a la función para procesar el archivo
        estado = procesar_archivo_txt(conexion, archivo_path, table_data, table_control, progress_bar, resultados)

        # Actualizar la barra de progreso por archivo procesado
        progress_bar.set((i + 1) * progress_step)
        progress_bar.update_idletasks()  # Refrescar la interfaz gráfica en cada iteración

        # Contar según el estado de procesamiento
        if estado == "exito":
            archivos_cargados_exitosamente += 1
        elif estado == "error":
            archivos_con_error += 1
            logging.error(f"Error al cargar el archivo {archivo}. Revisa el log para más detalles.")

    # Guardar el resumen en un archivo de texto
    resumen_path = recurso_path("resumen_carga.txt")
    with open(resumen_path, "w") as resumen_file:
        resumen_file.write("Resumen de archivos procesados:\n")
        resumen_file.write("\n".join(resultados))

    # Devolver el conteo de archivos exitosos y con errores
    return archivos_cargados_exitosamente, archivos_con_error


def procesar_archivo_txt(conexion, archivo_path, table_data, table_control, progress_bar, resultados):
    nombre_archivo = os.path.basename(archivo_path)
    
    # Verificar si el archivo ya fue cargado previamente
    if archivo_ya_cargado(conexion, nombre_archivo, table_control):
        resultados.append(f"{nombre_archivo}: Ya fue cargado anteriormente")
        return "ya_cargado"

    # Definir el mapeo de columnas entre el archivo y SQL Server
    mapeo_columnas = {
        "FECHA": "Fecha",
        "TARJETA": "Tarjeta",
        "TIPO OPERACION": "Tipo_Operacion",
        "COMERCIO": "Comercio",
        "TERMINAL": "Terminal",
        "TIPO DE PRODUCTO": "Tipo_Producto",
        "PRIVADA": "Privada",
        "VALOR BRUTO": "Valor_Bruto",
        "RESULTADO": "Resultado"
    }

    try:
        # Leer archivo completo
        data = pd.read_csv(archivo_path, delimiter=',')
        
        # Verificar que las columnas requeridas están presentes
        columnas_esperadas = list(mapeo_columnas.keys())
        columnas_faltantes = [col for col in columnas_esperadas if col not in data.columns]
        if columnas_faltantes:
            mensaje_error = f"{nombre_archivo}: Faltan columnas necesarias - {', '.join(columnas_faltantes)}"
            resultados.append(mensaje_error)
            logging.warning(mensaje_error)
            return "error"

        # Filtrar las columnas y aplicar filtros
        data = data[columnas_esperadas]  # Seleccionar solo las columnas necesarias
        data_filtrada = aplicar_filtros(data)  # Aplicar los filtros configurados
        if data_filtrada.empty:
            mensaje_error = f"{nombre_archivo}: No cumple con los filtros"
            resultados.append(mensaje_error)
            logging.info(mensaje_error)
            return "error"

        # Verificar tipos y transformar columna de fecha
        data_filtrada['FECHA'] = pd.to_datetime(data_filtrada['FECHA'], errors='coerce', format='%d/%m/%Y %H:%M:%S')
        data_filtrada['TARJETA'] = data_filtrada['TARJETA'].astype(str)
        data_filtrada['TIPO OPERACION'] = data_filtrada['TIPO OPERACION'].astype(str)
        data_filtrada['COMERCIO'] = pd.to_numeric(data_filtrada['COMERCIO'], errors='coerce', downcast='integer')
        data_filtrada['TERMINAL'] = data_filtrada['TERMINAL'].astype(str)
        data_filtrada['TIPO DE PRODUCTO'] = data_filtrada['TIPO DE PRODUCTO'].astype(str)
        data_filtrada['PRIVADA'] = data_filtrada['PRIVADA'].astype(str)
        data_filtrada['VALOR BRUTO'] = pd.to_numeric(data_filtrada['VALOR BRUTO'], errors='coerce', downcast='integer')
        data_filtrada['RESULTADO'] = data_filtrada['RESULTADO'].astype(str)

        # Eliminar filas con valores nulos en columnas clave antes de la inserción
        data_filtrada = data_filtrada.dropna(subset=['FECHA', 'COMERCIO', 'VALOR BRUTO'])

        # Renombrar columnas para coincidir con la base de datos
        data_filtrada.rename(columns=mapeo_columnas, inplace=True)

        # Llamar a cargar_datos_sql para cargar el DataFrame en la base de datos
        estado = cargar_datos_sql(conexion, data_filtrada, table_data, progress_bar)
        if estado == "exito":
            registrar_archivo_cargado(conexion, nombre_archivo, table_control)
            resultados.append(f"{nombre_archivo}: Cargado exitosamente")
            return "exito"
        else:
            mensaje_error = f"{nombre_archivo}: Error en la carga - {estado}"
            resultados.append(mensaje_error)
            logging.error(mensaje_error)
            return "error"

    except Exception as e:
        mensaje_error = f"{nombre_archivo}: Error al procesar el archivo - {e}"
        print(mensaje_error)
        resultados.append(mensaje_error)
        logging.error(mensaje_error)
        return "error"

def cargar_datos_sql(conexion, data, table_data, progress_bar):
    try:
        cursor = conexion.cursor()
        placeholders = ", ".join(["?"] * len(data.columns))
        columnas = ", ".join(data.columns)
        
        # Configurar progresión por lotes
        batch_size = 1000
        total_batches = len(data) // batch_size + 1
        progress_step = 1 / total_batches  # Paso de progreso por lote

        for start in range(0, len(data), batch_size):
            batch = data.iloc[start:start + batch_size]
            valores = [tuple(row) for row in batch.values]
            try:
                print(f"Ejecutando inserción en {table_data} para lote de tamaño {len(valores)}...")
                cursor.executemany(
                    f"INSERT INTO {table_data} ({columnas}) VALUES ({placeholders})", valores
                )
                conexion.commit()
                print("Inserción exitosa para el lote.")
                
                # Actualizar barra de progreso usando `set`
                if progress_bar:
                    progress_bar.set(progress_bar.get() + progress_step)
                    progress_bar.update_idletasks()  # Refrescar la interfaz gráfica
                
            except Exception as e:
                print(f"Error al insertar datos en {table_data}: {e}")
                conexion.rollback()
                return "error_insercion_sql"
        
        print("Inserción completada exitosamente.")
        return "exito"
    except Exception as e:
        print(f"Error al insertar los datos en la base de datos: {e}")
        return "error_lectura_dataframe"
