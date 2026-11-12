from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
import logging
import tkinter as tk
from tkinter import ttk

# Configuración del sistema de logs
logging.basicConfig(
    filename='sistema_fj.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# --- EXCEPCIONES PERSONALIZADAS ---
class ErrorSistemaFJ(Exception):
    """Excepción base para errores del sistema."""
    pass

class ClienteNoValidoError(ErrorSistemaFJ):
    """Se lanza cuando los datos del cliente no cumplen con las validaciones."""
    pass

class ReservaError(ErrorSistemaFJ):
    """Se lanza cuando ocurre un fallo al procesar una reserva."""
    pass


# --- CLASE ABSTRACTA GENERAL ---
class EntidadBase(ABC):
    @abstractmethod
    def obtener_detalles(self) -> str:
        pass


# --- CLASE CLIENTE ---
class Cliente(EntidadBase):
    def __init__(self, identificacion: str, nombre: str, correo: str):
        self.__identificacion = self.__validar_id(identificacion)
        self.__nombre = self.__validar_nombre(nombre)
        self.__correo = self.__validar_correo(correo)

    def __validar_id(self, identificacion: str) -> str:
        if not identificacion or not identificacion.isdigit():
            logging.error(f"Identificación inválida intentada: {identificacion}")
            raise ClienteNoValidoError("La identificación debe contener solo números.")
        return identificacion

    def __validar_nombre(self, nombre: str) -> str:
        if not nombre or len(nombre.strip()) < 3:
            logging.error(f"Nombre inválido intentado: {nombre}")
            raise ClienteNoValidoError("El nombre del cliente es muy corto o está vacío.")
        return nombre

    def __validar_correo(self, correo: str) -> str:
        if "@" not in correo or "." not in correo:
            logging.error(f"Correo inválido intentado: {correo}")
            raise ClienteNoValidoError("El formato del correo electrónico no es válido.")
        return correo

    @property
    def identificacion(self):
        return self.__identificacion

    @property
    def nombre(self):
        return self.__nombre

    @property
    def correo(self):
        return self.__correo

    def obtener_detalles(self) -> str:
        return f"Cliente: {self.__nombre} (ID: {self.__identificacion})"

    def __str__(self):
        return f"{self.__nombre} (ID: {self.__identificacion})"


# --- CLASE ABSTRACTA SERVICIO Y DERIVADAS ---
class Servicio(EntidadBase, ABC):
    def __init__(self, codigo: str, nombre_servicio: str, costo_base: float):
        if not codigo or not codigo.strip():
            raise ValueError("El código es obligatorio.")
        if not isinstance(costo_base, (int, float)) or isinstance(costo_base, bool) or costo_base <= 0:
            raise ValueError("El costo base debe ser un número mayor a cero.")
        
        self.codigo = codigo
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        pass


class ReservaSalas(Servicio):
    def __init__(self, codigo: str, costo_base: float, capacidad: int):
        super().__init__(codigo, "Reserva de Sala", costo_base)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un número entero positivo.")
        self.capacidad = capacidad

    def calcular_costo(self, horas: int, descuento: float = 0.0) -> float:
        if not isinstance(horas, int) or horas <= 0:
            raise ValueError("Las horas deben ser un número entero positivo.")
        if not (0 <= descuento < 1):
            raise ValueError("El descuento debe estar entre 0 y 1.")
        return round((self.costo_base * horas) * (1 - descuento), 2)

    def obtener_detalles(self) -> str:
        return f"[Sala] {self.nombre_servicio} ({self.codigo}) - Capacidad: {self.capacidad} - Costo/h: ${self.costo_base}"

    def __str__(self):
        return f"Sala: {self.codigo} - {self.nombre_servicio}"


class AlquilerEquipos(Servicio):
    def __init__(self, codigo: str, costo_base: float, tipo_equipo: str):
        super().__init__(codigo, "Alquiler de Equipo", costo_base)
        if not tipo_equipo or not tipo_equipo.strip():
            raise ValueError("El tipo de equipo es obligatorio.")
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, dias: int, seguro_adicional: bool = False) -> float:
        if not isinstance(dias, int) or dias <= 0:
            raise ValueError("Los días de alquiler deben ser un número entero positivo.")
        adicional = 15.0 if seguro_adicional else 0.0
        return round((self.costo_base * dias) + adicional, 2)

    def obtener_detalles(self) -> str:
        return f"[Equipo] {self.tipo_equipo} ({self.codigo}) - Costo/día: ${self.costo_base}"

    def __str__(self):
        return f"Equipo: {self.codigo} - {self.tipo_equipo}"


class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo: str, costo_base: float, area: str):
        super().__init__(codigo, "Asesoría Especializada", costo_base)
        if not area or not area.strip():
            raise ValueError("El área de asesoría es obligatoria.")
        self.area = area

    def calcular_costo(self, sesiones: int, impuesto: float = 0.19) -> float:
        if not isinstance(sesiones, int) or sesiones <= 0:
            raise ValueError("El número de sesiones debe ser un número entero positivo.")
        if not isinstance(impuesto, (int, float)) or impuesto < 0:
            raise ValueError("El impuesto debe ser mayor o igual a cero.")
        subtotal = self.costo_base * sesiones
        return round(subtotal * (1 + impuesto), 2)

    def obtener_detalles(self) -> str:
        return f"[Asesoría] {self.area} ({self.codigo}) - Costo/sesión: ${self.costo_base}"

    def __str__(self):
        return f"Asesoría: {self.codigo} - {self.area}"


# --- CLASE RESERVA ---
class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
        if not id_reserva or not id_reserva.strip():
            raise ReservaError("El ID de la reserva es obligatorio.")
        if not isinstance(duracion, int) or duracion <= 0:
            raise ReservaError("La duración debe ser un número entero positivo.")
        
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"

    def confirmar_reserva(self):
        try:
            self.estado = "Confirmada"
            logging.info(f"Reserva {self.id_reserva} confirmada con éxito.")
        except Exception as e:
            self.estado = "Fallida"
            logging.error(f"Error al confirmar reserva {self.id_reserva}: {e}")
            raise ReservaError("No se pudo confirmar la reserva.") from e
        else:
            print(f"Reserva {self.id_reserva} validada sin interrupciones.")
        finally:
            print(f"Estado de la reserva {self.id_reserva}: {self.estado}")

    def cancelar_reserva(self):
        if self.estado not in ["Pendiente", "Confirmada"]:
            raise ReservaError(f"No se puede cancelar una reserva en estado '{self.estado}'.")
        self.estado = "Cancelada"
        logging.info(f"Reserva {self.id_reserva} cancelada.")

    def procesar_reserva(self) -> float:
        if self.estado != "Confirmada":
            raise ReservaError("La reserva debe estar confirmada para poder procesarla y calcular costos.")
        costo = self.servicio.calcular_costo(self.duracion)
        logging.info(f"Reserva {self.id_reserva} procesada. Costo total: ${costo}")
        return costo

    def __str__(self):
        return f"Reserva {self.id_reserva} - Cliente: {self.cliente.nombre} [{self.estado}]"


# --- GESTOR GENERAL DEL SISTEMA ---
class SistemaFJ:
    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente: Cliente):
        if any(c.identificacion == cliente.identificacion for c in self.clientes):
            raise ClienteNoValidoError("El cliente ya se encuentra registrado.")
        self.clientes.append(cliente)
        logging.info(f"Cliente registrado: {cliente.nombre}")

    def registrar_servicio(self, servicio: Servicio):
        if any(s.codigo == servicio.codigo for s in self.servicios):
            raise ErrorSistemaFJ(f"Ya existe un servicio con el código '{servicio.codigo}'.")
        self.servicios.append(servicio)
        logging.info(f"Servicio registrado: {servicio.codigo}")

    def registrar_reserva(self, reserva: Reserva):
        if any(r.id_reserva == reserva.id_reserva for r in self.reservas):
            raise ReservaError(f"Ya existe una reserva con el ID '{reserva.id_reserva}'.")
        if reserva.cliente not in self.clientes:
            raise ReservaError("El cliente no está registrado en el sistema.")
        if reserva.servicio not in self.servicios:
            raise ReservaError("El servicio no está registrado en el sistema.")
        self.reservas.append(reserva)
        logging.info(f"Reserva registrada: {reserva.id_reserva}")


# --- INTERFAZ GRÁFICA (TKINTER) ---
class SistemaFJApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas y Servicios FJ")
        self.root.geometry("850x650")
        self.sistema = SistemaFJ()
        
        # Precargar servicios para pruebas rápidas en la interfaz
        try:
            self.sistema.registrar_servicio(ReservaSalas("S001", 50.0, 10))
            self.sistema.registrar_servicio(AlquilerEquipos("E001", 100.0, "Proyector"))
            self.sistema.registrar_servicio(AsesoriaEspecializada("A001", 80.0, "Software"))
        except Exception:
            pass

        self.crear_interfaz()

    def crear_interfaz(self):
        titulo = ttk.Label(self.root, text="Sistema de Reservas y Servicios FJ", font=("Arial", 18, "bold"))
        titulo.pack(pady=15)

        contenedor = ttk.Frame(self.root)
        contenedor.pack(fill="both", expand=True, padx=15)

        self.crear_seccion_clientes(contenedor)
        self.crear_seccion_reservas(contenedor)
        self.crear_seccion_resultados()

    def crear_seccion_clientes(self, contenedor):
        frame = ttk.LabelFrame(contenedor, text="Registro de Clientes", padding=15)
        frame.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        ttk.Label(frame, text="Identificación:").grid(row=0, column=0, sticky="w", pady=5)
        self.txt_identificacion = ttk.Entry(frame, width=25)
        self.txt_identificacion.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="w", pady=5)
        self.txt_nombre = ttk.Entry(frame, width=25)
        self.txt_nombre.grid(row=1, column=1, pady=5)

        ttk.Label(frame, text="Correo Electrónico:").grid(row=2, column=0, sticky="w", pady=5)
        self.txt_correo = ttk.Entry(frame, width=25)
        self.txt_correo.grid(row=2, column=1, pady=5)

        btn = ttk.Button(frame, text="Registrar Cliente", command=self.accion_registrar_cliente)
        btn.grid(row=3, column=0, columnspan=2, pady=15)

    def accion_registrar_cliente(self):
        try:
            c = Cliente(self.txt_identificacion.get().strip(), self.txt_nombre.get().strip(), self.txt_correo.get().strip())
            self.sistema.registrar_cliente(c)
            self.mostrar_resultado(f"Éxito: Cliente {c.nombre} registrado.")
            self.actualizar_comboboxes()
            self.txt_identificacion.delete(0, tk.END)
            self.txt_nombre.delete(0, tk.END)
            self.txt_correo.delete(0, tk.END)
        except Exception as e:
            self.mostrar_resultado(f"Error: {e}")

    def crear_seccion_reservas(self, contenedor):
        frame = ttk.LabelFrame(contenedor, text="Gestión de Reservas", padding=15)
        frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        ttk.Label(frame, text="Cliente:").grid(row=0, column=0, sticky="w", pady=5)
        self.cmb_clientes = ttk.Combobox(frame, width=23, state="readonly")
        self.cmb_clientes.grid(row=0, column=1, pady=5)

        ttk.Label(frame, text="Servicio:").grid(row=1, column=0, sticky="w", pady=5)
        self.cmb_servicios = ttk.Combobox(frame, width=23, state="readonly")
        self.cmb_servicios.grid(row=1, column=1, pady=5)
        self.actualizar_comboboxes()

        ttk.Label(frame, text="Duración (Horas/Días):").grid(row=2, column=0, sticky="w", pady=5)
        self.txt_duracion = ttk.Entry(frame, width=25)
        self.txt_duracion.grid(row=2, column=1, pady=5)

        btn = ttk.Button(frame, text="Crear y Procesar Reserva", command=self.accion_crear_reserva)
        btn.grid(row=3, column=0, columnspan=2, pady=15)

    def actualizar_comboboxes(self):
        self.cmb_clientes['values'] = [c.nombre for c in self.sistema.clientes]
        self.cmb_servicios['values'] = [s.codigo for s in self.sistema.servicios]

    def accion_crear_reserva(self):
        try:
            cli_nom = self.cmb_clientes.get()
            srv_cod = self.cmb_servicios.get()
            dur_str = self.txt_duracion.get().strip()

            if not cli_nom or not srv_cod or not dur_str:
                raise ValueError("Complete todos los campos de reserva.")

            cliente = next(c for c in self.sistema.clientes if c.nombre == cli_nom)
            servicio = next(s for s in self.sistema.servicios if s.codigo == srv_cod)
            reserva = Reserva(f"R-{len(self.sistema.reservas)+1:03d}", cliente, servicio, int(dur_str))
            
            self.sistema.registrar_reserva(reserva)
            reserva.confirmar_reserva()
            costo = reserva.procesar_reserva()
            self.mostrar_resultado(f"Reserva {reserva.id_reserva} procesada. Total: ${costo}")
        except Exception as e:
            self.mostrar_resultado(f"Error en reserva: {e}")

    def crear_seccion_resultados(self):
        frame = ttk.LabelFrame(self.root, text="Consola de Resultados", padding=10)
        frame.pack(fill="both", expand=True, padx=20, pady=10)

        self.txt_resultados = tk.Text(frame, height=8, state="disabled")
        self.txt_resultados.pack(fill="both", expand=True)

    def mostrar_resultado(self, mensaje):
        self.txt_resultados.config(state="normal")
        self.txt_resultados.insert(tk.END, mensaje + "\n")
        self.txt_resultados.see(tk.END)
        self.txt_resultados.config(state="disabled")

def main():
    root = tk.Tk()
    app = SistemaFJApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
