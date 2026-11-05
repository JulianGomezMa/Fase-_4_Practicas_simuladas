from abc import ABC, abstractmethod
from datetime import datetime
import logging

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
        self.capacidad = capacidad

    def calcular_costo(self, horas: int, descuento: float = 0.0) -> float:
        try:
            if horas <= 0:
                raise ValueError("Las horas deben ser mayores a cero.")
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
        self.tipo_equipo = tipo_equipo

    def calcular_costo(self, dias: int, seguro_adicional: bool = False) -> float:
        try:
            if dias <= 0:
                raise ValueError("Los días de alquiler deben ser mayores a cero.")
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
        self.area = area

    def calcular_costo(self, sesiones: int, impuesto: float = 0.19) -> float:
        try:
            if sesiones <= 0:
                raise ValueError("El número de sesiones debe ser mayor a cero.")
            subtotal = self.costo_base * sesiones
            costo_total = subtotal * (1 + impuesto)
            return round(costo_total, 2)
        except Exception as e:
            logging.error(f"Error al calcular costo de asesoría: {e}")
            raise

    def obtener_detalles(self) -> str:
        return f"[Asesoría] {self.nombre_servicio} en {area if 'area' in locals() else self.area}"


# --- CLASE RESERVA ---
class Reserva:
    def __init__(self, id_reserva: str, cliente: Cliente, servicio: Servicio):
        self.id_reserva = id_reserva
        self.cliente = cliente
        self.servicio = servicio
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
            raise ReservaError(f"No se pudo confirmar la reserva: {e}")
        else:
            print("Proceso de validación de reserva completado sin interrupciones.")
        finally:
            print(f"Estado actual de la reserva: {self.estado}\n")


# --- SIMULACIÓN DE OPERACIONES (Pruebas iniciales) ---
if __name__ == "__main__":
    print("--- INICIANDO PRUEBAS DEL SISTEMA SOFTWARE FJ ---")
    
    # Simulación de registros válidos e inválidos con manejo estructurado de excepciones
    try:
        # Cliente válido
        c1 = Cliente("10203040", "Julian Gomez", "julian@example.com")
        print(c1.obtener_detalles())
        
        # Creación de servicio y cálculo con sobrecarga/parámetros opcionales
        sala = ReservaSalas("S001", 50.0, 10)
        print(sala.obtener_detalles())
        costo = sala.calcular_costo(horas=3, descuento=0.1)
        print(f"Costo calculado de la sala: ${costo}")
        
        # Creación y confirmación de reserva
        reserva1 = Reserva("R-001", c1, sala)
        reserva1.confirmar_reserva()

    except ErrorSistemaFJ as ex:
        print(f"Error controlado en el sistema: {ex}")

    # Prueba de manejo de excepción por datos incorrectos
    print("\n--- PRUEBA DE MANEJO DE EXCEPCIÓN (Cliente inválido) ---")
    try:
        c_malo = Cliente("ABC", "Ana", "correo-invalido")
    except ClienteNoValidoError as ex:
        print(f"Excepción capturada correctamente: {ex}")
