from __future__ import annotations
from abc import ABC, abstractmethod
import logging
import tkinter as tk
from tkinter import ttk

# Configuración del archivo de logs para eventos y errores
logging.basicConfig(
    filename="sistema_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


# --- EXCEPCIONES PERSONALIZADAS ---
class ErrorSistemaFJ(Exception):
    """Excepción base del sistema Software FJ."""


class ClienteNoValidoError(ErrorSistemaFJ):
    """Error por datos inválidos o duplicados de cliente."""


class ReservaError(ErrorSistemaFJ):
    """Error por operación inválida, estado o cálculo de reserva."""


# --- CLASE ABSTRACTA GENERAL ---
class EntidadBase(ABC):
    """Clase abstracta base para entidades del sistema."""

    @abstractmethod
    def obtener_detalles(self) -> str:
        pass


# --- CLASE CLIENTE ---
class Cliente(EntidadBase):
    """Representa un cliente con datos personales encapsulados y validados."""

    def __init__(self, identificacion: str, nombre: str, correo: str):
        self.__identificacion = self.__validar_id(identificacion)
        self.__nombre = self.__validar_nombre(nombre)
        self.__correo = self.__validar_correo(correo)

    def __validar_id(self, identificacion: str) -> str:
        if not isinstance(identificacion, str) or not identificacion.strip().isdigit():
            raise ClienteNoValidoError("La identificación debe contener solo números.")
        return identificacion.strip()

    def __validar_nombre(self, nombre: str) -> str:
        if not isinstance(nombre, str) or len(nombre.strip()) < 3:
            raise ClienteNoValidoError("El nombre debe tener al menos 3 caracteres.")
        return nombre.strip()

    def __validar_correo(self, correo: str) -> str:
        if not isinstance(correo, str) or correo.count("@") != 1:
            raise ClienteNoValidoError("El correo debe contener un único símbolo @.")
        usuario, dominio = correo.strip().split("@")
        if not usuario or not dominio or "." not in dominio:
            raise ClienteNoValidoError("El correo debe tener usuario y dominio válido.")
        partes = dominio.split(".")
        if any(not parte or parte.isspace() for parte in partes) or any(c.isspace() for c in usuario):
            raise ClienteNoValidoError("El correo no puede tener espacios ni puntos inválidos.")
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
        return f"Cliente: {self.__nombre} | ID: {self.__identificacion} | Correo: {self.__correo}"

    def __str__(self) -> str:
        return f"{self.__nombre} (ID: {self.__identificacion})"


# --- CLASE ABSTRACTA SERVICIO Y DERIVADAS ---
class Servicio(EntidadBase, ABC):
    """Clase abstracta para los servicios de Software FJ."""

    def __init__(self, codigo: str, nombre_servicio: str, costo_base: float):
        if not codigo or not codigo.strip():
            raise ValueError("El código del servicio es obligatorio.")
        if not isinstance(costo_base, (int, float)) or isinstance(costo_base, bool) or costo_base <= 0:
            raise ValueError("El costo base debe ser un número mayor a cero.")
        self.codigo = codigo.strip()
        self.nombre_servicio = nombre_servicio.strip()
        self.costo_base = float(costo_base)

    @abstractmethod
    def calcular_costo(self, cantidad: int, descuento: float | None = None, **kwargs) -> dict:
        pass


class ReservaSalas(Servicio):
    """Servicio especializado de reserva de salas."""

    def __init__(self, codigo: str, costo_base: float, capacidad: int):
        super().__init__(codigo, "Reserva de Sala", costo_base)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ValueError("La capacidad de la sala debe ser un entero positivo.")
        self.capacidad = capacidad

    def calcular_costo(self, cantidad: int, descuento: float | None = None, **kwargs) -> dict:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError("Las horas deben ser un entero mayor o igual a cero.")

        if descuento is None:
            descuento = 0.15 if cantidad >= 5 else (0.10 if cantidad >= 3 else 0.0)

        if not isinstance(descuento, (int, float)) or isinstance(descuento, bool) or not (0 <= descuento < 1):
            raise ValueError("El descuento debe estar entre 0 y 1 (exclusivo).")

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
        return f"[Sala] {self.nombre_servicio} ({self.codigo}) - Capacidad: {self.capacidad} - ${self.costo_base}/h"


class AlquilerEquipos(Servicio):
    """Servicio especializado de alquiler de equipos."""

    def __init__(self, codigo: str, costo_base: float, tipo_equipo: str):
        super().__init__(codigo, "Alquiler de Equipo", costo_base)
        if not tipo_equipo or not tipo_equipo.strip():
            raise ValueError("El tipo de equipo es obligatorio.")
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
            raise ValueError("Los días deben ser un entero mayor o igual a cero.")

        if descuento is None:
            descuento = 0.15 if cantidad >= 5 else (0.10 if cantidad >= 3 else 0.0)

        if not isinstance(descuento, (int, float)) or isinstance(descuento, bool) or not (0 <= descuento < 1):
            raise ValueError("El descuento debe estar entre 0 y 1 (exclusivo).")

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
        return f"[Equipo] {self.tipo_equipo} ({self.codigo}) - ${self.costo_base}/día"


class AsesoriaEspecializada(Servicio):
    """Servicio especializado de asesorías especializadas."""

    def __init__(self, codigo: str, costo_base: float, area: str):
        super().__init__(codigo, "Asesoría Especializada", costo_base)
        if not area or not area.strip():
            raise ValueError("El área de asesoría es obligatoria.")
        self.area = area.strip()

    def calcular_costo(
        self,
        cantidad: int,
        descuento: float | None = None,
        impuesto: float = 0.19,
        **kwargs,
    ) -> dict:
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad < 0:
            raise ValueError("Las sesiones deben ser un entero mayor o igual a cero.")

        if descuento is None:
            descuento = 0.10 if cantidad >= 5 else (0.05 if cantidad >= 3 else 0.0)

        if not isinstance(descuento, (int, float)) or isinstance(descuento, bool) or not (0 <= descuento < 1):
            raise ValueError("El descuento debe estar entre 0 y 1 (exclusivo).")
        if not isinstance(impuesto, (int, float)) or isinstance(impuesto, bool) or impuesto < 0:
            raise ValueError("El impuesto debe ser un número mayor o igual a cero.")

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
        return f"[Asesoría] {self.area} ({self.codigo}) - ${self.costo_base}/sesión"


# --- CLASE RESERVA ---
class Reserva:
    """Integra cliente, servicio, duración y estado con control de excepciones."""

    def __init__(
        self,
        id_reserva: str,
        cliente: Cliente,
        servicio: Servicio,
        cantidad_reservada: int,
        seguro_aplicado: bool = False,
    ):
        if not id_reserva or not id_reserva.strip():
            raise ReservaError("El ID de la reserva es obligatorio.")
        if not isinstance(cantidad_reservada, int) or isinstance(cantidad_reservada, bool) or cantidad_reservada <= 0:
            raise ReservaError("La cantidad reservada debe ser un entero positivo.")

        self.id_reserva = id_reserva.strip()
        self.cliente = cliente
        self.servicio = servicio
        self.cantidad_reservada = cantidad_reservada
        self.cantidad_transcurrida = 0
        self.seguro_aplicado = seguro_aplicado
        self.estado = "Pendiente"

    def avanzar_tiempo(self, cantidad: int) -> None:
        if self.estado != "Pendiente":
            raise ReservaError(f"No se puede avanzar consumo en estado '{self.estado}'.")
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValueError("La cantidad a consumir debe ser un entero positivo.")
        if self.cantidad_transcurrida + cantidad > self.cantidad_reservada:
            raise ReservaError("La cantidad consumida supera la cantidad reservada.")

        self.cantidad_transcurrida += cantidad
        logging.info(
            f"Reserva {self.id_reserva}: {self.cantidad_transcurrida}/{self.cantidad_reservada} consumidas."
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
            logging.error(f"Error calculando costo en reserva {self.id_reserva}: {exc}")
            raise ReservaError("No fue posible calcular el costo de la reserva.") from exc
        finally:
            if isinstance(self.servicio, AlquilerEquipos):
                self.servicio.desactivar_seguro()

    def cancelar_reserva(self) -> dict:
        try:
            if self.estado != "Pendiente":
                raise ReservaError(f"No se puede cancelar una reserva en estado '{self.estado}'.")
            if self.cantidad_transcurrida == self.cantidad_reservada:
                raise ReservaError("La reserva ya consumió todas sus unidades; debe procesarse.")

            desglose = self.obtener_desglose_costo()
            self.estado = "Cancelada"
        except ReservaError:
            logging.error(f"Cancelación rechazada en reserva {self.id_reserva}.")
            raise
        except Exception as exc:
            logging.error(f"Fallo inesperado cancelando reserva {self.id_reserva}: {exc}")
            raise ReservaError("Error al cancelar la reserva.") from exc
        else:
            logging.info(f"Reserva {self.id_reserva} cancelada. Costo: ${desglose['total']}")
            return desglose
        finally:
            logging.info(f"Estado final tras cancelar {self.id_reserva}: {self.estado}")

    def procesar_reserva(self) -> dict:
        try:
            if self.estado != "Pendiente":
                raise ReservaError(f"No se puede procesar una reserva en estado '{self.estado}'.")
            if self.cantidad_transcurrida <= 0:
                raise ReservaError("Debe consumir al menos una unidad antes de procesar la reserva.")

            desglose = self.obtener_desglose_costo()
            self.estado = "Finalizada"
        except ReservaError:
            logging.error(f"Reserva {self.id_reserva} no pudo procesarse.")
            raise
        except Exception as exc:
            logging.error(f"Error inesperado procesando {self.id_reserva}: {exc}")
            raise ReservaError("Fallo al procesar la reserva.") from exc
        else:
            logging.info(f"Reserva {self.id_reserva} finalizada. Total: ${desglose['total']}")
            return desglose
        finally:
            logging.info(f"Estado actual de {self.id_reserva}: {self.estado}")


# --- GESTOR GENERAL ---
class SistemaFJ:
    """Gestiona listas de clientes, servicios y reservas sin base de datos."""

    def __init__(self):
        self.clientes: list[Cliente] = []
        self.servicios: list[Servicio] = []
        self.reservas: list[Reserva] = []

    def registrar_cliente(self, cliente: Cliente) -> None:
        if any(c.identificacion == cliente.identificacion for c in self.clientes):
            raise ClienteNoValidoError(f"Ya existe un cliente con ID '{cliente.identificacion}'.")
        self.clientes.append(cliente)
        logging.info(f"Cliente registrado: {cliente.nombre} ({cliente.identificacion})")

    def registrar_servicio(self, servicio: Servicio) -> None:
        if any(s.codigo == servicio.codigo for s in self.servicios):
            raise ErrorSistemaFJ(f"Ya existe un servicio con código '{servicio.codigo}'.")
        self.servicios.append(servicio)
        logging.info(f"Servicio registrado: {servicio.codigo}")

    def registrar_reserva(self, reserva: Reserva) -> None:
        if any(r.id_reserva == reserva.id_reserva for r in self.reservas):
            raise ReservaError(f"Ya existe la reserva '{reserva.id_reserva}'.")
        if reserva.cliente not in self.clientes:
            raise ReservaError("El cliente no está registrado.")
        if reserva.servicio not in self.servicios:
            raise ReservaError("El servicio no está registrado.")
        self.reservas.append(reserva)
        logging.info(f"Reserva registrada: {reserva.id_reserva}")

    def ejecutar_simulacion_10_operaciones(self) -> list[str]:
        """Simula 10 operaciones (válidas e inválidas) sin interrumpir el sistema."""
        resultados: list[str] = []
        cliente_base: Cliente | None = None
        sala_base: ReservaSalas | None = None
        reserva_valida: Reserva | None = None

        # 1. Registro válido de cliente
        try:
            cliente_base = Cliente("9001001", "Laura Méndez", "laura.mendez@correo.com")
            self.registrar_cliente(cliente_base)
            resultados.append("Op 1 [OK]: Cliente válido registrado.")
        except ErrorSistemaFJ as exc:
            logging.error(f"Op 1 falló: {exc}")
            resultados.append(f"Op 1 [ERROR CONTROLADO]: {exc}")

        # 2. Registro inválido de cliente (ID no numérico y correo sin @)
        try:
            cliente_malo = Cliente("ID-X", "Lu", "correo_invalido")
            self.registrar_cliente(cliente_malo)
            resultados.append("Op 2 [FALLO]: Se aceptó cliente inválido.")
        except ClienteNoValidoError as exc:
            logging.error(f"Op 2 error controlado: {exc}")
            resultados.append(f"Op 2 [ERROR CONTROLADO]: {exc}")

        # 3. Registro duplicado de cliente
        try:
            if cliente_base is None:
                raise ClienteNoValidoError("Cliente base no disponible.")
            duplicado = Cliente(cliente_base.identificacion, "Otro Nombre", "otro@correo.com")
            self.registrar_cliente(duplicado)
            resultados.append("Op 3 [FALLO]: Se aceptó cliente duplicado.")
        except ClienteNoValidoError as exc:
            logging.error(f"Op 3 error controlado: {exc}")
            resultados.append(f"Op 3 [ERROR CONTROLADO]: {exc}")

        # 4. Creación correcta de servicio (Reserva de Sala)
        try:
            sala_base = ReservaSalas("SAL-10", 60.0, 12)
            self.registrar_servicio(sala_base)
            resultados.append("Op 4 [OK]: Servicio de sala registrado.")
        except (ValueError, ErrorSistemaFJ) as exc:
            logging.error(f"Op 4 falló: {exc}")
            resultados.append(f"Op 4 [ERROR CONTROLADO]: {exc}")

        # 5. Creación incorrecta de servicio (capacidad inválida)
        try:
            sala_mala = ReservaSalas("SAL-ERR", 60.0, 0)
            self.registrar_servicio(sala_mala)
            resultados.append("Op 5 [FALLO]: Se aceptó sala con capacidad 0.")
        except ValueError as exc:
            logging.error(f"Op 5 error controlado: {exc}")
            resultados.append(f"Op 5 [ERROR CONTROLADO]: {exc}")

        # 6. Creación correcta de servicio (Alquiler de Equipo y Asesoría)
        try:
            equipo = AlquilerEquipos("EQ-10", 90.0, "Portátil")
            asesoria = AsesoriaEspecializada("ASE-10", 120.0, "Seguridad Informática")
            self.registrar_servicio(equipo)
            self.registrar_servicio(asesoria)
            resultados.append("Op 6 [OK]: Servicios de equipo y asesoría registrados.")
        except (ValueError, ErrorSistemaFJ) as exc:
            logging.error(f"Op 6 falló: {exc}")
            resultados.append(f"Op 6 [ERROR CONTROLADO]: {exc}")

        # 7. Reserva exitosa y procesada con consumo previo
        try:
            if cliente_base is None or sala_base is None:
                raise ReservaError("Faltan datos base para la reserva.")
            reserva_valida = Reserva("SIM-001", cliente_base, sala_base, 3)
            self.registrar_reserva(reserva_valida)
            reserva_valida.avanzar_tiempo(3)
            desglose = reserva_valida.procesar_reserva()
            resultados.append(f"Op 7 [OK]: Reserva SIM-001 finalizada. Total: ${desglose['total']}")
        except Exception as exc:
            logging.error(f"Op 7 falló: {exc}")
            resultados.append(f"Op 7 [ERROR CONTROLADO]: {exc}")

        # 8. Reserva fallida por cliente no registrado
        try:
            cliente_no_reg = Cliente("8888888", "Pedro Sin Registro", "pedro@correo.com")
            if sala_base is None:
                raise ReservaError("Servicio no disponible.")
            res_sin_cli = Reserva("SIM-002", cliente_no_reg, sala_base, 2)
            self.registrar_reserva(res_sin_cli)
            resultados.append("Op 8 [FALLO]: Se registró reserva de cliente no inscrito.")
        except ReservaError as exc:
            logging.error(f"Op 8 error controlado: {exc}")
            resultados.append(f"Op 8 [ERROR CONTROLADO]: {exc}")

        # 9. Reserva fallida por intentar procesar sin consumo
        try:
            if cliente_base is None or sala_base is None:
                raise ReservaError("Datos no disponibles.")
            res_sin_uso = Reserva("SIM-003", cliente_base, sala_base, 2)
            self.registrar_reserva(res_sin_uso)
            res_sin_uso.procesar_reserva()
            resultados.append("Op 9 [FALLO]: Se procesó reserva sin consumo.")
        except ReservaError as exc:
            logging.error(f"Op 9 error controlado: {exc}")
            resultados.append(f"Op 9 [ERROR CONTROLADO]: {exc}")

        # 10. Intento de cancelar reserva ya finalizada
        try:
            if reserva_valida is None:
                raise ReservaError("Reserva base no disponible.")
            reserva_valida.cancelar_reserva()
            resultados.append("Op 10 [FALLO]: Se canceló reserva ya finalizada.")
        except ReservaError as exc:
            logging.error(f"Op 10 error controlado: {exc}")
            resultados.append(f"Op 10 [ERROR CONTROLADO]: {exc}")

        return resultados


# --- INTERFAZ TKINTER ---
class SistemaFJApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Sistema Integral Software FJ")
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
                Cliente("10000001", "Ana Perez", "ana@gmail.com"),
                Cliente("10000002", "Carlos Gomez", "carlos@gmail.com"),
            ]:
                self.sistema.registrar_cliente(c)

            for s in [
                ReservaSalas("S001", 50.0, 10),
                AlquilerEquipos("E001", 100.0, "Proyector"),
                AsesoriaEspecializada("A001", 80.0, "Arquitectura de Software"),
            ]:
                self.sistema.registrar_servicio(s)
        except ErrorSistemaFJ as exc:
            logging.error(f"Error cargando datos iniciales: {exc}")

    def _construir_interfaz(self) -> None:
        titulo = ttk.Label(
            self.root,
            text="Sistema de Gestión de Clientes, Servicios y Reservas - Software FJ",
            font=("Arial", 15, "bold"),
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
        frame = ttk.LabelFrame(contenedor, text="Registro de Clientes", padding=12)
        frame.grid(row=0, column=0, padx=6, pady=6, sticky="nsew")

        ttk.Label(frame, text="Identificación:").grid(row=0, column=0, sticky="w", pady=4)
        self.txt_id = ttk.Entry(frame, width=26)
        self.txt_id.grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Nombre:").grid(row=1, column=0, sticky="w", pady=4)
        self.txt_nombre = ttk.Entry(frame, width=26)
        self.txt_nombre.grid(row=1, column=1, pady=4)

        ttk.Label(frame, text="Correo:").grid(row=2, column=0, sticky="w", pady=4)
        self.txt_correo = ttk.Entry(frame, width=26)
        self.txt_correo.grid(row=2, column=1, pady=4)

        ttk.Button(frame, text="Registrar Cliente", command=self.accion_registrar_cliente).grid(
            row=3, column=0, columnspan=2, pady=10
        )

        ttk.Separator(frame).grid(row=4, column=0, columnspan=2, sticky="ew", pady=10)

        ttk.Button(frame, text="Ejecutar 10 Pruebas", command=self.accion_ejecutar_10_pruebas).grid(
            row=5, column=0, columnspan=2, pady=6
        )

    def _crear_panel_reservas(self, contenedor: ttk.Frame) -> None:
        frame = ttk.LabelFrame(contenedor, text="Gestión de Reservas", padding=12)
        frame.grid(row=0, column=1, padx=6, pady=6, sticky="nsew")

        ttk.Label(frame, text="Cliente:").grid(row=0, column=0, sticky="w", pady=4)
        self.cmb_clientes = ttk.Combobox(frame, width=24, state="readonly")
        self.cmb_clientes.grid(row=0, column=1, pady=4)

        ttk.Label(frame, text="Servicio:").grid(row=1, column=0, sticky="w", pady=4)
        self.cmb_servicios = ttk.Combobox(frame, width=24, state="readonly")
        self.cmb_servicios.grid(row=1, column=1, pady=4)
        self.cmb_servicios.bind("<<ComboboxSelected>>", self.actualizar_info_servicio)

        self.lbl_info_servicio = ttk.Label(frame, text="Seleccione un servicio.")
        self.lbl_info_servicio.grid(row=2, column=0, columnspan=2, pady=4)

        ttk.Label(frame, text="Cantidad a reservar:").grid(row=3, column=0, sticky="w", pady=4)
        self.txt_cantidad = ttk.Entry(frame, width=26)
        self.txt_cantidad.grid(row=3, column=1, pady=4)

        self.var_seguro = tk.BooleanVar(value=False)
        self.chk_seguro = ttk.Checkbutton(
            frame, text="Seguro adicional (+$15)", variable=self.var_seguro, state="disabled"
        )
        self.chk_seguro.grid(row=4, column=0, columnspan=2, pady=4)

        ttk.Button(frame, text="Crear Reserva", command=self.accion_crear_reserva).grid(
            row=5, column=0, columnspan=2, pady=8
        )

        ttk.Separator(frame).grid(row=6, column=0, columnspan=2, sticky="ew", pady=8)

        ttk.Label(frame, text="Reserva activa:").grid(row=7, column=0, sticky="w", pady=4)
        self.cmb_reservas = ttk.Combobox(frame, width=24, state="readonly")
        self.cmb_reservas.grid(row=7, column=1, pady=4)
        self.cmb_reservas.bind("<<ComboboxSelected>>", self.seleccionar_reserva)

        ttk.Label(frame, text="Unidades a consumir:").grid(row=8, column=0, sticky="w", pady=4)
        self.txt_consumo = ttk.Entry(frame, width=26)
        self.txt_consumo.insert(0, "1")
        self.txt_consumo.grid(row=8, column=1, pady=4)

        ttk.Button(frame, text="Avanzar Consumo", command=self.accion_avanzar_consumo).grid(
            row=9, column=0, columnspan=2, pady=4
        )
        ttk.Button(frame, text="Procesar / Finalizar", command=self.accion_procesar_reserva).grid(
            row=10, column=0, columnspan=2, pady=4
        )
        ttk.Button(frame, text="Cancelar Reserva", command=self.accion_cancelar_reserva).grid(
            row=11, column=0, columnspan=2, pady=4
        )

    def _crear_panel_resultados(self) -> None:
        frame = ttk.LabelFrame(self.root, text="Resultados y Eventos", padding=10)
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
        self.lbl_info_servicio.config(text=f"Costo base: ${servicio.costo_base} | {servicio.nombre_servicio}")
        if isinstance(servicio, AlquilerEquipos):
            self.chk_seguro.config(state="normal")
        else:
            self.var_seguro.set(False)
            self.chk_seguro.config(state="disabled")

    def accion_ejecutar_10_pruebas(self) -> None:
        lineas = self.sistema.ejecutar_simulacion_10_operaciones()
        self._actualizar_combos()
        self._mostrar_mensaje("--- SIMULACIÓN DE 10 OPERACIONES ---\n" + "\n".join(lineas))

    def accion_registrar_cliente(self) -> None:
        try:
            cliente = Cliente(self.txt_id.get(), self.txt_nombre.get(), self.txt_correo.get())
            self.sistema.registrar_cliente(cliente)
            self._actualizar_combos()
            self.txt_id.delete(0, tk.END)
            self.txt_nombre.delete(0, tk.END)
            self.txt_correo.delete(0, tk.END)
            self._mostrar_mensaje(f"Cliente registrado: {cliente.obtener_detalles()}")
        except Exception as exc:
            logging.error(f"Error al registrar cliente en GUI: {exc}")
            self._mostrar_mensaje(f"Error al registrar cliente: {exc}")

    def accion_crear_reserva(self) -> None:
        try:
            nombre_cli = self.cmb_clientes.get()
            opcion_srv = self.cmb_servicios.get()
            cant_texto = self.txt_cantidad.get().strip()

            if not nombre_cli or not opcion_srv or not cant_texto:
                raise ReservaError("Debe seleccionar cliente, servicio e ingresar cantidad.")

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
            self._mostrar_mensaje(self._formatear_desglose(reserva, desglose, "RESERVA CREADA (ESTIMADO)"))
        except ValueError as exc:
            logging.error(f"Cantidad inválida al crear reserva: {exc}")
            self._mostrar_mensaje("Error: la cantidad a reservar debe ser un número entero.")
        except Exception as exc:
            logging.error(f"Error al crear reserva en GUI: {exc}")
            self._mostrar_mensaje(f"Error al crear reserva: {exc}")

    def seleccionar_reserva(self, event=None) -> None:
        self.reserva_seleccionada = self.reservas_por_opcion.get(self.cmb_reservas.get())
        if self.reserva_seleccionada:
            r = self.reserva_seleccionada
            self._mostrar_mensaje(
                f"Reserva {r.id_reserva} seleccionada | Estado: {r.estado} | "
                f"Consumido: {r.cantidad_transcurrida}/{r.cantidad_reservada} | "
                f"Restante: {r.obtener_cantidad_restante()}"
            )

    def accion_avanzar_consumo(self) -> None:
        try:
            if self.reserva_seleccionada is None:
                raise ReservaError("Seleccione una reserva primero.")
            unidades = int(self.txt_consumo.get().strip())
            self.reserva_seleccionada.avanzar_tiempo(unidades)
            self._actualizar_combo_reservas()
            r = self.reserva_seleccionada
            self._mostrar_mensaje(
                f"Consumo actualizado en {r.id_reserva}: {r.cantidad_transcurrida}/{r.cantidad_reservada}."
            )
        except ValueError:
            self._mostrar_mensaje("Error: ingrese un número entero válido para consumir.")
        except Exception as exc:
            logging.error(f"Error al avanzar consumo: {exc}")
            self._mostrar_mensaje(f"Error: {exc}")

    def accion_procesar_reserva(self) -> None:
        try:
            if self.reserva_seleccionada is None:
                raise ReservaError("Seleccione una reserva primero.")
            desglose = self.reserva_seleccionada.procesar_reserva()
            self._actualizar_combo_reservas()
            self._mostrar_mensaje(
                self._formatear_desglose(self.reserva_seleccionada, desglose, "RESERVA FINALIZADA")
            )
        except Exception as exc:
            logging.error(f"Error al procesar reserva: {exc}")
            self._mostrar_mensaje(f"Error: {exc}")

    def accion_cancelar_reserva(self) -> None:
        try:
            if self.reserva_seleccionada is None:
                raise ReservaError("Seleccione una reserva primero.")
            desglose = self.reserva_seleccionada.cancelar_reserva()
            self._actualizar_combo_reservas()
            self._mostrar_mensaje(
                self._formatear_desglose(self.reserva_seleccionada, desglose, "RESERVA CANCELADA")
            )
        except Exception as exc:
            logging.error(f"Error al cancelar reserva: {exc}")
            self._mostrar_mensaje(f"Error: {exc}")

    def _formatear_desglose(self, reserva: Reserva, desglose: dict, encabezado: str) -> str:
        return (
            f"=== {encabezado} ({reserva.id_reserva}) ===\n"
            f"Cliente: {reserva.cliente.nombre} | Servicio: {reserva.servicio.nombre_servicio}\n"
            f"Subtotal: ${desglose['subtotal']} | Descuento ({desglose['porcentaje_descuento']}%): -${desglose['descuento']}\n"
            f"Seguro: ${desglose['seguro']} | Impuesto: ${desglose['impuesto']} | TOTAL: ${desglose['total']}"
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
