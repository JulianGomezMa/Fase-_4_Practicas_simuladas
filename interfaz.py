import tkinter as tk
from tkinter import ttk
from SistemaIntegraldeGestion import SistemaFJ,Cliente,Servicio,Reserva

class SistemaFJApp: 
    """Interfaz gráfica para el Sistema de Reservas y Servicios FJ."""
    
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas y Servicios FJ")
        self.root.geometry("800x600")

        self.sistema = SistemaFJ()

        self.crear_interfaz()
        
    def crear_interfaz(self):
        """Construye los elementos y componentes de la interfaz gráfica."""
        
        titulo = ttk.Label(
            self.root,
            text="Sistema de Reservas y Servicios FJ",
            font=("Arial", 20, "bold"),
        )
        titulo.pack(pady=20)
        
        contenedor = ttk.Frame(self.root)
        contenedor.pack(fill="both", expand=True, padx=20)
        
        self.crear_seccion_clientes(contenedor)
        self.crear_seccion_reservas(contenedor)
        self.crear_seccion_resultados()
        
    def crear_seccion_clientes(self, contenedor):
        """Crea la sección de registro de clientes."""
        
        frame_clientes = ttk.LabelFrame(
            contenedor,
            text="Registro de Clientes",
            padding=15
        )
        frame_clientes.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(
            frame_clientes, 
            text="Identificación:"
        ).grid(row=0, column=0, sticky="w", pady=5)
        
        self.txt_indentificacion = ttk.Entry(frame_clientes, width=30)
        self.txt_indentificacion.grid(row=0, column=1, pady=5)
        
        ttk.Label(
            frame_clientes,
            text="Nombre:"
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        self.txt_nombre = ttk.Entry(frame_clientes, width=30)
        self.txt_nombre.grid( row=1, column=1, pady=5)
        
        ttk.Label(
            frame_clientes,
            text="Correo Electrónico:"
        ).grid(row=2, column=0, sticky="w", pady=5)
        
        self.txt_correo = ttk.Entry(frame_clientes, width=30)
        self.txt_correo.grid(row=2, column=1, pady=5)
        
        self.btn_registrar_cliente = ttk.Button(
            frame_clientes,
            text="Registrar Cliente",
            command=self.registrar_cliente
        )
        self.btn_registrar_cliente.grid(row=3, column=0, columnspan=2, pady=15)
        
    def registrar_cliente(self):
        """Registra un nuevo cliente en el sistema."""
        
        identificacion = self.txt_indentificacion.get().strip()
        nombre = self.txt_nombre.get().strip()
        correo = self.txt_correo.get().strip()
        
        try:
            cliente = Cliente(identificacion, nombre, correo)
            
            self.sistema.registrar_cliente(cliente)
            
            self.mostrar_resultado(f"Cliente {nombre} registrado exitosamente.")
        except Exception as e:
            self.mostrar_resultado(f"Error al registrar cliente: {str(e)}")
        finally:
            self.txt_indentificacion.delete(0, tk.END)
            self.txt_nombre.delete(0, tk.END)
            self.txt_correo.delete(0, tk.END)
        
    def crear_seccion_reservas(self, contenedor):
        """Crea la sección destinada a la gestión de reservas"""
        
        frame_reservas = ttk.LabelFrame(
            contenedor,
            text="Gestión de Reservas",
            padding=15
        )
        frame_reservas.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ttk.Label(
            frame_reservas,
            text="Cliente:"
        ).grid(row=0, column=0, sticky="w", pady=5)

        self.cmb_clientes = ttk.Combobox(frame_reservas, width=27, state="readonly")
        self.cmb_clientes.grid(row=0, column=1, pady=5)
        
        ttk.Label(
            frame_reservas,
            text="Servicio:"
        ).grid(row=1, column=0, sticky="w", pady=5)
        
        self.cmb_servicios = ttk.Combobox(frame_reservas, width=27, state="readonly")
        self.cmb_servicios.grid(row=1, column=1, pady=5)
        
        ttk.Label(
            frame_reservas,
            text="Duracion:"
        ).grid(row=2, column=0, sticky="w", pady=5)
        
        self.txt_duracion = ttk.Entry(frame_reservas, width=30)
        self.txt_duracion.grid(row=2, column=1, pady=5)
        
        ttk.Label(
            frame_reservas,
            text="Estado:"
        ).grid(row=3, column=0, sticky="w", pady=5)
        
        self.lbl_estado = ttk.Label(frame_reservas, text="Pendiente")
        self.lbl_estado.grid(row=3, column=1, sticky="w", pady=5)
        
        self.btn_crear_reserva = ttk.Button(
            frame_reservas,
            text="Crear reserva",
        )
        self.btn_crear_reserva.grid(row=4, column=0, columnspan=2, pady=10)
        
        self.btn_confirmar_reserva = ttk.Button(
            frame_reservas,
            text="Confirmar",
        )
        self.btn_confirmar_reserva.grid(row=5, column=0, padx=5, pady=5)
        
        self.btn_cancelar_reserva = ttk.Button(
            frame_reservas,
            text="Cancelar",
        )
        self.btn_cancelar_reserva.grid(row=5, column=1, padx=5, pady=5)
        
    def crear_seccion_resultados(self):
        """Crea la sección donde se mostrarán los resultados de las operaciones."""
        
        frame_resultados = ttk.LabelFrame(
            self.root,
            text="Resultados",
            padding=10
        )
        frame_resultados.pack(fill="both", expand=True, padx=30, pady=10)
        
        self.txt_resultados = tk.Text(
            frame_resultados,
            height=8, 
            state="disabled",
        )
        self.txt_resultados.pack(fill="both", expand=True)
        
    def mostrar_resultado(self, mensaje):
        """Muestra un mensaje en el área de resultados."""

        self.txt_resultados.config(state="normal")
    
        self.txt_resultados.insert(
            tk.END,
            mensaje + "\n"
        )
    
        self.txt_resultados.config(state="disabled")
        
def main():
    """Inicia la aplicación."""
    
    root = tk.Tk()
    app = SistemaFJApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()