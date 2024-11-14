
import configparser
import os
import sys

def obtener_ruta_config_ini(relative_path):
    # Obtiene la ruta del directorio de ejecución del .exe o script
    if getattr(sys, 'frozen', False):  # Verifica si está empaquetado
        dir_actual = os.path.dirname(sys.executable)
    else:
        dir_actual = os.path.abspath(".")
    return os.path.join(dir_actual, relative_path)

def cargar_configuracion():
    config = configparser.ConfigParser()
    config.read(obtener_ruta_config_ini("config.ini"))
    rutas = {
        "source_path": config["Paths"]["source_path"],
        "destination_path": config["Paths"]["destination_path"],
        "file_keyword": config["Paths"]["file_keyword"]
    }
    db_config = {
        "server": config["Database"]["server"],
        "database": config["Database"]["database"],
        "table_data": config["Database"]["table_data"],
        "table_control": config["Database"]["table_control"],
        "table_control_descompresion": config["Database"]["table_control_descompresion"]
    }
    return rutas, db_config

def guardar_rutas(source, destination):
    config = configparser.ConfigParser()
    config.read(obtener_ruta_config_ini("config.ini"))
    config["Paths"]["source_path"] = source
    config["Paths"]["destination_path"] = destination
    with open(obtener_ruta_config_ini(), 'w') as configfile:
        config.write(configfile)

def obtener_columnas_esperadas():
    config = configparser.ConfigParser()
    config.read(obtener_ruta_config_ini("config.ini"))
    columnas = config["Columns"]["column_names"]
    return columnas

def cargar_filtros():
    config = configparser.ConfigParser()
    config.read('config.ini')

    # Cargar los filtros tal como están definidos en config.ini
    filtros = {
        "filtro_1_tipo_producto": config["Filters"]["filtro_1_tipo_producto"],
        "filtro_1_privada": [x.strip() for x in config["Filters"]["filtro_1_privada"].split(",")],
        "filtro_2_tipo_producto": config["Filters"]["filtro_2_tipo_producto"],
        "filtro_2_tipo_operacion": config["Filters"]["filtro_2_tipo_operacion"]
    }

    return filtros
