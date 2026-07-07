import json
import re
from typing import List, Dict, Any

class MotorEvaluacion:
    """
    Clase encargada de la lógica de evaluación pura para el Simulador WISC-V.
    """
    def __init__(self, json_path: str):
        self.json_path = json_path
        self.datos: Dict[str, Any] = {}

    def cargar_datos(self) -> None:
        """
        Lee el archivo JSON de forma segura y lo carga en memoria.
        """
        try:
            with open(self.json_path, 'r', encoding='utf-8') as f:
                self.datos = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Error: No se encontró el archivo {self.json_path}")
        except json.JSONDecodeError:
            raise ValueError(f"Error: El archivo {self.json_path} no es un JSON válido o está corrupto")

    def obtener_datos(self) -> Dict[str, Any]:
        """
        Retorna los datos cargados del JSON.
        """
        return self.datos

    @staticmethod
    def limpiar_input_digitos(user_input: str) -> List[int]:
        """
        Limpia el input del usuario eliminando todo lo que no sea un dígito.
        Convierte la cadena de texto en una lista de números enteros de un solo dígito.
        Ejemplo: "2, 9" -> [2, 9]
        """
        digitos_str = re.sub(r'\D', '', user_input)
        return [int(d) for d in digitos_str]

    @staticmethod
    def limpiar_input_dibujos(user_input: str) -> str:
        """
        Limpia el input del usuario eliminando espacios y caracteres no alfabéticos,
        dejando únicamente letras en mayúsculas para la comparación.
        Ejemplo: "a b" -> "AB"
        """
        letras = re.sub(r'[^a-zA-Z]', '', user_input)
        return letras.upper()

    @staticmethod
    def evaluar_digitos_directos(user_input: str, estimulo: List[int]) -> bool:
        """
        Dígitos Directos: Input del usuario == Array Original.
        """
        input_procesado = MotorEvaluacion.limpiar_input_digitos(user_input)
        return input_procesado == estimulo

    @staticmethod
    def evaluar_digitos_inversos(user_input: str, estimulo: List[int]) -> bool:
        """
        Dígitos Inversos: Input del usuario == Array Original invertido (ej. [::-1]).
        """
        input_procesado = MotorEvaluacion.limpiar_input_digitos(user_input)
        return input_procesado == estimulo[::-1]

    @staticmethod
    def evaluar_digitos_secuenciacion(user_input: str, estimulo: List[int]) -> bool:
        """
        Dígitos Secuenciación: Input del usuario == Array Original ordenado de menor a mayor.
        """
        input_procesado = MotorEvaluacion.limpiar_input_digitos(user_input)
        return input_procesado == sorted(estimulo)

    @staticmethod
    def evaluar_dibujos(user_input: str, respuesta_correcta: List[str]) -> bool:
        """
        Dibujos: Comparación de cadenas de letras (ignorando espacios y mayúsculas).
        """
        input_procesado = MotorEvaluacion.limpiar_input_dibujos(user_input)
        esperado_str = "".join(respuesta_correcta).upper()
        return input_procesado == esperado_str
