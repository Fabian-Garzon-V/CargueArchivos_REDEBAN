
# Cargue de Archivos REDEBAN

## Descripción del Proyecto
Este proyecto facilita la carga de archivos de transacciones REDEBAN a una base de datos SQL Server. Incluye funciones para la descompresión de archivos en formato ZIP, el procesamiento y filtrado de datos en formato CSV, y la inserción de estos datos en SQL Server, todo mediante una interfaz gráfica de usuario.

## Características
- **Descompresión de archivos**: Procesa archivos ZIP de manera recursiva, descomprimiendo archivos que cumplan con ciertos criterios de nombre.
- **Filtrado de datos**: Aplica filtros personalizados para seleccionar solo los registros relevantes para la base de datos.
- **Carga en base de datos SQL Server**: Inserta los datos en SQL Server con control de errores y un sistema de logs.
- **Interfaz gráfica de usuario (GUI)**: Usa `customtkinter` para ofrecer una interfaz de usuario intuitiva.

## Requisitos
- **Python 3.x**
- Librerías necesarias:
  - `customtkinter`
  - `pyodbc`
  - `pandas`

## Instalación
1. Clona el repositorio:
   ```bash
   git clone https://github.com/Fabian-Garzon-V/CargueArchivos_REDEBAN.git
   ```
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

## Configuración
### Archivo `config.ini`
Asegúrate de que el archivo `config.ini` esté configurado correctamente para conectarse a la base de datos SQL Server y para especificar las rutas de origen y destino para los archivos. Aquí tienes un ejemplo de configuración:

```ini
[Paths]
source_path = ruta/al/directorio/de/origen
destination_path = ruta/al/directorio/de/destino
file_keyword = palabra_clave_para_filtrar_archivos

[Database]
server = nombre_del_servidor
database = nombre_de_la_base
table_data = nombre_de_la_tabla_datos
table_control = nombre_de_la_tabla_control
table_control_descompresion = nombre_de_la_tabla_control_descompresion

[Filters]
filtro_1_tipo_producto = tipo_producto_1
filtro_1_privada = valor1, valor2
filtro_2_tipo_producto = tipo_producto_2
filtro_2_tipo_operacion = operacion_tipo
```

## Uso
1. Ejecuta la aplicación con el comando:
   ```bash
   python main.py
   ```
2. A través de la GUI, proporciona las credenciales de SQL Server cuando se soliciten.
3. Usa las funciones de descompresión y carga para procesar los archivos en la ruta de origen.

## Creación del ejecutable (.exe)
Para convertir el script en un ejecutable, puedes utilizar PyInstaller con el siguiente comando:

```bash
pyinstaller --onefile --noconsole --icon="ruta/a/redeban_grande.ico" --add-data "config.ini;." --add-data "procesamiento.log;." --add-data "resumen_carga.txt;." --hidden-import=customtkinter main.py
```

## Archivos de Log
- **procesamiento.log**: Registra los errores y advertencias que se produzcan durante el proceso de carga y descompresión de archivos.
- **resumen_carga.txt**: Incluye un resumen de los archivos procesados, indicando si fueron cargados correctamente o si presentaron algún error.

## Estructura del Proyecto
```plaintext
CargueArchivos_REDEBAN/
├── config.ini                # Archivo de configuración
├── database.py               # Funciones de conexión y carga a SQL Server
├── file_processing.py        # Funciones de descompresión y filtrado
├── main.py                   # Script principal con GUI
├── db_utils.py               # Utilidades para la base de datos
├── procesamiento.log         # Archivo de log para errores y eventos
├── resumen_carga.txt         # Resumen de la carga de archivos
└── README.md                 # Documentación del proyecto
```

## Licencia
Este proyecto está licenciado bajo la Licencia MIT.

## Contribuciones
Las contribuciones son bienvenidas. Por favor, abre un "issue" para reportar problemas o enviar sugerencias.

## Contacto
Para preguntas o comentarios, contacta a [tu_email@example.com].
