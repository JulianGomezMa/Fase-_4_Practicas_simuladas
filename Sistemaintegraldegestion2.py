from __future__ import annotations
from abc import ABC, abstractmethod
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

    def __validar_correo(self, correo: str):
        """Valida que el correo tenga un formato correcto."""

        if not correo or correo.count("@") != 1:
            logging.error(f"Correo inválido: {correo}")
            raise ClienteNoValidoError(
                "El correo debe contener un único símbolo @."
            )

        usuario, dominio = correo.split("@")

        if not usuario or not dominio:
            logging.error(f"Correo inválido: {correo}")
            raise ClienteNoValidoError(
                "Debe existir texto antes y después del @."
            )

        if "." not in dominio:
            logging.error(f"Correo inválido: {correo}")
            raise ClienteNoValidoError(
                "El dominio debe contener al menos un punto."
            )

        partes_dominio = dominio.split(".")

        if any(not parte for parte in partes_dominio):
            logging.error(f"Correo inválido: {correo}")
            raise ClienteNoValidoError(
                "El dominio no puede tener puntos consecutivos "
                "ni terminar en un punto."
            )

        if any(parte.isspace() for parte in partes_dominio) or any(
            caracter.isspace() for caracter in usuario
        ):
            logging.error(f"Correo inválido: {correo}")
            raise ClienteNoValidoError(
                "El correo no puede contener espacios."
            )
        
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
    def calcular_costo(self, *args, **kwargs) -> dict:
        pass


class ReservaSalas(Servicio):
    def __init__(self, codigo: str, costo_base: float, capacidad: int):
        super().__init__(codigo, "Reserva de Sala", costo_base)
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un número entero positivo.")
        self.capacidad = capacidad

    def calcular_costo(self, horas: int) -> dict:
        """Calcula el costo de la sala y devuelve el desglose."""

        if not isinstance(horas, int) or isinstance(horas, bool) or horas < 0:
            raise ValueError("Las horas deben ser un entero positivo o cero.")

        descuento = 0.0
        if horas >= 5:
            descuento = 0.15
        elif horas >= 3:
            descuento = 0.10

        subtotal = self.costo_base * horas
        valor_descuento = subtotal * descuento
        subtotal_descuento = subtotal - valor_descuento

        return {
            "subtotal": round(subtotal, 2),
            "porcentaje_descuento": descuento * 100,
            "descuento": round(valor_descuento, 2),
            "subtotal_descuento": round(subtotal_descuento, 2),
            "seguro": 0.0,
            "impuesto": 0.0,
            "total": round(subtotal_descuento, 2)
        }

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
        self.seguro_activado = False

    def calcular_costo(self, dias: int) -> dict:
        """Calcula el costo del equipo y devuelve el desglose."""
        if (not isinstance(dias, int) or isinstance(dias, bool) or dias < 0):
            raise ValueError(
                "Los días de alquiler deben ser un número entero positivo o cero."
            )

        descuento = 0.0
        if dias >= 5:
            descuento = 0.15
        elif dias >= 3:
            descuento = 0.10

        subtotal = self.costo_base * dias
        valor_descuento = subtotal * descuento
        subtotal_descuento = subtotal - valor_descuento

        seguro = 15.0 if self.seguro_activado and dias > 0 else 0.0

        total = subtotal_descuento + seguro

        return {
            "subtotal": round(subtotal, 2),
            "porcentaje_descuento": descuento * 100,
            "descuento": round(valor_descuento, 2),
            "subtotal_descuento": round(subtotal_descuento, 2),
            "seguro": seguro,
            "impuesto": 0.0,
            "total": round(total, 2)
        }

    def activar_seguro(self):
        """Activa el seguro adicional para el alquiler del equipo."""
        self.seguro_activado = True
        logging.info(f"Seguro activado para el equipo {self.codigo}.")

    def desactivar_seguro(self):
        """Desactiva el seguro adicional del equipo."""
        self.seguro_activado = False
        logging.info(f"Seguro desactivado para el equipo {self.codigo}.")

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

    def calcular_costo(self, sesiones: int) -> dict:
        """Calcula el costo de la asesoría y devuelve el desglose."""   

        if not isinstance(sesiones, int) or isinstance(sesiones, bool) or sesiones < 0:
            raise ValueError("Las sesiones deben ser un entero positivo o cero.")   

        descuento = 0.0 
        if sesiones >= 5:
            descuento = 0.10
        elif sesiones >= 3:
            descuento = 0.05    

        subtotal = self.costo_base * sesiones
        valor_descuento = subtotal * descuento
        subtotal_descuento = subtotal - valor_descuento 

        impuesto = subtotal_descuento * 0.19
        total = subtotal_descuento + impuesto   

        return {
            "subtotal": round(subtotal, 2),
            "porcentaje_descuento": descuento * 100,
            "descuento": round(valor_descuento, 2),
            "subtotal_descuento": round(subtotal_descuento, 2),
            "seguro": 0.0,
            "impuesto": round(impuesto, 2),
            "total": round(total, 2)
        }

    def obtener_detalles(self) -> str:
        return f"[Asesoría] {self.area} ({self.codigo}) - Costo/sesión: ${self.costo_base}"

    def __str__(self):
        return f"Asesoría: {self.codigo} - {self.area}"


# --- CLASE RESERVA ---
class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, cantidad_reservada: int, seguro_aplicado: bool = False):
        if not id_reserva or not id_reserva.strip():
            raise ReservaError("El ID de la reserva es obligatorio.")
        if not isinstance(cantidad_reservada, int) or cantidad_reservada <= 0:
            raise ReservaError("La cantidad reservada debe ser un número entero positivo.")
        
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio 
        
        self.cantidad_reservada = cantidad_reservada
        self.cantidad_transcurrida = 0
        self.seguro_aplicado = seguro_aplicado
        
        # Estados posibles:
        # Pendiente -> mientras la reserva siga activa
        # Cancelada -> terminó antes de consumir todo
        # Finalizada -> terminó normalmente
        self.estado = "Pendiente"

    def avanzar_tiempo(self, cantidad: int):
        """simula el consumo de tiempo de la reserva, avanzando la cantidad especificada."""
        if self.estado != "Pendiente":
            raise ReservaError("Solo se puede consumir tiempo en reservas pendientes.")
        if not isinstance(cantidad, int) or isinstance(cantidad, bool) or cantidad <= 0:
            raise ValueError("La cantidad de tiempo a avanzar debe ser un número entero positivo.")
        
        nueva_cantidad = self.cantidad_transcurrida + cantidad      
        if nueva_cantidad > self.cantidad_reservada:
            raise ReservaError("La cantidad transcurrida no puede superar la cantidad contratada.")
        
        self.cantidad_transcurrida = nueva_cantidad
        logging.info(
            f"Reserva {self.id_reserva}: "
            f"{self.cantidad_transcurrida}/{self.cantidad_reservada} unidades consumidas."
            )

    def obtener_cantidad_restante(self) -> int:
        """Devuelve la cantidad de tiempo restante en la reserva."""
        return self.cantidad_reservada - self.cantidad_transcurrida

    def obtener_desglose_costo(self, cantidad=None) -> dict:
        """Obtiene el desglose del costo según la cantidad consumida."""
        if cantidad is None:
            cantidad = self.cantidad_transcurrida

        if isinstance(self.servicio, AlquilerEquipos):
            try:
                if self.seguro_aplicado:
                    self.servicio.activar_seguro()
                else:
                    self.servicio.desactivar_seguro()
                return self.servicio.calcular_costo(cantidad)
            finally:
                self.servicio.desactivar_seguro()
        return self.servicio.calcular_costo(cantidad)

    def cancelar_reserva(self) -> dict:
        """Cancela la reserva y calcula el costo correspondiente a la cantidad de tiempo consumido."""
        if self.estado != "Pendiente":
            raise ReservaError(f"No se puede cancelar una reserva en estado '{self.estado}'.")
        if self.cantidad_transcurrida == self.cantidad_reservada:
            raise ReservaError(
                "la cantidad reservada ya fue consumida "
                "por completo. Debe procesar la reserva"
            )
        
        desglose = self.obtener_desglose_costo()
        costo = desglose["total"]

        self.estado = "Cancelada"
        
        logging.info(
            f"Reserva {self.id_reserva} cancelada. "
            f"Cantidad consumida: {self.cantidad_transcurrida}. "
            f"Costo: ${costo}"
            )
        
        return desglose

    def procesar_reserva(self) -> dict:
        """Procesa la reserva y calcula el costo total basado en la duración contratada."""
        if self.estado != "Pendiente":
            raise ReservaError(f"No se puede procesar una reserva en estado '{self.estado}'.")
        if self.cantidad_transcurrida == 0:
            raise ReservaError(
                "No se puede finalizar una reserva sin haber consumido ninguna unidad. "
            )
        
        desglose = self.obtener_desglose_costo()
        costo = desglose["total"]
        self.estado = "Finalizada"
        
        logging.info(
            f"Reserva {self.id_reserva} finalizada."
            f"Cantidad consumida: {self.cantidad_transcurrida}. "
            f"Costo: ${costo}"
        )
        return desglose

    def __str__(self):
        return (
            f"Reserva {self.id_reserva} - "
            f"Cliente: {self.cliente.nombre} - "
            f"Servicio: {self.servicio.nombre_servicio} - "
            f"Uso: {self.cantidad_transcurrida}/{self.cantidad_reservada} - "
            f"Estado: {self.estado}"
        )

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
        
    def cargar_clientes_iniciales(self):
        """Carga 10 clientes iniciales para utilizar en el sistema."""
    
        clientes = [
            Cliente("10000001", "Ana Perez", "ana@gmail.com"),
            Cliente("10000002", "Carlos Gomez", "carlos@gmail.com"),
            Cliente("10000003", "Laura Rodriguez", "laura@gmail.com"),
            Cliente("10000004", "Andres Martinez", "andres@gmail.com"),
            Cliente("10000005", "Sofia Hernandez", "sofia@gmail.com"),
            Cliente("10000006", "Daniel Torres", "daniel@gmail.com"),
            Cliente("10000007", "Valentina Castro", "valentina@gmail.com"),
            Cliente("10000008", "Mateo Ramirez", "mateo@gmail.com"),
            Cliente("10000009", "Camila Vargas", "camila@gmail.com"),
            Cliente("10000010", "Sebastian Moreno", "sebastian@gmail.com")
        ]
    
        for cliente in clientes:
            self.registrar_cliente(cliente)


# --- INTERFAZ GRÁFICA (TKINTER) ---
class SistemaFJApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sistema de Reservas y Servicios FJ")
        self.root.geometry("850x650")
        self.sistema = SistemaFJ()
        self.reserva_seleccionada = None
        self.sistema.cargar_clientes_iniciales()
        # Precargar servicios para pruebas rápidas en la interfaz
        try:
            self.sistema.registrar_servicio(ReservaSalas("S001", 50.0, 10))
            self.sistema.registrar_servicio(AlquilerEquipos("E001", 100.0, "Proyector"))
            self.sistema.registrar_servicio(AsesoriaEspecializada("A001", 80.0, "Software"))
        except Exception as e:
            logging.error(f"Error al cargar servicios iniciales: {e}")

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
        frame = ttk.LabelFrame(
            contenedor,
            text="Gestión de Reservas",
            padding=15
        )
        frame.grid(row=0, column=1, padx=5, pady=5, sticky="nsew")

        # Selección del cliente
        ttk.Label(frame, text="Cliente:").grid(row=0, column=0, sticky="w", pady=5)
        self.cmb_clientes = ttk.Combobox(frame, width=25, state="readonly")
        self.cmb_clientes.grid(row=0, column=1, pady=5)

        # Selección del servicio
        ttk.Label(frame, text="Servicio:").grid(row=1, column=0, sticky="w", pady=5)
        self.cmb_servicios = ttk.Combobox(frame, width=25, state="readonly")
        self.cmb_servicios.grid(row=1, column=1, pady=5)
        self.cmb_servicios.bind("<<ComboboxSelected>>", self.actualizar_info_servicio)

        # Información del servicio
        self.lbl_info_servicio = ttk.Label(frame, text="Seleccione un servicio.")
        self.lbl_info_servicio.grid(row=2, column=0, columnspan=2, pady=5)

        # Cantidad reservada
        ttk.Label(frame, text="Cantidad a reservar:").grid(row=3, column=0, sticky="w", pady=5)
        self.txt_cantidad = ttk.Entry(frame, width=25)
        self.txt_cantidad.grid(row=3, column=1, pady=5)

        # Seguro opcional
        self.var_seguro = tk.BooleanVar(value=False)
        self.chk_seguro = ttk.Checkbutton(frame, text="Agregar seguro (+$15)", variable=self.var_seguro)
        self.chk_seguro.grid(row=4, column=0, columnspan=2, pady=5)
        self.chk_seguro.config(state="disabled")

        # Crear reserva
        btn_crear = ttk.Button(frame, text="Crear Reserva", command=self.accion_crear_reserva)
        btn_crear.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Separator(frame).grid(row=6, column=0, columnspan=2,sticky="ew", pady=10)

        # Seleccionar reserva existente
        ttk.Label(frame, text="Reserva:").grid(row=7, column=0, sticky="w", pady=5)
        self.cmb_reservas = ttk.Combobox(
            frame,
            width=25,
            state="readonly"
        )
        self.cmb_reservas.grid(row=7, column=1, pady=5)
        self.cmb_reservas.bind("<<ComboboxSelected>>",self.seleccionar_reserva)

        # Cantidad a simular
        ttk.Label(frame, text="Cantidad a consumir:").grid(row=8, column=0, sticky="w", pady=5)
        self.txt_consumo = ttk.Entry(frame, width=25)
        self.txt_consumo.insert(0, "1")
        self.txt_consumo.grid(row=8, column=1, pady=5)

        # Simular consumo
        btn_avanzar = ttk.Button(
            frame,
            text="Avanzar Consumo",
            command=self.accion_avanzar_consumo
        )
        btn_avanzar.grid(row=9, column=0, columnspan=2, pady=5)

        # Procesar reserva
        btn_procesar = ttk.Button(
            frame,
            text="Procesar / Finalizar",
            command=self.accion_procesar_reserva
        )
        btn_procesar.grid(row=10, column=0, columnspan=2, pady=5)

        # Cancelar reserva
        btn_cancelar = ttk.Button(
            frame,
            text="Cancelar Reserva",
            command=self.accion_cancelar_reserva
        )
        btn_cancelar.grid(row=11, column=0, columnspan=2, pady=5)
        self.actualizar_comboboxes()

    def actualizar_comboboxes(self):
        self.cmb_clientes["values"] = [
            c.nombre for c in self.sistema.clientes
        ]
        self.servicios_por_opcion = {
            f"{s.nombre_servicio} - {s.codigo}": s
            for s in self.sistema.servicios
        }
        self.cmb_servicios["values"] = list(
            self.servicios_por_opcion.keys()
        )
        self.actualizar_lista_reservas()
        
    def actualizar_lista_reservas(self):
        self.reservas_por_opcion = {
            (
                f"{r.id_reserva} | {r.cliente.nombre} | "
                f"{r.estado} | "
                f"{r.cantidad_transcurrida}/"
                f"{r.cantidad_reservada}"
            ): r
            for r in self.sistema.reservas
        }
        self.cmb_reservas["values"] = list(
            self.reservas_por_opcion.keys()
        )

    def actualizar_info_servicio(self, event=None):
        opcion = self.cmb_servicios.get()
        servicio = self.servicios_por_opcion.get(opcion)
        if servicio is None:
            return
        self.lbl_info_servicio.config(
            text=(
                f"Costo base: ${servicio.costo_base} "
                f"| {servicio.nombre_servicio}"
            )
        )
        if isinstance(servicio, AlquilerEquipos):
            self.chk_seguro.config(state="normal")
        else:
            self.var_seguro.set(False)
            self.chk_seguro.config(state="disabled")

    def accion_crear_reserva(self):
        try:
            cli_nom = self.cmb_clientes.get()
            srv_opcion = self.cmb_servicios.get()
            cantidad_str = self.txt_cantidad.get().strip()
            
            if not cli_nom or not srv_opcion or not cantidad_str:
                raise ValueError(
                    "Complete todos los campos de la reserva."
                )
                
            cantidad = int(cantidad_str)
            cliente = next(
                c for c in self.sistema.clientes
                if c.nombre == cli_nom
            )
            
            servicio = self.servicios_por_opcion[srv_opcion]
            seguro = (isinstance(servicio, AlquilerEquipos)and self.var_seguro.get())
            
            reserva = Reserva(
                f"R-{len(self.sistema.reservas) + 1:03d}",
                cliente,
                servicio,
                cantidad,
                seguro_aplicado=seguro
            )
            desglose = reserva.obtener_desglose_costo(cantidad)
            self.sistema.registrar_reserva(reserva)
            mensaje = self.formatear_desglose(
                reserva,
                desglose,
                "RESERVA CREADA - COSTO ESTIMADO"
            )
            mensaje += (
                "\nNota: estimación suponiendo que se consume "
                "toda la cantidad contratada."
            )
            self.mostrar_resultado(mensaje)
            self.actualizar_lista_reservas()
            
            self.txt_cantidad.delete("0", tk.END)
            self.var_seguro.set(False)
        except Exception as e:
            self.mostrar_resultado(f"Error al crear reserva: {e}")
            
    def seleccionar_reserva(self, event=None):
        opcion = self.cmb_reservas.get()
        self.reserva_seleccionada = (
            self.reservas_por_opcion.get(opcion)
        )

        if self.reserva_seleccionada:
            r = self.reserva_seleccionada
            self.mostrar_resultado(
                f"Seleccionada: {r.id_reserva} | "
                f"Uso: {r.cantidad_transcurrida}/{r.cantidad_reservada} | "
                f"Restante: {r.obtener_cantidad_restante()} | "
                f"Estado: {r.estado}"
            )
            
    def accion_avanzar_consumo(self):
        try:
            reserva = self.reserva_seleccionada
            if reserva is None:
                raise ReservaError("Seleccione una reserva.")
            cantidad = int(self.txt_consumo.get().strip())
            reserva.avanzar_tiempo(cantidad)
            self.mostrar_resultado(
                f"Reserva {reserva.id_reserva}: "
                f"{reserva.cantidad_transcurrida}/"
                f"{reserva.cantidad_reservada} consumidas. "
                f"Restantes: {reserva.obtener_cantidad_restante()}."
            )
            self.actualizar_lista_reservas()
        except Exception as e:
            self.mostrar_resultado(f"Error: {e}")
            
    def accion_procesar_reserva(self):
        try:
            reserva = self.reserva_seleccionada
            if reserva is None:
                raise ReservaError("Seleccione una reserva.")
            
            desgloce = reserva.obtener_desglose_costo()
            reserva.procesar_reserva()
            
            mensaje = self.formatear_desglose(
                reserva,
                desgloce,
                "RESERVA FINALIZADA - COSTO TOTAL"
            )
            self.mostrar_resultado(mensaje)
            self.actualizar_lista_reservas()
        except Exception as e:
            self.mostrar_resultado(f"Error: {e}")
            
    def accion_cancelar_reserva(self):
        try:
            reserva = self.reserva_seleccionada
            if reserva is None:
                raise ReservaError("Seleccione una reserva.")
            
            desgloce = reserva.obtener_desglose_costo()
            reserva.cancelar_reserva()
            
            mensaje = self.formatear_desglose(
                reserva,
                desgloce,
                "RESERVA CANCELADA"
            )
            self.mostrar_resultado(mensaje)
            self.actualizar_lista_reservas()
        except Exception as e:
            self.mostrar_resultado(f"Error: {e}")

    def formatear_desglose(self, reserva, desglose, titulo):
        servicio = reserva.servicio 
        if isinstance(servicio, ReservaSalas):
            unidad = "horas"
        elif isinstance(servicio, AlquilerEquipos):
            unidad = "días"
        else:
            unidad = "sesiones" 

        lineas = [
            f"========== {titulo} ==========",
            f"Reserva: {reserva.id_reserva}",
            f"Cliente: {reserva.cliente.nombre}",
            f"Servicio: {servicio.nombre_servicio}",
            f"Cantidad consumida: {reserva.cantidad_transcurrida} {unidad}",
            f"Cantidad contratada: {reserva.cantidad_reservada} {unidad}",
            "",
            "DETALLE DEL COSTO",
            f"Costo base por unidad: ${servicio.costo_base:.2f}",
            f"Subtotal: ${desglose['subtotal']:.2f}",
            f"Descuento ({desglose['porcentaje_descuento']:.0f}%): "
            f"-${desglose['descuento']:.2f}",
            f"Subtotal con descuento: ${desglose['subtotal_descuento']:.2f}"
        ]   

        if isinstance(servicio, AlquilerEquipos):
            estado_seguro = "Sí" if reserva.seguro_aplicado else "No"
            lineas.append(f"Seguro contratado: {estado_seguro}")
            lineas.append(f"Costo del seguro: +${desglose['seguro']:.2f}")  

        if isinstance(servicio, AsesoriaEspecializada):
            lineas.append(f"Impuesto (19%): +${desglose['impuesto']:.2f}")  

        lineas.extend([
            "--------------------------------",
            f"TOTAL: ${desglose['total']:.2f}",
            "================================"
        ])  

        return "\n".join(lineas)

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
