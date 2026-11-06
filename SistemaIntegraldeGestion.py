from __future__ import annotations
from abc import ABC, abstractmethod
from datetime import datetime
import logging

#Manejo de listas y diccionarios para almacenar clientes, reservas y servicios
class SistemaFJ:
    """Gestiona los clientes, servicios y reservas del sistema."""

    def __init__(self):
        self.clientes = []
        self.servicios = []
        self.reservas = []

    def registrar_cliente(self, cliente: Cliente):
        """Agrega un cliente a la lista de clientes."""
        if any (c.identificacion == cliente.identificacion 
                for c in self.clientes): 
            raise ClienteNoValidoError( "El cliente ya se encuentra registrado."
            )

        self.clientes.append(cliente)
        logging.info(f"Cliente registrado: {cliente.nombre}")

    def registrar_servicio(self, servicio: Servicio):
        """Agrega un servicio si su código no está registrado."""

        if any(s.codigo == servicio.codigo for s in self.servicios):
            raise ErrorSistemaFJ(
                f"Ya existe un servicio con el código '{servicio.codigo}'."
            )

        self.servicios.append(servicio)
        logging.info(f"Servicio registrado: {servicio.codigo}")

    def registrar_reserva(self, reserva: Reserva):
        """Registra una reserva validando cliente, servicio e ID."""

        if any(r.id_reserva == reserva.id_reserva for r in self.reservas):
            raise ReservaError(
                f"Ya existe una reserva con el ID '{reserva.id_reserva}'."
            )

        if reserva.cliente not in self.clientes:
            raise ReservaError(
                "El cliente de la reserva no está registrado en el sistema."
            )

        if reserva.servicio not in self.servicios:
            raise ReservaError(
                "El servicio de la reserva no está registrado en el sistema."
            )

        self.reservas.append(reserva)

        logging.info(
            f"Reserva registrada: {reserva.id_reserva}"
        )
        
    def ejecutar_pruebas(self):
        """Ejecuta 10 operaciones de prueba del sistema."""

        print("\n========================================")
        print("   PRUEBAS DEL SISTEMA SOFTWARE FJ")
        print("========================================\n")
        operaciones = [
            "Registrar cliente válido",
            "Registrar cliente con identificación inválida",
            "Registrar cliente duplicado",
            "Registrar servicio de sala válido",
            "Registrar sala con capacidad inválida",
            "Registrar alquiler de equipo válido",
            "Registrar asesoría especializada válida",
            "Registrar reserva válida",
            "Intentar procesar reserva no confirmada",
            "Cancelar y procesar una reserva confirmada"
        ]
        print("Se ejecutarán 10 operaciones:\n")
        for numero, descripcion in enumerate(operaciones, start=1):
            print(f"{numero}. {descripcion}")
        print("\n----------------------------------------")

        # Operación 1
        try:
            cliente1 = Cliente(
                "10203040",
                "Julian Gomez",
                "julian@example.com"
            )
            self.registrar_cliente(cliente1)
            print("1. OK - Cliente registrado correctamente.")
        except Exception as e:
            logging.error(f"Operación 1 fallida: {e}")
            print(f"1. ERROR - {e}")

        # Operación 2
        try:
            cliente_invalido = Cliente(
                "ABC",
                "Ana",
                "correo-invalido"
            )
            self.registrar_cliente(cliente_invalido)
            print("2. ERROR - El cliente inválido fue aceptado.")
        except ClienteNoValidoError as e:
            logging.error(f"Operación 2 - Cliente inválido: {e}")
            print(f"2. OK - Error controlado: {e}")

        # Operación 3
        try:
            cliente_duplicado = Cliente(
                "10203040",
                "Julian Gomez 2",
                "julian2@example.com"
            )
            self.registrar_cliente(cliente_duplicado)
            print("3. ERROR - Se permitió un cliente duplicado.")
        except ClienteNoValidoError as e:
            logging.error(f"Operación 3 - Cliente duplicado: {e}")
            print(f"3. OK - Error controlado: {e}")

        # Operación 4
        try:
            sala = ReservaSalas(
                "S001",
                50.0,
                10
            )
            self.registrar_servicio(sala)
            print("4. OK - Sala registrada correctamente.")
        except Exception as e:
            logging.error(f"Operación 4 fallida: {e}")
            print(f"4. ERROR - {e}")
        
        # Operación 5
        try:
            sala_invalida = ReservaSalas(
                "S002",
                50.0,
                0
            )
            self.registrar_servicio(sala_invalida)
            print("5. ERROR - Se permitió una sala con capacidad inválida.")
        except ValueError as e:
            logging.error(f"Operación 5 - Capacidad inválida: {e}")
            print(f"5. OK - Error controlado: {e}")

        # Operación 6
        try:
            equipo = AlquilerEquipos(
                "E001",
                100.0,
                "Proyector"
            )
            self.registrar_servicio(equipo)
            print("6. OK - Equipo registrado correctamente.")
        except Exception as e:
            logging.error(f"Operación 6 fallida: {e}")
            print(f"6. ERROR - {e}")

        # Operación 7
        try:
            asesoria = AsesoriaEspecializada(
                "A001",
                80.0,
                "Desarrollo de software"
            )
            self.registrar_servicio(asesoria)
            print("7. OK - Asesoría registrada correctamente.")
        except Exception as e:
            logging.error(f"Operación 7 fallida: {e}")
            print(f"7. ERROR - {e}")

        # Operación 8
        try:
            reserva1 = Reserva(
                "R001",
                cliente1,
                sala,
                3
            )
            self.registrar_reserva(reserva1)
            reserva1.confirmar_reserva()
            print("8. OK - Reserva creada y confirmada correctamente.")
        except Exception as e:
            logging.error(f"Operación 8 fallida: {e}")
            print(f"8. ERROR - {e}")

        # Operación 9
        try:
            reserva2 = Reserva(
                "R002",
                cliente1,
                sala,
                2
            )
            self.registrar_reserva(reserva2)
            reserva2.procesar_reserva()
            print("9. ERROR - Se procesó una reserva sin confirmar.")
        except ReservaError as e:
            logging.error(f"Operación 9 - Reserva no confirmada: {e}")
            print(f"9. OK - Error controlado: {e}")

        # Operación 10
        try:
            reserva1.cancelar_reserva()
            print("10. OK - Reserva cancelada correctamente.")
            try:
                reserva1.procesar_reserva()
            except ReservaError as e:
                logging.error(
                    f"Operación 10 - Procesamiento de reserva cancelada: {e}"
                )
                print(f"    OK - No se permitió procesar la reserva cancelada: {e}")
        except Exception as e:
            logging.error(f"Operación 10 fallida: {e}")
            print(f"10. ERROR - {e}")

        print("\n========================================")
        print("   PRUEBAS FINALIZADAS")
        print("   Revise sistema_fj.log para los errores registrados.")
        print("========================================\n")

# 1. Configuración del sistema de logs (requisito de manejo de errores y eventos)
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
    """Clase abstracta que representa entidades generales del sistema."""
    
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

    def obtener_detalles(self) -> str:
        return f"Cliente: {self.__nombre} (ID: {self.__identificacion}, Correo: {self.__correo})"


# --- CLASE ABSTRACTA SERVICIO Y DERIVADAS ---
class Servicio(EntidadBase, ABC):
    def __init__(self, codigo: str, nombre_servicio: str, costo_base: float):
        
        if not codigo or not codigo.strip():
            raise ValueError("El código es obligatorio.")
        
        if not isinstance(costo_base, (int, float)) or isinstance(costo_base, bool):
            raise ValueError("El costo debe ser un número.")

        if costo_base <= 0:
            raise ValueError("El costo debe ser mayor a cero.")
        
        self.codigo = codigo
        self.nombre_servicio = nombre_servicio
        self.costo_base = costo_base

    @abstractmethod
    def calcular_costo(self, *args, **kwargs) -> float:
        """Método polimórfico para calcular costos (admite sobrecarga simulada)."""
        pass

# 1. Servicio: Reserva de Salas
class ReservaSalas(Servicio):
    def __init__(self, codigo: str, costo_base: float, capacidad: int):
        super().__init__(codigo, "Reserva de Sala", costo_base)
        
        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ValueError("La capacidad debe ser un número entero positivo.")
        
        self.capacidad = capacidad

    def calcular_costo(self, horas: int, descuento: float = 0.0) -> float:
        try:
            if not isinstance(horas, int) or horas <= 0:
                raise ValueError("Las horas deben ser un número entero positivo.")
            if not (0 <= descuento < 1):
                raise ValueError("El descuento debe estar entre 0 y 1 (exclusivo).")
            costo_total = (self.costo_base * horas) * (1 - descuento)
            return round(costo_total, 2)
        except Exception as e:
            logging.error(f"Error al calcular costo de sala: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"[Sala] {self.nombre_servicio} - Costo base/hora: ${self.costo_base} (Capacidad: {self.capacidad} personas)"

# 2. Servicio: Alquiler de Equipos
class AlquilerEquipos(Servicio):
    def __init__(self, codigo: str, costo_base: float, tipo_equipo: str):
        super().__init__(codigo, "Alquiler de Equipo", costo_base)
        
        if not tipo_equipo or not tipo_equipo.strip():
            raise ValueError("El tipo de equipo es obligatorio.")
        
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, dias: int, seguro_adicional: bool = False) -> float:
        try:
            if not isinstance(dias, int) or isinstance(dias, bool) or dias <= 0:
                raise ValueError("Los días de alquiler deben ser un número entero positivo.")
            adicional = 15.0 if seguro_adicional else 0.0
            costo_total = (self.costo_base * dias) + adicional
            return round(costo_total, 2)
        except Exception as e:
            logging.error(f"Error al calcular costo de equipo: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"[Equipo] {self.nombre_servicio} ({self.tipo_equipo}) - Costo base/día: ${self.costo_base}"

# 3. Servicio: Asesorías Especializadas
class AsesoriaEspecializada(Servicio):
    def __init__(self, codigo: str, costo_base: float, area: str):
        super().__init__(codigo, "Asesoría Especializada", costo_base)
        
        if not area or not area.strip():
            raise ValueError("El área de asesoría es obligatoria.")
        
        self.area = area

    def calcular_costo(self, sesiones: int, impuesto: float = 0.19) -> float:
        try:
            if not isinstance(sesiones, int) or isinstance(sesiones, bool) or sesiones <= 0:
                raise ValueError("El número de sesiones debe ser un número entero positivo.")
            
            if not isinstance(impuesto, (int, float)) or impuesto < 0:
                raise ValueError("El impuesto debe ser un número mayor o igual a cero.")
            
            subtotal = self.costo_base * sesiones
            costo_total = subtotal * (1 + impuesto)
            
            return round(costo_total, 2)
        
        except Exception as e:
            logging.error(f"Error al calcular costo de asesoría: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"[Asesoría] {self.nombre_servicio} en {self.area}"


# --- CLASE RESERVA ---
class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio, duracion: int):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
        
        if not isinstance(duracion, int) or isinstance(duracion, bool) or duracion <= 0:
            raise ReservaError("La duración debe ser un número entero positivo.")
        
        self.duracion = duracion
        self.estado = "Pendiente"

    def confirmar_reserva(self):
        try:
            # Bloque try/except/else/finally de ejemplo para robustez
            self.estado = "Confirmada"
            logging.info(f"Reserva {self.id_reserva} confirmada con éxito.")
            print(f"-> Éxito: Reserva {self.id_reserva} para el cliente {self.cliente.nombre} confirmada.")
        except Exception as e:
            self.estado = "Fallida"
            logging.error(f"Error al confirmar reserva {self.id_reserva}: {e}")
            raise ReservaError(f"No se pudo confirmar la reserva.") from e
        else:
            print("Proceso de validación de reserva completado sin interrupciones.")
        finally:
            print(f"Estado actual de la reserva: {self.estado}\n")
    
    def cancelar_reserva(self):
        """Cancela una reserva pendiente o confirmada"""
        try:
            if self.estado not in ["Pendiente", "Confirmada"]:
                raise ReservaError(f"No se puede cancelar esta reserva en estado '{self.estado}'.")
            
            self.estado = "Cancelada"
            
            logging.info(f"Reserva {self.id_reserva} cancelada con éxito.")
            
        except ReservaError as e:
            logging.error(f"Error al cancelar reserva {self.id_reserva}: {e}")
            raise

    def procesar_reserva(self):
        """Procesa una reserva confirmada y calcula su costo."""
        try:
            if self.estado != "Confirmada":
                raise ReservaError(
                    "La reserva debe estar confirmada."
                )

            costo = self.servicio.calcular_costo(self.duracion)

            logging.info(
                f"Reserva {self.id_reserva} procesada. "
                f"Costo: ${costo}"
            )

            return costo

        except Exception as e:
            logging.error(
                f"Error al procesar reserva {self.id_reserva}: {e}"
            )

            raise ReservaError(
                "No fue posible procesar la reserva."
            ) from e

# --- SIMULACIÓN DE OPERACIONES (Pruebas iniciales) ---
if __name__ == "__main__":
    
    SistemaFJ().ejecutar_pruebas()
    
    #print("--- INICIANDO PRUEBAS DEL SISTEMA SOFTWARE FJ ---")
    
    # Simulación de registros válidos e inválidos con manejo estructurado de excepciones
    #try:
    #    # Cliente válido
    #    c1 = Cliente("10203040", "Julian Gomez", "julian@example.com")
    #    print(c1.obtener_detalles())
    #    
    #    # Creación de servicio y cálculo con sobrecarga/parámetros opcionales
    #    sala = ReservaSalas("S001", 50.0, 10)
    #    print(sala.obtener_detalles())
    #    costo = sala.calcular_costo(horas=3, descuento=0.1)
    #    print(f"Costo calculado de la sala: ${costo}")
    #    
    #    # Creación y confirmación de reserva
    #    reserva1 = Reserva("R-001", c1, sala, 3)
    #    reserva1.confirmar_reserva()
#
    #except ErrorSistemaFJ as ex:
    #    print(f"Error controlado en el sistema: {ex}")
#
    ## Prueba de manejo de excepción por datos incorrectos
    #print("\n--- PRUEBA DE MANEJO DE EXCEPCIÓN (Cliente inválido) ---")
    #try:
    #    c_malo = Cliente("ABC", "Ana", "correo-invalido")
    #except ClienteNoValidoError as ex:
    #    print(f"Excepción capturada correctamente: {ex}")
