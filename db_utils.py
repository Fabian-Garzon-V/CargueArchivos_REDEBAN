import pyodbc

def registrar_archivo_cargado(conexion, nombre_archivo, table_control):
    cursor = conexion.cursor()
    cursor.execute(f"INSERT INTO {table_control} (NombreArchivo) VALUES (?)", nombre_archivo)
    conexion.commit()
