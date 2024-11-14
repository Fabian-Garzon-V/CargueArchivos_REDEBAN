import customtkinter as ctk
from tkinter import messagebox, filedialog
from config import cargar_configuracion, guardar_rutas
from database import cargar_archivos_descomprimidos, conectar_sql_server
from file_processing import descomprimir_archivos
from database import archivo_ya_cargado

# Configuración inicial de customtkinter
ctk.set_appearance_mode("dark")  # Puedes cambiar a "light" para un tema claro
ctk.set_default_color_theme("blue")  # Otros temas: "green", "dark-blue"

class Aplicacion:
    def __init__(self, root):
        self.root = root
        self.root.title("Descompresión y carga de archivos - REDEBAN")
        self.root.geometry("1000x500")
        self.root.configure(bg="#2e2e2e")  # Fondo oscuro para apariencia moderna

        # Mostrar solo la pantalla de autenticación al inicio
        self.mostrar_autenticacion()

    def mostrar_autenticacion(self):
        # Frame de autenticación, ocupa toda la ventana
        self.auth_frame = ctk.CTkFrame(self.root, corner_radius=15)
        self.auth_frame.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(self.auth_frame, text="Usuario:", font=("Arial", 14, "bold")).pack(pady=10)
        self.entry_usuario = ctk.CTkEntry(self.auth_frame, width=250)
        self.entry_usuario.pack(pady=5)

        ctk.CTkLabel(self.auth_frame, text="Contraseña:", font=("Arial", 14, "bold")).pack(pady=10)
        self.entry_contrasena = ctk.CTkEntry(self.auth_frame, width=250, show="*")
        self.entry_contrasena.pack(pady=5)

        ctk.CTkButton(self.auth_frame, text="Ingresar", command=self.verificar_credenciales, width=200).pack(pady=20)

    def verificar_credenciales(self):
        usuario = self.entry_usuario.get()
        contrasena = self.entry_contrasena.get()

        rutas, db_config = cargar_configuracion()
        conexion = conectar_sql_server(db_config["server"], db_config["database"], usuario, contrasena)

        if conexion:
            self.auth_frame.pack_forget()  # Oculta la pantalla de autenticación
            messagebox.showinfo("Éxito", "Autenticación exitosa")
            self.mostrar_interfaz_principal(conexion, rutas, db_config)
        else:
            messagebox.showerror("Error", "Credenciales incorrectas")

    def guardar_rutas_con_mensaje(self, source_path, destination_path):
        # Guarda las rutas
        guardar_rutas(source_path, destination_path)
        # Muestra mensaje de confirmación
        messagebox.showinfo("Éxito", "Las rutas se guardaron correctamente.")

    def mostrar_interfaz_principal(self, conexion, rutas, db_config):
        # Notebook para las pestañas
        notebook = ctk.CTkTabview(self.root, width=800, height=400, corner_radius=15)
        notebook.pack(fill='both', expand=True, padx=20, pady=20)

        tab_configuracion = notebook.add("Configuración de Rutas")

        # Frame de configuración de rutas
        config_frame = ctk.CTkFrame(tab_configuracion, corner_radius=15)
        config_frame.pack(fill="both", expand=True, padx=20, pady=20)

        # Configuración de las entradas y botones en el frame
        ctk.CTkLabel(config_frame, text="Ruta de Origen:", font=("Arial", 12)).grid(row=0, column=0, padx=5, pady=5, sticky="w")
        source_path_entry = ctk.CTkEntry(config_frame, width=600)
        source_path_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        source_path_entry.insert(0, rutas["source_path"])

        seleccionar_origen_button = ctk.CTkButton(config_frame, text="Seleccionar...", command=lambda: self.seleccionar_ruta(source_path_entry))
        seleccionar_origen_button.grid(row=0, column=2, padx=5, pady=5)

        ctk.CTkLabel(config_frame, text="Ruta de Destino:", font=("Arial", 12)).grid(row=1, column=0, padx=5, pady=5, sticky="w")
        destination_path_entry = ctk.CTkEntry(config_frame, width=600)
        destination_path_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        destination_path_entry.insert(0, rutas["destination_path"])

        seleccionar_destino_button = ctk.CTkButton(config_frame, text="Seleccionar...", command=lambda: self.seleccionar_ruta(destination_path_entry))
        seleccionar_destino_button.grid(row=1, column=2, padx=5, pady=5)

        save_button = ctk.CTkButton(config_frame, text="Guardar Rutas", command=lambda: self.guardar_rutas_con_mensaje(source_path_entry.get(), destination_path_entry.get()), width=150)
        save_button.grid(row=2, column=1, pady=20, sticky="e")

        descomprimir_button = ctk.CTkButton(tab_configuracion, text="Descomprimir Archivos",
                                            command=lambda: descomprimir_archivos({
                                                "source_path": source_path_entry.get(),
                                                "destination_path": destination_path_entry.get(),
                                                "file_keyword": rutas["file_keyword"],
                                                "db_config": db_config
                                            }, conexion, archivo_ya_cargado),
                                            width=200, height=40)
        descomprimir_button.pack(pady=10)

        # Barra de progreso inicializada en 0
        self.progress_bar = ctk.CTkProgressBar(tab_configuracion, width=500)
        self.progress_bar.set(0)  # Iniciar en 0
        self.progress_bar.pack(pady=10)

        cargar_button = ctk.CTkButton(tab_configuracion, text="Cargar Archivos en SQL Server",
                                      command=lambda: self.cargar_archivos_con_progreso(conexion, rutas["destination_path"], db_config),
                                      width=200, height=40)
        cargar_button.pack(pady=10)

    def cargar_archivos_con_progreso(self, conexion, destination_path, db_config):
        # Función para cargar archivos con progreso real basado en lotes procesados
        self.progress_bar.set(0)  # Reiniciar barra de progreso al inicio
        archivos_exitosos, archivos_con_error = cargar_archivos_descomprimidos(
            conexion, destination_path, db_config["table_data"], db_config["table_control"], self.progress_bar
        )
        
        # Generar el mensaje de resumen
        mensaje = f"Archivos cargados exitosamente: {archivos_exitosos}\n"
        if archivos_con_error > 0:
            mensaje += f"Archivos con error: {archivos_con_error}. Revisa el archivo de log para más detalles."
        
        # Mostrar el mensaje de resumen final
        messagebox.showinfo("Resumen de Carga", mensaje)
        
        # Al finalizar, reiniciar la barra de progreso a 0
        self.progress_bar.set(0)

    def seleccionar_ruta(self, entry):
        ruta = filedialog.askdirectory()
        if ruta:
            entry.delete(0, ctk.END)
            entry.insert(0, ruta)

if __name__ == "__main__":
    root = ctk.CTk()
    app = Aplicacion(root)
    root.mainloop()
