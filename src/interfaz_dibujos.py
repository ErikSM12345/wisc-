"""
interfaz_dibujos.py
Vista de la subprueba Span de Dibujos (Picture Span) del WISC-V.
Muestra estímulos visuales con temporizador de 5 s, recoge respuestas
de letras y puntúa con el motor de evaluación.
"""

import customtkinter as ctk
from PIL import Image
from tkinter import filedialog
import os
from pathlib import Path

from src.motor import MotorEvaluacion


class VistaDibujos(ctk.CTkFrame):
    """Frame principal para la subprueba Span de Dibujos."""

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

        # Ruta base para las imágenes (assets/img/ desde la raíz del proyecto)
        self.base_path = Path(__file__).resolve().parent.parent / "assets" / "img"
        self.carpeta_imagenes: Path = self.base_path
        self.imagenes_ordenadas: list[Path] = []

        # Datos de ítems procedentes del motor
        self.items: list[dict] = self.motor.obtener_items_dibujos()
        self.indice_actual: int = 0

        # Resultados acumulados
        self.resultados: dict = {
            "items": [],
            "puntuacion_directa_total": 0,
        }

        # Cache de imágenes para optimización
        self._image_cache: dict = {}

        # Referencia al temporizador activo (para poder cancelarlo)
        self._timer_id = None
        # Referencia a la CTkImage mostrada (evita recolección de basura)
        self._ctk_image_ref = None

        # Cargar imágenes de la carpeta por defecto
        self._cargar_imagenes_desde_carpeta(self.carpeta_imagenes)

        # Construir la interfaz
        self._setup_ui()

        # Arrancar con el primer ítem
        self._mostrar_item_actual()

    # ──────────────────────────────────────────────────────────────────
    #  Construcción de la UI
    # ──────────────────────────────────────────────────────────────────

    def _setup_ui(self) -> None:
        """Crea todos los widgets (pack layout)."""

        # Título
        self.lbl_titulo = ctk.CTkLabel(
            self,
            text="Span de Dibujos",
            font=("Arial", 22, "bold"),
        )
        self.lbl_titulo.pack(pady=(15, 5))

        # ── Selección de carpeta ──
        frame_carpeta = ctk.CTkFrame(self, fg_color="transparent")
        frame_carpeta.pack(pady=(0, 5))

        self.btn_carpeta = ctk.CTkButton(
            frame_carpeta,
            text="Seleccionar carpeta de imágenes",
            command=self._seleccionar_carpeta,
            width=220,
            height=28,
            font=("Arial", 12),
            fg_color="gray40",
            hover_color="gray50",
        )
        self.btn_carpeta.pack(side="left", padx=(0, 8))

        self.lbl_carpeta = ctk.CTkLabel(
            frame_carpeta,
            text=str(self.carpeta_imagenes),
            font=("Arial", 11),
            text_color="gray70",
            wraplength=350,
        )
        self.lbl_carpeta.pack(side="left")

        # ── Info del ítem ──
        self.lbl_item_info = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 16),
        )
        self.lbl_item_info.pack(pady=(10, 5))

        # ── Botón "Mostrar Estímulo" ──
        self.btn_mostrar = ctk.CTkButton(
            self,
            text="Mostrar Estímulo",
            command=self._mostrar_estimulo,
            font=("Arial", 16, "bold"),
            width=250,
            height=50,
        )
        self.btn_mostrar.pack(pady=10)

        # ── Área de imagen (no empaquetada hasta que tenga contenido) ──
        self.lbl_imagen = ctk.CTkLabel(self, text="")

        # ── Campo de entrada (oculto al inicio) ──
        self.entrada_respuesta = ctk.CTkEntry(
            self,
            placeholder_text="Ingrese las letras...",
            width=250,
        )
        # No se empaqueta hasta que sea necesario

        # ── Botón "Siguiente" (oculto al inicio) ──
        self.btn_siguiente = ctk.CTkButton(
            self,
            text="Siguiente",
            command=self._registrar_respuesta,
            width=200,
            height=40,
        )
        # No se empaqueta hasta que sea necesario

        # ── Etiqueta de progreso ──
        self.lbl_progreso = ctk.CTkLabel(
            self,
            text="",
            font=("Arial", 12),
            text_color="gray70",
        )
        self.lbl_progreso.pack(side="bottom", pady=(5, 10))

    # ──────────────────────────────────────────────────────────────────
    #  Carga de imágenes
    # ──────────────────────────────────────────────────────────────────

    def _cargar_imagenes_desde_carpeta(self, carpeta_path) -> None:
        """Carga y ordena alfabéticamente los archivos de imagen de *carpeta_path*."""
        carpeta = Path(carpeta_path)
        self.carpeta_imagenes = carpeta
        self.imagenes_ordenadas = []
        self._image_cache.clear()

        if not carpeta.exists() or not carpeta.is_dir():
            return

        extensiones = {".jpg", ".jpeg", ".JPG", ".JPEG", ".png", ".PNG"}
        archivos = [
            f for f in sorted(carpeta.iterdir()) if f.suffix in extensiones
        ]
        self.imagenes_ordenadas = archivos

        # Precargar TODAS las imágenes (estímulos y páginas de respuesta)
        for idx_imagen, ruta in enumerate(self.imagenes_ordenadas):
            try:
                pil_img = Image.open(str(ruta))
                ctk_img = ctk.CTkImage(
                    light_image=pil_img,
                    dark_image=pil_img,
                    size=(500, 380),
                )
                self._image_cache[idx_imagen] = ctk_img
            except Exception:
                self._image_cache[idx_imagen] = None

    def _seleccionar_carpeta(self) -> None:
        """Abre un diálogo para elegir una carpeta de imágenes y recarga."""
        nueva_carpeta = filedialog.askdirectory(
            title="Seleccionar carpeta de imágenes",
            initialdir=str(self.carpeta_imagenes),
        )
        if nueva_carpeta:
            self._cargar_imagenes_desde_carpeta(nueva_carpeta)
            self.lbl_carpeta.configure(text=str(self.carpeta_imagenes))

    # ──────────────────────────────────────────────────────────────────
    #  Flujo del test
    # ──────────────────────────────────────────────────────────────────

    def _mostrar_item_actual(self) -> None:
        """Configura la UI para el ítem actual y espera a que el usuario
        pulse 'Mostrar Estímulo'."""

        if self.indice_actual >= len(self.items):
            self._finalizar_test()
            return

        item = self.items[self.indice_actual]

        # Construir etiqueta informativa
        if item.get("es_ejemplo", False):
            texto_info = f"Ejemplo {item['item']}"
        else:
            # Contar solo los ítems regulares para el denominador
            items_regulares = [
                it for it in self.items if not it.get("es_ejemplo", False)
            ]
            # Posición dentro de los regulares
            pos_regular = sum(
                1
                for it in self.items[: self.indice_actual + 1]
                if not it.get("es_ejemplo", False)
            )
            texto_info = f"Ítem {pos_regular} / {len(items_regulares)}"
        self.lbl_item_info.configure(text=texto_info)

        # Actualizar progreso global
        self.lbl_progreso.configure(
            text=f"Progreso: {self.indice_actual + 1} de {len(self.items)}"
        )

        # ── Resetear widgets en orden correcto ──
        # Quitar todos los widgets dinámicos del layout
        self.btn_mostrar.pack_forget()
        self.lbl_imagen.pack_forget()
        self.entrada_respuesta.pack_forget()
        self.btn_siguiente.pack_forget()

        # NO establecemos image=None porque CustomTkinter tiene un bug que rompe el label
        self.lbl_imagen.configure(text="")

        # Re-empaquetar solo el botón (en el orden correcto)
        self.btn_mostrar.configure(state="normal")
        self.btn_mostrar.pack(pady=10)

    def _mostrar_estimulo(self) -> None:
        """Muestra la imagen-estímulo del ítem actual durante 5 000 ms."""

        self.btn_mostrar.configure(state="disabled")
        self.btn_mostrar.pack_forget()

        # Intentar cargar la imagen correspondiente desde el caché
        idx_imagen = 2 * self.indice_actual  # pares: estímulo
        if idx_imagen < len(self.imagenes_ordenadas):
            ctk_img = self._image_cache.get(idx_imagen)
            if ctk_img is not None:
                self._ctk_image_ref = ctk_img
                self.lbl_imagen.configure(image=ctk_img, text="")
            else:
                # Fallback si no pudo cargarse en memoria
                self.lbl_imagen.configure(
                    image="",  # Usar string vacío en vez de None
                    text="[Imagen no disponible]",
                    text_color="gray60",
                )
                self._ctk_image_ref = None
        else:
            # Si solo hay 1 imagen dummy, mostrar esa siempre en caso de error, o usar fallback
            if len(self.imagenes_ordenadas) == 1 and 0 in self._image_cache:
                ctk_img = self._image_cache[0]
                if ctk_img is not None:
                    self._ctk_image_ref = ctk_img
                    self.lbl_imagen.configure(image=ctk_img, text="")
                else:
                    self.lbl_imagen.configure(
                        image="",
                        text="[Sin imagen para este ítem]",
                        text_color="gray60",
                    )
                    self._ctk_image_ref = None
            else:
                self.lbl_imagen.configure(
                    image="",
                    text="[Sin imagen para este ítem]",
                    text_color="gray60",
                )
                self._ctk_image_ref = None

        # Empaquetar la imagen AHORA que tiene contenido
        self.lbl_imagen.pack(pady=5)
        self.update_idletasks()

        # Programar cambio a la página de respuestas a los 5 s
        self._timer_id = self.after(5000, self._mostrar_pagina_respuesta)

    def _mostrar_pagina_respuesta(self) -> None:
        """Cambia la imagen al cuadernillo de respuestas y muestra el campo de entrada."""
        self._timer_id = None

        # Intentar cargar la imagen de respuesta (impar)
        idx_imagen_respuesta = 2 * self.indice_actual + 1
        if idx_imagen_respuesta < len(self.imagenes_ordenadas):
            ctk_img = self._image_cache.get(idx_imagen_respuesta)
            if ctk_img is not None:
                self._ctk_image_ref = ctk_img
                self.lbl_imagen.configure(image=ctk_img, text="")
            else:
                self.lbl_imagen.configure(
                    image="",
                    text="[Imagen de respuesta no disponible]",
                    text_color="gray60",
                )
                self._ctk_image_ref = None
        else:
            # Fallback en caso de usar la imagen dummy única
            if len(self.imagenes_ordenadas) == 1 and 0 in self._image_cache:
                ctk_img = self._image_cache[0]
                if ctk_img is not None:
                    self._ctk_image_ref = ctk_img
                    self.lbl_imagen.configure(image=ctk_img, text="")
            else:
                self.lbl_imagen.configure(
                    image="",
                    text="[Sin imagen de respuesta]",
                    text_color="gray60",
                )
                self._ctk_image_ref = None

        # Mostrar entrada y botón siguiente
        self.entrada_respuesta.delete(0, "end")
        self.entrada_respuesta.pack(pady=10)
        self.btn_siguiente.pack(pady=5)

        # Foco automático y bind de Enter
        self.entrada_respuesta.focus()
        self.entrada_respuesta.bind("<Return>", lambda e: self._registrar_respuesta())


    def _registrar_respuesta(self) -> None:
        """Lee la respuesta, puntúa y avanza al siguiente ítem."""

        respuesta_usuario = self.entrada_respuesta.get().strip()
        item = self.items[self.indice_actual]

        respuesta_correcta = item.get("respuesta_correcta", [])
        puntuacion = MotorEvaluacion.evaluar_dibujos_puntuacion(
            respuesta_usuario, respuesta_correcta
        )

        # Almacenar resultado
        resultado_item = {
            "item": item["item"],
            "es_ejemplo": item.get("es_ejemplo", False),
            "respuesta_correcta": respuesta_correcta,
            "respuesta_usuario": respuesta_usuario,
            "puntuacion": puntuacion,
        }
        self.resultados["items"].append(resultado_item)

        # Sumar puntuación directa (solo ítems regulares)
        if not item.get("es_ejemplo", False):
            self.resultados["puntuacion_directa_total"] += puntuacion

        # Desvincular Enter para evitar dobles envíos
        self.entrada_respuesta.unbind("<Return>")

        # Avanzar
        self.indice_actual += 1
        self._mostrar_item_actual()

    # ──────────────────────────────────────────────────────────────────
    #  Finalización
    # ──────────────────────────────────────────────────────────────────

    def _finalizar_test(self) -> None:
        """Muestra mensaje de finalización e invoca el callback."""

        # Ocultar controles de prueba
        self.btn_mostrar.pack_forget()
        self.entrada_respuesta.pack_forget()
        self.btn_siguiente.pack_forget()
        self.lbl_imagen.pack_forget()

        total = self.resultados["puntuacion_directa_total"]
        self.lbl_item_info.configure(
            text="¡Prueba finalizada!",
            font=("Arial", 20, "bold"),
        )
        self.lbl_progreso.configure(
            text=f"Puntuación directa total: {total}",
        )

        if self.on_complete is not None:
            self.on_complete()

    # ──────────────────────────────────────────────────────────────────
    #  Métodos públicos
    # ──────────────────────────────────────────────────────────────────

    def obtener_resultados(self) -> dict:
        """Devuelve el diccionario completo de resultados."""
        return self.resultados

    def reiniciar(self) -> None:
        """Reinicia todo el estado para volver a empezar la prueba."""

        # Cancelar temporizador pendiente
        if self._timer_id is not None:
            self.after_cancel(self._timer_id)
            self._timer_id = None

        self.indice_actual = 0
        self.resultados = {
            "items": [],
            "puntuacion_directa_total": 0,
        }
        self._ctk_image_ref = None

        # Recargar ítems por si el JSON cambió
        self.items = self.motor.obtener_items_dibujos()

        # Recargar imágenes
        self._cargar_imagenes_desde_carpeta(self.carpeta_imagenes)

        # Restaurar UI
        self.lbl_item_info.configure(font=("Arial", 16))
        self._mostrar_item_actual()
