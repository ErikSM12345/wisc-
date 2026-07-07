import json
import re
from pathlib import Path
from typing import List, Dict, Any, Union, Optional


class MotorEvaluacion:
    """
    Clase encargada de la lógica de evaluación pura para el Simulador WISC-V.
    Responsabilidades:
      - Carga y navegación de datos JSON
      - Evaluación de respuestas (dígitos y dibujos)
      - Cálculo de puntuaciones directas, escalares e IMT
      - Detección del punto teórico de discontinuación
    """

    def __init__(self, json_filename: str = "data.json"):
        # Resuelve la ruta base independientemente del lugar de ejecución.
        # Path(__file__).resolve() apunta a wisc-v-app/src/motor.py
        # .parent.parent apunta a wisc-v-app/
        base_path = Path(__file__).resolve().parent.parent
        self.json_path = base_path / "data" / json_filename

        self.datos: Dict[str, Any] = {}
        self._cargar_datos()

    def _cargar_datos(self) -> None:
        """Lee el archivo JSON de forma segura y lo carga en memoria."""
        try:
            with open(self.json_path, "r", encoding="utf-8") as f:
                self.datos = json.load(f)
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo en {self.json_path}")
        except json.JSONDecodeError:
            print(
                f"Error: El archivo {self.json_path} no es un JSON válido o está corrupto"
            )

    def obtener_datos(self) -> Dict[str, Any]:
        """Retorna los datos cargados del JSON."""
        return self.datos

    # ─── Navegación de Ítems ─────────────────────────────────────────

    def obtener_items_digitos(self, modalidad: str) -> List[Dict[str, Any]]:
        """
        Retorna la lista de ítems para una modalidad de dígitos.
        modalidad: 'orden_directo' | 'orden_inverso' | 'orden_creciente'
        """
        return (
            self.datos.get("wisc_v", {})
            .get("subprueba_digitos", {})
            .get(modalidad, [])
        )

    def obtener_items_dibujos(self) -> List[Dict[str, Any]]:
        """Retorna la lista completa de ítems de Span de Dibujos."""
        return self.datos.get("wisc_v", {}).get("subprueba_span_dibujos", [])

    # ─── Evaluación de Dígitos ───────────────────────────────────────

    @staticmethod
    def evaluar_digitos(
        input_usuario: str, secuencia_original: List[int], modalidad: str
    ) -> bool:
        """
        Evalúa el input del usuario frente a la secuencia original según la modalidad.
        Modalidades soportadas: 'directo', 'inverso', 'secuenciacion'
        Devuelve False si el input contiene caracteres inválidos (como letras).
        """
        # Validación de robustez: si el input contiene letras, retorna False.
        if re.search(r"[a-zA-Z]", input_usuario):
            return False

        try:
            # Extraemos únicamente los dígitos del input
            digitos_str = re.sub(r"\D", "", input_usuario)
            # Convertimos a lista de enteros
            input_procesado = [int(d) for d in digitos_str]
        except Exception:
            return False

        # Evaluamos según la modalidad solicitada
        if modalidad == "directo":
            return input_procesado == secuencia_original
        elif modalidad == "inverso":
            return input_procesado == secuencia_original[::-1]
        elif modalidad == "secuenciacion":
            return input_procesado == sorted(secuencia_original)
        else:
            raise ValueError(f"Modalidad desconocida: {modalidad}")

    # ─── Evaluación de Dibujos ───────────────────────────────────────

    @staticmethod
    def evaluar_dibujos(
        input_usuario: str, respuesta_correcta: Union[str, List[str]]
    ) -> bool:
        """
        Evalúa si el input de letras coincide exactamente con la respuesta esperada.
        La comparación ignora espacios y mayúsculas.
        """
        try:
            input_limpio = re.sub(r"[^a-zA-Z]", "", input_usuario).upper()
            if isinstance(respuesta_correcta, list):
                esperado = "".join(respuesta_correcta)
            else:
                esperado = str(respuesta_correcta)
            esperado_limpio = re.sub(r"[^a-zA-Z]", "", esperado).upper()
            return input_limpio == esperado_limpio
        except Exception:
            return False

    @staticmethod
    def evaluar_dibujos_puntuacion(
        input_usuario: str, respuesta_correcta: List[str]
    ) -> int:
        """
        Sistema de puntuación del Span de Dibujos:
          2 puntos → secuencia idéntica (mismas letras, mismo orden)
          1 punto  → mismos elementos en orden diferente
          0 puntos → cualquier otro caso
        """
        try:
            input_limpio = re.sub(r"[^a-zA-Z]", "", input_usuario).upper()
            input_lista = list(input_limpio)
            esperado = [c.upper() for c in respuesta_correcta]

            if input_lista == esperado:
                return 2
            elif sorted(input_lista) == sorted(esperado):
                return 1
            else:
                return 0
        except Exception:
            return 0

    # ─── Cálculo de Baremos ──────────────────────────────────────────

    def calcular_puntuacion_escalar(
        self, puntuacion_directa: int, subtest: str
    ) -> Optional[int]:
        """
        Busca la puntuación escalar en la tabla de baremos.
        subtest: 'DS_d' para dígitos, 'PS_sd' para span de dibujos
        Returns None si la puntuación no está en la tabla.
        """
        baremos = self.datos.get("baremos", {}).get(
            "baremos_subtests_completos", []
        )
        for fila in baremos:
            rango = fila.get(subtest)
            if rango is None:
                continue
            rango_str = str(rango)
            if "-" in rango_str:
                partes = rango_str.split("-")
                minimo, maximo = int(partes[0]), int(partes[1])
                if minimo <= puntuacion_directa <= maximo:
                    return fila["puntuacion_escalar"]
            else:
                if puntuacion_directa == int(rango_str):
                    return fila["puntuacion_escalar"]
        return None

    def calcular_imt(
        self, pe_digitos: int, pe_dibujos: int
    ) -> Optional[Dict[str, Any]]:
        """
        Calcula el Índice de Memoria de Trabajo (IMT / WMI) a partir de
        la suma de las puntuaciones escalares de Dígitos y Span de Dibujos.
        """
        suma = pe_digitos + pe_dibujos
        tabla_imt = self.datos.get("baremos", {}).get(
            "indice_memoria_trabajo_IMT_WMI", []
        )
        for fila in tabla_imt:
            if fila["suma_puntuaciones_escalares"] == suma:
                return {
                    "suma_pe": suma,
                    "imt_wmi": fila["imt_wmi"],
                    "rango_percentil": fila["rango_percentil"],
                    "intervalo_confianza_90": fila["intervalo_confianza_90"],
                    "intervalo_confianza_95": fila["intervalo_confianza_95"],
                }
        return None

    # ─── Detección de Punto de Discontinuación ───────────────────────

    @staticmethod
    def detectar_discontinuacion_digitos(
        resultados_items: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Detecta el ítem donde se habría aplicado la regla de discontinuación
        estándar del WISC-V para dígitos: 0 puntos en ambos intentos de
        2 ítems consecutivos (no-ejemplo).
        Returns el número de ítem o None.
        """
        consecutivos_cero = 0
        for resultado in resultados_items:
            if resultado.get("es_ejemplo", False):
                continue
            intentos = resultado.get("intentos_resultado", [])
            score_item = sum(1 for i in intentos if i.get("correcto", False))
            if score_item == 0:
                consecutivos_cero += 1
                if consecutivos_cero >= 2:
                    return resultado["item"]
            else:
                consecutivos_cero = 0
        return None

    @staticmethod
    def detectar_discontinuacion_dibujos(
        resultados_items: List[Dict[str, Any]],
    ) -> Optional[str]:
        """
        Detecta el punto de discontinuación para Span de Dibujos:
        0 puntos en 2 ítems consecutivos (no-ejemplo).
        Returns el número de ítem o None.
        """
        consecutivos_cero = 0
        for resultado in resultados_items:
            if resultado.get("es_ejemplo", False):
                continue
            if resultado.get("puntuacion", 0) == 0:
                consecutivos_cero += 1
                if consecutivos_cero >= 2:
                    return resultado["item"]
            else:
                consecutivos_cero = 0
        return None
