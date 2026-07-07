"""
Interfaz gráfica para la prueba de Dígitos del WISC-V.

Administra las tres modalidades (Orden Directo, Orden Inverso y
Secuenciación) reproduciendo estímulos por audio y recogiendo las
respuestas del evaluado sin mostrar si son correctas o incorrectas.
"""

import customtkinter as ctk
import pygame
import threading
import time
import os
from pathlib import Path

from src.motor import MotorEvaluacion


class VistaDigitos(ctk.CTkFrame):
    """Frame principal de la prueba de Dígitos."""

    # Modalidades en orden de administración
    MODALIDADES = ["orden_directo", "orden_inverso", "orden_creciente"]

    # Etiquetas legibles para la UI
    LABEL_MODALIDAD = {
        "orden_directo": "Orden Directo",
        "orden_inverso": "Orden Inverso",
        "orden_creciente": "Secuenciación",
    }

    # Claves usadas para la evaluación interna
    EVAL_KEY = {
        "orden_directo": "directo",
        "orden_inverso": "inverso",
        "orden_creciente": "secuenciacion",
    }

    # ------------------------------------------------------------------ #
    #  Constructor
    # ------------------------------------------------------------------ #
    def __init__(
        self,
        master,
        motor: MotorEvaluacion,
        on_complete=None,
        **kwargs,
    ):
        super().__init__(master, **kwargs)
        self.motor = motor
        self.on_complete = on_complete

        # Ruta base del proyecto (un nivel arriba de src/)
        self.base_path = Path(__file__).resolve().parent.parent

        # Inicializar pygame mixer
        pygame.mixer.init()

        # Estado interno
        self.resultados: dict = {}
        self._modalidad_idx: int = 0
        self._items: list = []
        self._item_idx: int = 0
        self._intento_idx: int = 0  # 0 o 1 (dos intentos por ítem)
        self._reproduciendo: bool = False

        # Construir widgets
        self._crear_widgets()

        # Arrancar la primera modalidad
        self._iniciar_modalidad()

    # ------------------------------------------------------------------ #
    #  Widgets
    # ------------------------------------------------------------------ #
    def _crear_widgets(self):
        """Crea y posiciona todos los widgets del frame."""
        self.grid_columnconfigure(0, weight=1)

        row = 0

        # Título
        self.lbl_titulo = ctk.CTkLabel(
            self, text="Prueba de Dígitos", font=("Arial", 22, "bold")
        )
        self.lbl_titulo.grid(row=row, column=0, pady=(18, 6), sticky="n")
        row += 1

        # Fase / modalidad actual
        self.lbl_fase = ctk.CTkLabel(
            self, text="", font=("Arial", 17, "bold")
        )
        self.lbl_fase.grid(row=row, column=0, pady=(8, 2))
        row += 1

        # Progreso (Ítem X/N - Directo)
        self.lbl_progreso = ctk.CTkLabel(
            self, text="", font=("Arial", 13)
        )
        self.lbl_progreso.grid(row=row, column=0, pady=(2, 2))
        row += 1

        # Ítem / intento actual
        self.lbl_item = ctk.CTkLabel(
            self, text="", font=("Arial", 14)
        )
        self.lbl_item.grid(row=row, column=0, pady=(4, 4))
        row += 1

        # Botón reproducir
        self.btn_reproducir = ctk.CTkButton(
            self,
            text="Reproducir Secuencia",
            width=200,
            command=self._on_reproducir,
        )
        self.btn_reproducir.grid(row=row, column=0, pady=(10, 6))
        row += 1

        # Campo de entrada
        self.entry_respuesta = ctk.CTkEntry(
            self,
            placeholder_text="Ingresa los dígitos...",
            width=250,
            state="disabled",
        )
        self.entry_respuesta.grid(row=row, column=0, pady=(6, 4))
        self.entry_respuesta.bind("<Return>", lambda e: self._on_siguiente())
        row += 1

        # Botón siguiente
        self.btn_siguiente = ctk.CTkButton(
            self,
            text="Siguiente",
            command=self._on_siguiente,
            state="disabled",
        )
        self.btn_siguiente.grid(row=row, column=0, pady=(6, 4))
        row += 1

        # Etiqueta de estado
        self.lbl_estado = ctk.CTkLabel(
            self, text="", font=("Arial", 13)
        )
        self.lbl_estado.grid(row=row, column=0, pady=(6, 10))

    # ------------------------------------------------------------------ #
    #  Flujo de modalidades / ítems / intentos
    # ------------------------------------------------------------------ #
    def _modalidad_actual(self) -> str:
        """Devuelve la clave de la modalidad en curso."""
        return self.MODALIDADES[self._modalidad_idx]

    def _iniciar_modalidad(self):
        """Carga los ítems de la modalidad actual y prepara la UI."""
        modalidad = self._modalidad_actual()
        self._items = list(self.motor.obtener_items_digitos(modalidad))
        self._item_idx = 0
        self._intento_idx = 0

        # Preparar almacenamiento de resultados para esta modalidad
        self.resultados[modalidad] = {"items": [], "puntuacion_total": 0}

        self.lbl_fase.configure(
            text=self.LABEL_MODALIDAD[modalidad]
        )
        self._preparar_intento()

    def _preparar_intento(self):
        """Configura la UI para el intento actual."""
        item = self._items[self._item_idx]
        intento_data = item["intentos"][self._intento_idx]

        # Si es el primer intento de un nuevo ítem, crear registro
        if self._intento_idx == 0:
            self.resultados[self._modalidad_actual()]["items"].append(
                {
                    "item": str(item.get("item", self._item_idx + 1)),
                    "es_ejemplo": bool(item.get("es_ejemplo", False)),
                    "intentos_resultado": [],
                    "puntuacion": 0,
                }
            )

        total_items = len(self._items)
        modalidad_label_corto = self.LABEL_MODALIDAD[self._modalidad_actual()]
        self.lbl_progreso.configure(
            text=f"Ítem {self._item_idx + 1}/{total_items} - {modalidad_label_corto}"
        )

        self.lbl_item.configure(
            text=f"Ítem {self._item_idx + 1} - Intento {self._intento_idx + 1}"
        )

        # Resetear controles
        self.entry_respuesta.configure(state="normal")
        self.entry_respuesta.delete(0, "end")
        self.entry_respuesta.configure(state="disabled")

        self.btn_reproducir.configure(state="normal")
        self.btn_siguiente.configure(state="disabled")
        self.lbl_estado.configure(text="Pulse «Reproducir Secuencia» para comenzar")

    # ------------------------------------------------------------------ #
    #  Reproducción de audio
    # ------------------------------------------------------------------ #
    def _on_reproducir(self):
        """Inicia la reproducción del estímulo en un hilo secundario."""
        if self._reproduciendo:
            return

        self._reproduciendo = True
        self.btn_reproducir.configure(state="disabled")
        self.entry_respuesta.configure(state="disabled")
        self.btn_siguiente.configure(state="disabled")
        self.lbl_estado.configure(text="Reproduciendo...")

        item = self._items[self._item_idx]
        estimulo = item["intentos"][self._intento_idx]["estimulo"]

        hilo = threading.Thread(
            target=self._reproducir_secuencia,
            args=(list(estimulo),),
            daemon=True,
        )
        hilo.start()

    def _reproducir_secuencia(self, estimulo: list):
        """Reproduce cada dígito del estímulo (ejecuta en hilo secundario)."""
        audio_dir = self.base_path / "assets" / "audio"

        for i, num in enumerate(estimulo):
            # Intentar .mp3 primero, luego .wav
            archivo = None
            for ext in (".mp3", ".wav"):
                candidato = audio_dir / f"{num}{ext}"
                if candidato.exists():
                    archivo = candidato
                    break

            if archivo is not None:
                try:
                    sonido = pygame.mixer.Sound(str(archivo))
                    sonido.play()
                    # Esperar a que termine la reproducción del sonido
                    while pygame.mixer.get_busy():
                        time.sleep(0.05)
                except Exception:
                    pass

            # Pausa de 1 segundo entre números (no después del último)
            if i < len(estimulo) - 1:
                time.sleep(1)

        # Volver al hilo principal para actualizar la UI
        self.after(0, self._fin_reproduccion)

    def _fin_reproduccion(self):
        """Actualiza la UI tras terminar la reproducción."""
        self._reproduciendo = False
        self.entry_respuesta.configure(state="normal")
        self.entry_respuesta.focus_set()
        self.btn_siguiente.configure(state="normal")
        self.lbl_estado.configure(text="Ingrese su respuesta")

    # ------------------------------------------------------------------ #
    #  Registro de respuesta
    # ------------------------------------------------------------------ #
    def _on_siguiente(self):
        """Recoge la respuesta del usuario y avanza."""
        if self._reproduciendo:
            return

        # Verificar que el botón esté habilitado (previene doble clic)
        if str(self.btn_siguiente.cget("state")) == "disabled":
            return

        respuesta_usuario = self.entry_respuesta.get().strip()

        item = self._items[self._item_idx]
        intento_data = item["intentos"][self._intento_idx]
        estimulo = intento_data["estimulo"]

        # Evaluar usando el motor con la modalidad correcta
        modalidad = self._modalidad_actual()
        eval_key = self.EVAL_KEY[modalidad]
        correcto = MotorEvaluacion.evaluar_digitos(
            respuesta_usuario, estimulo, eval_key
        )

        # Guardar resultado del intento
        registro_item = self.resultados[modalidad]["items"][-1]
        registro_item["intentos_resultado"].append(
            {
                "intento": self._intento_idx + 1,
                "estimulo": list(estimulo),
                "respuesta_usuario": respuesta_usuario,
                "correcto": correcto,
            }
        )

        # Avanzar al siguiente intento o ítem
        self._intento_idx += 1
        if self._intento_idx >= len(item["intentos"]):
            # Terminaron los intentos de este ítem → calcular puntuación
            self._calcular_puntuacion_item(registro_item)
            self._intento_idx = 0
            self._item_idx += 1

            if self._item_idx >= len(self._items):
                # Terminó la modalidad actual
                self._calcular_puntuacion_modalidad(modalidad)
                self._modalidad_idx += 1

                if self._modalidad_idx >= len(self.MODALIDADES):
                    # Todas las modalidades completadas
                    self._finalizar()
                    return
                else:
                    self._iniciar_modalidad()
                    return

        self._preparar_intento()

    @staticmethod
    def _calcular_puntuacion_item(registro_item: dict):
        """Suma los intentos correctos (excluyendo ejemplos)."""
        if registro_item.get("es_ejemplo", False):
            registro_item["puntuacion"] = 0
        else:
            registro_item["puntuacion"] = sum(
                1 for r in registro_item["intentos_resultado"] if r["correcto"]
            )

    def _calcular_puntuacion_modalidad(self, modalidad: str):
        """Calcula la puntuación total de una modalidad (sin ejemplos)."""
        total = sum(
            it["puntuacion"]
            for it in self.resultados[modalidad]["items"]
            if not it.get("es_ejemplo", False)
        )
        self.resultados[modalidad]["puntuacion_total"] = total

    # ------------------------------------------------------------------ #
    #  Finalización
    # ------------------------------------------------------------------ #
    def _finalizar(self):
        """Muestra mensaje de fin y ejecuta el callback."""
        # Puntuación directa total
        self.resultados["puntuacion_directa_total"] = sum(
            self.resultados[m]["puntuacion_total"]
            for m in self.MODALIDADES
        )

        self.lbl_fase.configure(text="Prueba Finalizada")
        self.lbl_item.configure(text="")
        self.lbl_progreso.configure(text="")
        self.lbl_estado.configure(
            text="La prueba de Dígitos ha sido completada."
        )
        self.btn_reproducir.configure(state="disabled")
        self.btn_siguiente.configure(state="disabled")
        self.entry_respuesta.configure(state="disabled")

        if self.on_complete is not None:
            self.on_complete()

    # ------------------------------------------------------------------ #
    #  API pública
    # ------------------------------------------------------------------ #
    def obtener_resultados(self) -> dict:
        """Devuelve el diccionario completo de resultados."""
        return self.resultados

    def reiniciar(self):
        """Reinicia todo el estado para volver a administrar la prueba."""
        self.resultados = {}
        self._modalidad_idx = 0
        self._items = []
        self._item_idx = 0
        self._intento_idx = 0
        self._reproduciendo = False

        self.entry_respuesta.configure(state="normal")
        self.entry_respuesta.delete(0, "end")
        self.entry_respuesta.configure(state="disabled")

        self._iniciar_modalidad()
