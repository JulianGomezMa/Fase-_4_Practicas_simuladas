from __future__ import annotations
from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import ttk

# Log file configuration for events and errors
logging.basicConfig(
    filename="sistema_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# --- CUSTOM EXCEPTIONS ---
class ErrorSistemaFJ(Exception):
    """Base exception for the Software FJ system."""


class ClienteNoValidoError(ErrorSistemaFJ):
    """Error for invalid or duplicate client data."""


class ReservaError(ErrorSistemaFJ):
    """Error for invalid reservation operation, state, or calculation."""


# --- GENERAL ABSTRACT CLASS ---
class EntidadBase(ABC):
    """Base abstract class for system entities."""

    @abstractmethod
    def obtener_detalles(self) -> str:
        pass


# --- CLIENT CLASS ---
class Cliente(EntidadBase):
    """Represents a client with encapsulated and validated personal data."""

    MIN_ID_LENGTH = 10

    def __init__(self, identificacion: str, nombre: str, correo: str):
        self.__identificacion = self.__validar_id(identificacion)
        self.__nombre = self.__validar_nombre(nombre)
        self.__correo = self.__validar_correo(correo)

    def __validar_id(self, identificacion: str) -> str:
        if not isinstance(identificacion, str):
            raise ClienteNoValidoError("ID must be a text string of digits.")
        id_limpio = identificacion.strip()
        if not id_limpio.isdigit():
            raise ClienteNoValidoError("ID must contain only numbers.")
        if len(id_limpio) < self.MIN_ID_LENGTH:
            raise ClienteNoValidoError(
                f"ID must be at least {self.MIN_ID_LENGTH} digits long."
            )
        return id_limpio

    def __validar_nombre(self, nombre: str) -> str:
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise ClienteNoValidoError("Name must be at least 3 characters long.")
        return nombre.strip()

    def __validar_correo(self, correo: str) -> str:
        if not isinstance(correo, str) or correo.count("@") != 1:
            raise ClienteNoValidoError("Email must contain a single @ symbol.")
        usuario, dominio = correo.strip().split("@")
        if not usuario or not dominio or "." not in dominio:
            raise ClienteNoValidoError("Email must have a valid user and domain.")
        partes = dominio.split(".")
        if any(not parte or parte.isspace() for parte in partes) or any(
            c.isspace() for c in usuario
        ):
            raise ClienteNoValidoError("Email cannot contain spaces or invalid dots.")
        return correo.strip()

    @property
    def identificacion(self) -> str:
        return self.__identificacion

    @property
    def nombre(self) -> str:
        return self.__nombre

    @property
    def correo(self) -> str:
        return self.__correo

    def obtener_detalles(self) -> str:
        return f"Client: {self.__nombre} | ID: {self.__identificacion} | Email: {self.__correo}"

    def __str__(self) -> str:
        return f"{self.__nombre} (ID: {self.__identificacion})"


# --- ABSTRACT SERVICE CLASS AND SUBCLASSES ---
class Servicio(EntidadBase, ABC):
    """Abstract class for Software FJ services."""

    def __init__(self, codigo: str, nombre_servicio: str, costo_base: float):
        if not codigo or not codigo.strip():
            raise ValueError("Service code is required.")
        if (
            not isinstance(costo_base, (int, float))
            or isinstance(costo_base, bool)
            or costo_base <= 0
        ):
            raise ValueError("Base cost must be a number greater than zero.")
        self.codigo = codigo.strip()
        self.nombre_servicio = nombre_servicio.strip()
        self.costo_base = float(costo_base)

    @abstractmethod
    def calcular_costo(self, cantidad: int, descuento: float | None = None, **kwargs) -> dict:
        pass


class ReservaSalas(Servicio):
    """Specialized room reservation service."""

    def __init__(self, codigo: str, costo_base: float, capacidad: int):
        super().__init__(codigo, "Room Reservation", costo_base)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ValueError("Room capacity must be a positive integer.")
        self.capacidad = capacidad

    def calcular_costo(self, cantidad: int, descuento: float | None = None, **kwargs) -> dict:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError("Hours must be an integer greater than or equal to zero.")

        if descuento is None:
            descuento = 0.15 if cantidad >= 5 else (0.10 if cantidad >= 3 else 0.0)

        if (
            not isinstance(descuento, (int, float))
            or isinstance(descuento, bool)
            or not (0 <= descuento < 1)
        ):
            raise ValueError("Discount must be between 0 and 1 (exclusive).")

        subtotal = self.costo_base * cantidad
        valor_desc = subtotal * descuento
        total = subtotal - valor_desc

        return {
            "subtotal": round(subtotal, 2),
            "porcentaje_descuento": round(descuento * 100, 2),
            "descuento": round(valor_desc, 2),
            "seguro": 0.0,
            "impuesto": 0.0,
            "total": round(total, 2),
        }

    def obtener_detalles(self) -> str:
        return f"[Room] {self.nombre_servicio} ({self.codigo}) - Capacity: {self.capacidad} - ${self.costo_base}/h"


class AlquilerEquipos(Servicio):
    """Specialized equipment rental service."""

    def __init__(self, codigo: str, costo_base: float, tipo_equipo: str):
        super().__init__(codigo, "Equipment Rental", costo_base)
        if not tipo_equipo or not tipo_equipo.strip():
            raise ValueError("Equipment type is required.")
        self.tipo_equipo = tipo_equipo.strip()
        self.seguro_activado = False

    def calcular_costo(
        self,
        cantidad: int,
        descuento: float | None = None,
        seguro: bool | None = None,
        **kwargs,
    ) -> dict:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError("Days must be an integer greater than or equal to zero.")

        if descuento is None:
            descuento = 0.15 if cantidad >= 5 else (0.10 if cantidad >= 3 else 0.0)

        if (
            not isinstance(descuento, (int, float))
            or isinstance(descuento, bool)
            or not (0 <= descuento < 1)
        ):
            raise ValueError("Discount must be between 0 and 1 (exclusive).")

        usar_seguro = self.seguro_activado if seguro is None else bool(seguro)

        subtotal = self.costo_base * cantidad
        valor_desc = subtotal * descuento
        sub_desc = subtotal - valor_desc
        valor_seguro = 15.0 if (usar_seguro and cantidad > 0) else 0.0
        total = sub_desc + valor_seguro

        return {
            "subtotal": round(subtotal, 2),
            "porcentaje_descuento": round(descuento * 100, 2),
            "descuento": round(valor_desc, 2),
            "seguro": round(valor_seguro, 2),
            "impuesto": 0.0,
            "total": round(total, 2),
        }

    def activar_seguro(self) -> None:
        self.seguro_activado = True

    def desactivar_seguro(self) -> None:
        self.seguro_activado = False

    def obtener_detalles(self) -> str:
        return f"[Equipment] {self.tipo_equipo} ({self.codigo}) - ${self.costo_base}/day"


class AsesoriaEspecializada(Servicio):
    """Specialized consulting service."""

    def __init__(self, codigo: str, costo_base: float, area: str):
        super().__init__(codigo, "Specialized Consulting", costo_base)
        if not area or not area.strip():
            raise ValueError("Consulting area is required.")
        self.area = area.strip()

    def calcular_costo(
        self,
        cantidad: int,
        descuento: float | None = None,
        impuesto: float = 0.19,
        **kwargs,
    ) -> dict:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError("Sessions must be an integer greater than or equal to zero.")

        if descuento is None:
            descuento = 0.10 if cantidad >= 5 else (0.05 if cantidad >= 3 else 0.0)

        if (
            not isinstance(descuento, (int, float))
            or isinstance(descuento, bool)
            or not (0 <= descuento < 1)
        ):
            raise ValueError("Discount must be between 0 and 1 (exclusive).")
        if (
            not isinstance(impuesto, (int, float))
            or isinstance(impuesto, bool)
            or impuesto < 0
        ):
            raise ValueError("Tax must be a number greater than or equal to zero.")

        subtotal = self.costo_base * cantidad
        valor_desc = subtotal * descuento
        sub_desc = subtotal - valor_desc
        valor_imp = sub_desc * impuesto
        total = sub_desc + valor_imp

        return {
            "subtotal": round(subtotal, 2),
            "porcentaje_descuento": round(descuento * 100, 2),
            "descuento": round(valor_desc, 2),
            "seguro": 0.0,
            "impuesto": round(valor_imp, 2),
            "total": round(total, 2),
        }

    def obtener_detalles(self) -> str:
        return f"[Consulting] {self.area} ({self.codigo}) - ${self.costo_base}/session"


# --- RESERVATION CLASS ---
class Reserva:
    """Integrates client, service, duration, and status with exception handling."""

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        cantidad_reservada: int,
        seguro_aplicado: bool = False,
    ):
        if not id_reserva or not id_reserva.strip():
            raise ReservaError("Reservation ID is required.")
        if (
            not isinstance(cantidad_reservada, int)
            or isinstance(cantidad_reservada, bool)
            or cantidad_reservada <= 0
        ):
            raise ReservaError("Reserved quantity must be a positive integer.")

        self.id_reserva = id_reserva.strip()
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad_reservada = cantidad_reservada
        self.cantidad_transcurrida = 0
        self.seguro_aplicado = seguro_aplicado
        self.estado = "Pending"

    def avanzar_tiempo(self, cantidad: int) -> None:
        if self.estado != "Pending":
            raise ReservaError(f"Cannot advance consumption in '{self.estado}' status.")
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValueError("Quantity to consume must be a positive integer.")
        if self.cantidad_transcurrida + cantidad > self.cantidad_reservada:
            raise ReservaError("Consumed quantity exceeds reserved quantity.")

        self.cantidad_transcurrida += cantidad
        logging.info(
            f"Reservation {self.id_reserva}: {self.cantidad_transcurrida}/{self.cantidad_reservada} units consumed."
        )

    def obtener_cantidad_restante(self) -> int:
        return self.cantidad_reservada - self.cantidad_transcurrida

    def obtener_desglose_costo(self, cantidad: int | None = None) -> dict:
        unidades = self.cantidad_transcurrida if cantidad is None else cantidad
        try:
            if isinstance(self.servicio, AlquilerEquipos):
                self.servicio.activar_seguro() if self.seguro_aplicado else self.servicio.desactivar_seguro()
            return self.servicio.calcular_costo(unidades)
        except Exception as exc:
            logging.error(f"Error calculating cost in reservation {self.id_reserva}: {exc}")
            raise ReservaError("Unable to calculate reservation cost.") from exc
        finally:
            if isinstance(self.servicio, AlquilerEquipos):
                self.servicio.desactivar_seguro()

    def cancelar_reserva(self) -> dict:
        try:
            if self.estado != "Pending":
                raise ReservaError(f"Cannot cancel a reservation in '{self.estado}' status.")
            if self.cantidad_transcurrida == self.cantidad_reservada:
                raise ReservaError("All reserved units have been consumed; it must be processed.")

            desglose = self.obtener_desglose_costo()
            self.estado = "Canceled"
        except ReservaError:
            logging.error(f"Cancellation rejected for reservation {self.id_reserva}.")
            raise
        except Exception as exc:
            logging.error(f"Unexpected failure canceling reservation {self.id_reserva}: {exc}")
            raise ReservaError("Error canceling reservation.") from exc
        else:
            logging.info(f"Reservation {self.id_reserva} canceled. Cost: ${desglose['total']}")
            return desglose
        finally:
            logging.info(f"Final status after canceling {self.id_reserva}: {self.estado}")

    def procesar_reserva(self) -> dict:
        try:
            if self.estado != "Pending":
                raise ReservaError(f"Cannot process a reservation in '{self.estado}' status.")
            if self.cantidad_transcurrida <= 0:
                raise ReservaError("At least one unit must be consumed before processing.")

            desglose = self.obtener_desglose_costo()
            self.estado = "Completed"
        except ReservaError:
            logging.error(f"Reservation {self.id_reserva} could not be processed.")
            raise
        except Exception as exc:
            logging.error(f"Unexpected error processing {self.id_reserva}: {exc}")
            raise ReservaError("Failed to process reservation.") from exc
        else:
            logging.info(f"Reservation {self.id_reserva} completed. Total: ${desglose['total']}")
            return desglose
        finally:
            logging.info(f"Current status of {self.id_reserva}: {self.estado}")


# --- GENERAL SYSTEM MANAGER ---
class SistemaFJ:
    """Manages lists of clients, services, and reservations without a database."""

    def __init__(self):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, cliente: Cliente) -> None:
        if any(c.identificacion == cliente.identificacion for c in self.clientes):
            raise ClienteNoValidoError(f"A client with ID '{cliente.identificacion}' already exists.")
        self.clientes.append(cliente)
        logging.info(f"Client registered: {cliente.nombre} ({cliente.identificacion})")

    def registrar_servicio(self, servicio: Servicio) -> None:
        if any(s.codigo == servicio.codigo for s in self.servicios):
            raise ErrorSistemaFJ(f"A service with code '{servicio.codigo}' already exists.")
        self.servicios.append(servicio)
        logging.info(f"Service registered: {servicio.codigo}")

    def registrar_reserva(self, reserva: Reserva) -> None:
        if any(r.id_reserva == reserva.id_reserva for r in self.reservas):
            raise ReservaError(f"Reservation '{reserva.id_reserva}' already exists.")
        if reserva.cliente not in self.clientes:
            raise ReservaError("Client is not registered in the system.")
        if reserva.servicio not in self.servicios:
            raise ReservaError("Service is not registered in the system.")
        self.reservas.append(reserva)
        logging.info(f"Reservation registered: {reserva.id_reserva}")

    def ejecutar_simulacion_10_operaciones(self) -> list[str]:
        """Simulates 10 operations (valid and invalid) without interrupting the system."""
        resultados: list[str] = []
        cliente_base: Cliente | None = None
        sala_base: ReservaSalas | None = None
        reserva_valida: Reserva | None = None

        # 1. Valid client registration (10 digits)
        try:
            cliente_base = Cliente("9001001001", "Laura Mendez", "laura.mendez@email.com")
            self.registrar_cliente(cliente_base)
            resultados.append("Op 1 [OK]: Valid client registered.")
        except ErrorSistemaFJ as exc:
            logging.error(f"Op 1 failed: {exc}")
            resultados.append(f"Op 1 [CONTROLLED ERROR]: {exc}")

        # 2. Invalid client registration (short ID < 10 digits and invalid email)
        try:
            cliente_malo = Cliente("12345", "Lu", "invalid_email")
            self.registrar_cliente(cliente_malo)
            resultados.append("Op 2 [FAIL]: Invalid client was accepted.")
        except ClienteNoValidoError as exc:
            logging.error(f"Op 2 controlled error: {exc}")
            resultados.append(f"Op 2 [CONTROLLED ERROR]: {exc}")

        # 3. Duplicate client registration
        try:
            if cliente_base is None:
                raise ClienteNoValidoError("Base client unavailable.")
            duplicado = Cliente(cliente_base.identificacion, "Other Name", "other@email.com")
            self.registrar_cliente(duplicado)
            resultados.append("Op 3 [FAIL]: Duplicate client was accepted.")
        except ClienteNoValidoError as exc:
            logging.error(f"Op 3 controlled error: {exc}")
            resultados.append(f"Op 3 [CONTROLLED ERROR]: {exc}")

        # 4. Valid service creation (Room Reservation following S001 format)
        try:
            sala_base = ReservaSalas("S002", 60.0, 12)
            self.registrar_servicio(sala_base)
            resultados.append("Op 4 [OK]: Room service (S002) registered.")
        except (ValueError, ErrorSistemaFJ) as exc:
            logging.error(f"Op 4 failed: {exc}")
            resultados.append(f"Op 4 [CONTROLLED ERROR]: {exc}")

        # 5. Invalid service creation (capacity 0)
        try:
            sala_mala = ReservaSalas("S003", 60.0, 0)
            self.registrar_servicio(sala_mala)
            resultados.append("Op 5 [FAIL]: Room with 0 capacity was accepted.")
        except ValueError as exc:
            logging.error(f"Op 5 controlled error: {exc}")
            resultados.append(f"Op 5 [CONTROLLED ERROR]: {exc}")

        # 6. Valid service creation (Equipment Rental E002 & Consulting A002)
        try:
            equipo = AlquilerEquipos("E002", 90.0, "Laptop")
            asesoria = AsesoriaEspecializada("A002", 120.0, "Cybersecurity")
            self.registrar_servicio(equipo)
            self.registrar_servicio(asesoria)
            resultados.append("Op 6 [OK]: Equipment (E002) and Consulting (A002) registered.")
        except (ValueError, ErrorSistemaFJ) as exc:
            logging.error(f"Op 6 failed: {exc}")
            resultados.append(f"Op 6 [CONTROLLED ERROR]: {exc}")

        # 7. Successful reservation created, consumed, and completed
        try:
            if cliente_base is None or sala_base is None:
                raise ReservaError("Base data missing for reservation.")
            reserva_valida = Reserva("R-SIM1", cliente_base, sala_base, 3)
            self.registrar_reserva(reserva_valida)
            reserva_valida.avanzar_tiempo(3)
            desglose = reserva_valida.procesar_reserva()
            resultados.append(f"Op 7 [OK]: Reservation R-SIM1 completed. Total: ${desglose['total']}")
        except Exception as exc:
            logging.error(f"Op 7 failed: {exc}")
            resultados.append(f"Op 7 [CONTROLLED ERROR]: {exc}")

        # 8. Failed reservation due to unregistered client
        try:
            cliente_no_reg = Cliente("8888888888", "Peter Unregistered", "peter@email.com")
            if sala_base is None:
                raise ReservaError("Service unavailable.")
            res_sin_cli = Reserva("R-SIM2", cliente_no_reg, sala_base, 2)
            self.registrar_reserva(res_sin_cli)
            resultados.append("Op 8 [FAIL]: Reservation with unregistered client was accepted.")
        except ReservaError as exc:
            logging.error(f"Op 8 controlled error: {exc}")
            resultados.append(f"Op 8 [CONTROLLED ERROR]: {exc}")

        # 9. Failed reservation due to processing without consumption
        try:
            if cliente_base is None or sala_base is None:
                raise ReservaError("Data unavailable.")
            res_sin_uso = Reserva("R-SIM3", cliente_base, sala_base, 2)
            self.registrar_reserva(res_sin_uso)
            res_sin_uso.procesar_reserva()
            resultados.append("Op 9 [FAIL]: Reservation processed without consumption.")
        except ReservaError as exc:
            logging.error(f"Op 9 controlled error: {exc}")
            resultados.append(f"Op 9 [CONTROLLED ERROR]: {exc}")

        # 10. Attempt to cancel an already completed reservation
        try:
            if reserva_valida is None:
                raise ReservaError("Base reservation unavailable.")
            reserva_valida.cancelar_reserva()
            resultados.append("Op 10 [FAIL]: Completed reservation was canceled.")
        except ReservaError as exc:
            logging.error(f"Op 10 controlled error: {exc}")
            resultados.append(f"Op 10 [CONTROLLED ERROR]: {exc}")

        return resultados


# --- TKINTER GUI (100% IN ENGLISH) ---
class SistemaFJApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Software FJ - Integral Management System")
        self.root.geometry("920x700")
        self.sistema = SistemaFJ()
        self.reserva_seleccionada: Reserva | None = None
        self.servicios_por_opcion: dict[str, Servicio] = {}
        self.reservas_por_opcion: dict[str, Reserva] = {}

        self._cargar_datos_iniciales()
        self._construir_interfaz()

    def _cargar_datos_iniciales(self) -> None:
        try:
            for c in [
                Cliente("1000000001", "Ana Perez", "ana@gmail.com"),
                Cliente("1000000002", "Carlos Gomez", "carlos@gmail.com"),
            ]:
                self.sistema.registrar_cliente(c)

            for s in [
                ReservaSalas("S001", 50.0, 10),
                AlquilerEquipos("E001", 100.0, "Projector"),
                AsesoriaEspecializada("A001", 80.0, "Software Architecture"),
            ]:
                self.sistema.registrar_servicio(s)
        except ErrorSistemaFJ as exc:
            logging.error(f"Error loading initial data: {exc}")

    def _construir_interfaz(self) -> None:
        titulo = ttk.Label(
            self.root,
            text="Client, Service, and Reservation Management System - Software FJ",
            font=("Arial", 14, "bold"),
        )
        titulo.pack(pady=10)

        contenedor = ttk.Frame(self.root, padding=10)
        contenedor.pack(fill="both", expand=True)
        contenedor.columnconfigure(0, weight=1)
        contenedor.columnconfigure(1, weight=1)

        self._crear_panel_clientes(contenedor)
        self._crear_panel_reservas(contenedor)
        self._crear_panel_resultados()
        self._actualizar_combos()

    def _crear_panel_clientes(self, contenedor: ttk.Frame) -> None:
        frame = ttk.LabelFrame(contenedor, text="Client Registration", padding=12)
        frame.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        ttk.Label(frame, text="ID Number (min 10 digits):").grid(row=0, column=0, sticky="w", pady=4)
        self.txt_id = ttk.Entry(frame, width=26)
        self.txt_id.grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Full Name:").grid(row=1, column=0, sticky="w", pady=4)
        self.txt_nombre = ttk.Entry(frame, width=26)
        self.txt_nombre.grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Email Address:").grid(row=2, column=0, sticky="w", pady=4)
        self.txt_correo = ttk.Entry(frame, width=26)
        self.txt_correo.grid(row=2, column=1, pady=4)

        ttk.Button(frame, text="Register Client", command=self.accion_registrar_cliente).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        ttk.Separator(frame).grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Button(frame, text="Run 10 Simulation Tests", command=self.accion_ejecutar_10_pruebas).grid(
            row=5, column=0, columnspan=2, pady=6
        )

    def _crear_panel_reservas(self, contenedor: ttk.Frame) -> None:
        frame = ttk.LabelFrame(contenedor, text="Reservation Management", padding=12)
        frame.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        ttk.Label(frame, text="Client:").grid(row=0, column=0, sticky="w", pady=4)
        self.cmb_clientes = ttk.Combobox(frame, width=24, state="readonly")
        self.cmb_clientes.grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Service:").grid(row=1, column=0, sticky="w", pady=4)
        self.cmb_servicios = ttk.Combobox(frame, width=24, state="readonly")
        self.cmb_servicios.grid(row=1, column=1, pady=4)
        self.cmb_servicios.bind("<<ComboboxSelected>>", self.actualizar_info_servicio)

        self.lbl_info_servicio = ttk.Label(frame, text="Select a service.")
        self.lbl_info_servicio.grid(row=2, column=0, columnspan=2, pady=4)

        ttk.Label(frame, text="Quantity to reserve:").grid(row=3, column=0, sticky="w", pady=4)
        self.txt_cantidad = ttk.Entry(frame, width=26)
        self.txt_cantidad.grid(row=3, column=1, pady=4)

        self.var_seguro = tk.BooleanVar(value=False)
        self.chk_seguro = ttk.Checkbutton(
            frame, text="Additional insurance (+$15)", variable=self.var_seguro, state="disabled"
        )
        self.chk_seguro.grid(row=4, column=0, columnspan=2, pady=4)

        ttk.Button(frame, text="Create Reservation", command=self.accion_crear_reserva).grid(
            row=5, column=0, columnspan=2, pady=8
        )

        ttk.Separator(frame).grid(row=6, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(frame, text="Active Reservation:").grid(row=7, column=0, sticky="w", pady=4)
        self.cmb_reservas = ttk.Combobox(frame, width=24, state="readonly")
        self.cmb_reservas.grid(row=7, column=1, pady=4)
        self.cmb_reservas.bind("<<ComboboxSelected>>", self.seleccionar_reserva)

        ttk.Label(frame, text="Units to consume:").grid(row=8, column=0, sticky="w", pady=4)
        self.txt_consumo = ttk.Entry(frame, width=26)
        self.txt_consumo.insert(0, "1")
        self.txt_consumo.grid(row=8, column=1, pady=4)

        ttk.Button(frame, text="Advance Consumption", command=self.accion_avanzar_consumo).grid(
            row=9, column=0, columnspan=2, pady=4
        )
        ttk.Button(frame, text="Process / Complete", command=self.accion_procesar_reserva).grid(
            row=10, column=0, columnspan=2, pady=4
        )
        ttk.Button(frame, text="Cancel Reservation", command=self.accion_cancelar_reserva).grid(
            row=11, column=0, columnspan=2, pady=4
        )

    def _crear_panel_resultados(self) -> None:
        frame = ttk.LabelFrame(self.root, text="Results and Events Console", padding=10)
        frame.pack(fill="both", expand=True, padx=16, pady=10)

        self.txt_resultados = tk.Text(frame, height=11, state="disabled")
        self.txt_resultados.pack(fill="both", expand=True)

    def _actualizar_combos(self) -> None:
        self.cmb_clientes["values"] = [c.nombre for c in self.sistema.clientes]
        self.servicios_por_opcion = {
            f"{s.nombre_servicio} ({s.codigo})": s for s in self.sistema.servicios
        }
        self.cmb_servicios["values"] = list(self.servicios_por_opcion.keys())
        self._actualizar_combo_reservas()

    def _actualizar_combo_reservas(self) -> None:
        self.reservas_por_opcion = {
            f"{r.id_reserva} | {r.cliente.nombre} | {r.estado} | {r.cantidad_transcurrida}/{r.cantidad_reservada}": r
            for r in self.sistema.reservas
        }
        self.cmb_reservas["values"] = list(self.reservas_por_opcion.keys())

    def actualizar_info_servicio(self, event=None) -> None:
        servicio = self.servicios_por_opcion.get(self.cmb_servicios.get())
        if servicio is None:
            return
        self.lbl_info_servicio.config(text=f"Base cost: ${servicio.costo_base} | {servicio.nombre_servicio}")
        if isinstance(servicio, AlquilerEquipos):
            self.chk_seguro.config(state="normal")
        else:
            self.var_seguro.set(False)
            self.chk_seguro.config(state="disabled")

    def accion_ejecutar_10_pruebas(self) -> None:
        lineas = self.sistema.ejecutar_simulacion_10_operaciones()
        self._actualizar_combos()
        self._mostrar_mensaje("--- 10 OPERATIONS SIMULATION ---\n" + "\n".join(lineas))

    def accion_registrar_cliente(self) -> None:
        try:
            cliente = Cliente(self.txt_id.get(), self.txt_nombre.get(), self.txt_correo.get())
            self.sistema.registrar_cliente(cliente)
            self._actualizar_combos()
            self.txt_id.delete(0, tk.END)
            self.txt_nombre.delete(0, tk.END)
            self.txt_correo.delete(0, tk.END)
            self._mostrar_mensaje(f"Client registered: {cliente.obtener_detalles()}")
        except Exception as exc:
            logging.error(f"Error registering client in GUI: {exc}")
            self._mostrar_mensaje(f"Error registering client: {exc}")

    def accion_crear_reserva(self) -> None:
        try:
            nombre_cli = self.cmb_clientes.get()
            opcion_srv = self.cmb_servicios.get()
            cant_texto = self.txt_cantidad.get().strip()

            if not nombre_cli or not opcion_srv or not cant_texto:
                raise ReservaError("Please select client, service, and enter quantity.")

            cantidad = int(cant_texto)
            cliente = next(c for c in self.sistema.clientes if c.nombre == nombre_cli)
            servicio = self.servicios_por_opcion[opcion_srv]
            seguro = isinstance(servicio, AlquilerEquipos) and self.var_seguro.get()

            reserva = Reserva(
                f"R-{len(self.sistema.reservas) + 1:03d}",
                cliente,
                servicio,
                cantidad,
                seguro_aplicado=seguro,
            )
            desglose = reserva.obtener_desglose_costo(cantidad)
            self.sistema.registrar_reserva(reserva)
            self._actualizar_combo_reservas()
            self.txt_cantidad.delete(0, tk.END)
            self.var_seguro.set(False)
            self._mostrar_mensaje(self._formatear_desglose(reserva, desglose, "RESERVATION CREATED (ESTIMATED)"))
        except ValueError as exc:
            logging.error(f"Invalid quantity when creating reservation: {exc}")
            self._mostrar_mensaje("Error: Quantity to reserve must be an integer.")
        except Exception as exc:
            logging.error(f"Error creating reservation in GUI: {exc}")
            self._mostrar_mensaje(f"Error creating reservation: {exc}")

    def seleccionar_reserva(self, event=None) -> None:
        self.reserva_seleccionada = self.reservas_por_opcion.get(self.cmb_reservas.get())
        if self.reserva_seleccionada:
            r = self.reserva_seleccionada
            self._mostrar_mensaje(
                f"Reservation {r.id_reserva} selected | Status: {r.estado} | "
                f"Consumed: {r.cantidad_transcurrida}/{r.cantidad_reservada} | "
                f"Remaining: {r.obtener_cantidad_restante()}"
            )

    def accion_avanzar_consumo(self) -> None:
        try:
            if self.reserva_seleccionada is None:
                raise ReservaError("Please select a reservation first.")
            unidades = int(self.txt_consumo.get().strip())
            self.reserva_seleccionada.avanzar_tiempo(unidades)
            self._actualizar_combo_reservas()
            r = self.reserva_seleccionada
            self._mostrar_mensaje(
                f"Consumption updated in {r.id_reserva}: {r.cantidad_transcurrida}/{r.cantidad_reservada}."
            )
        except ValueError:
            self._mostrar_mensaje("Error: Enter a valid integer to consume.")
        except Exception as exc:
            logging.error(f"Error advancing consumption: {exc}")
            self._mostrar_mensaje(f"Error: {exc}")

    def accion_procesar_reserva(self) -> None:
        try:
            if self.reserva_seleccionada is None:
                raise ReservaError("Please select a reservation first.")
            desglose = self.reserva_seleccionada.procesar_reserva()
            self._actualizar_combo_reservas()
            self._mostrar_mensaje(
                self._formatear_desglose(self.reserva_seleccionada, desglose, "RESERVATION COMPLETED")
            )
        except Exception as exc:
            logging.error(f"Error processing reservation: {exc}")
            self._mostrar_mensaje(f"Error: {exc}")

    def accion_cancelar_reserva(self) -> None:
        try:
            if self.reserva_seleccionada is None:
                raise ReservaError("Please select a reservation first.")
            desglose = self.reserva_seleccionada.cancelar_reserva()
            self._actualizar_combo_reservas()
            self._mostrar_mensaje(
                self._formatear_desglose(self.reserva_seleccionada, desglose, "RESERVATION CANCELED")
            )
        except Exception as exc:
            logging.error(f"Error canceling reservation: {exc}")
            self._mostrar_mensaje(f"Error: {exc}")

    def _formatear_desglose(self, reserva: Reserva, desglose: dict, encabezado: str) -> str:
        return (
            f"=== {encabezado} ({reserva.id_reserva}) ===\n"
            f"Client: {reserva.cliente.nombre} | Service: {reserva.servicio.nombre_servicio}\n"
            f"Subtotal: ${desglose['subtotal']} | Discount ({desglose['porcentaje_descuento']}%): -${desglose['descuento']}\n"
            f"Insurance: ${desglose['seguro']} | Tax: ${desglose['impuesto']} | TOTAL: ${desglose['total']}"
        )

    def _mostrar_mensaje(self, texto: str) -> None:
        self.txt_resultados.config(state="normal")
        self.txt_resultados.insert(tk.END, texto + "\n")
        self.txt_resultados.see(tk.END)
        self.txt_resultados.config(state="disabled")


def main() -> None:
    root = tk.Tk()
    SistemaFJApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
