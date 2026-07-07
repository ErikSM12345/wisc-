"""
Punto de entrada principal del Simulador WISC-V.
Pantalla de inicio → Pestañas de pruebas → Resultados → Exportar PDF.
"""

import customtkinter as ctk
from pathlib import Path
from tkinter import messagebox
import os
import sys

# Asegurar que el directorio raíz del proyecto esté en el path
_project_root = str(Path(__file__).resolve().parent.parent)
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from src.motor import MotorEvaluacion
from src.interfaz_digitos import VistaDigitos
from src.interfaz_dibujos import VistaDibujos

# ─── Configuración global de CustomTkinter ───────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class App(ctk.CTk):
    """Ventana principal del Simulador WISC-V."""

    def __init__(self):
        super().__init__()

        self.title("Simulador WISC-V")
        self.geometry("950x700")
        self.minsize(800, 600)

        # Motor de evaluación compartido
        self.motor = MotorEvaluacion()

        # Estado de finalización de tests
        self._digitos_completado = False
        self._dibujos_completado = False

        # Mostrar pantalla de inicio
        self._crear_pantalla_inicio()

    # ─── Pantalla de Inicio ──────────────────────────────────────────

    def _crear_pantalla_inicio(self):
        """Frame de bienvenida con el botón 'Comenzar prueba'."""
        self.frame_inicio = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_inicio.pack(fill="both", expand=True)

        # Contenedor central
        contenedor = ctk.CTkFrame(self.frame_inicio, fg_color="transparent")
        contenedor.place(relx=0.5, rely=0.45, anchor="center")

        ctk.CTkLabel(
            contenedor,
            text="🧠",
            font=("Arial", 64),
        ).pack(pady=(0, 10))

        ctk.CTkLabel(
            contenedor,
            text="Simulador WISC-V",
            font=("Arial", 36, "bold"),
        ).pack(pady=(0, 5))

        ctk.CTkLabel(
            contenedor,
            text="Memoria de Trabajo — Dígitos & Span de Dibujos",
            font=("Arial", 16),
            text_color="gray60",
        ).pack(pady=(0, 40))

        ctk.CTkButton(
            contenedor,
            text="Comenzar Prueba",
            font=("Arial", 20, "bold"),
            width=280,
            height=55,
            corner_radius=12,
            command=self._iniciar_pruebas,
        ).pack()

        # Versión
        ctk.CTkLabel(
            self.frame_inicio,
            text="v1.0 · Python + CustomTkinter",
            font=("Arial", 11),
            text_color="gray40",
        ).pack(side="bottom", pady=10)

    # ─── Iniciar Pruebas ─────────────────────────────────────────────

    def _iniciar_pruebas(self):
        """Oculta la pantalla de inicio y muestra las pestañas de pruebas."""
        self.frame_inicio.destroy()

        # Crear TabView
        self.tabview = ctk.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)

        # Pestañas
        self.tab_digitos = self.tabview.add("Test de Dígitos")
        self.tab_dibujos = self.tabview.add("Span de Dibujos")
        self.tab_resultados = self.tabview.add("Resultados")

        # Vistas de pruebas
        self.vista_digitos = VistaDigitos(
            master=self.tab_digitos,
            motor=self.motor,
            on_complete=self._on_digitos_completado,
        )
        self.vista_digitos.pack(fill="both", expand=True)

        self.vista_dibujos = VistaDibujos(
            master=self.tab_dibujos,
            motor=self.motor,
            on_complete=self._on_dibujos_completado,
        )
        self.vista_dibujos.pack(fill="both", expand=True)

        # Vista de resultados (inicialmente vacía)
        self._crear_tab_resultados()

    # ─── Callbacks de Finalización ───────────────────────────────────

    def _on_digitos_completado(self):
        """Callback cuando el test de dígitos finaliza."""
        self._digitos_completado = True
        self._actualizar_resultados()

    def _on_dibujos_completado(self):
        """Callback cuando el test de dibujos finaliza."""
        self._dibujos_completado = True
        self._actualizar_resultados()

    # ─── Pestaña de Resultados ───────────────────────────────────────

    def _crear_tab_resultados(self):
        """Crea la pestaña de resultados con un mensaje de espera."""
        self.frame_resultados = ctk.CTkScrollableFrame(
            self.tab_resultados, fg_color="transparent"
        )
        self.frame_resultados.pack(fill="both", expand=True, padx=10, pady=10)

        self.lbl_espera = ctk.CTkLabel(
            self.frame_resultados,
            text="Complete ambos tests para ver los resultados.",
            font=("Arial", 16),
            text_color="gray60",
        )
        self.lbl_espera.pack(pady=40)

        # Botón de recalcular
        self.btn_calcular = ctk.CTkButton(
            self.frame_resultados,
            text="Calcular Resultados",
            font=("Arial", 14),
            command=self._actualizar_resultados,
        )
        self.btn_calcular.pack(pady=10)

    def _actualizar_resultados(self):
        """Recalcula y muestra los resultados si ambos tests están completos."""
        # Limpiar frame
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

        if not self._digitos_completado and not self._dibujos_completado:
            ctk.CTkLabel(
                self.frame_resultados,
                text="Complete al menos un test para ver resultados parciales.",
                font=("Arial", 16),
                text_color="gray60",
            ).pack(pady=40)
            return

        # ── Título ──
        ctk.CTkLabel(
            self.frame_resultados,
            text="📊  Resultados del Simulador WISC-V",
            font=("Arial", 22, "bold"),
        ).pack(pady=(10, 20))

        # ── Resultados de Dígitos ──
        pd_digitos = 0
        resultados_dig = None
        if self._digitos_completado:
            resultados_dig = self.vista_digitos.obtener_resultados()
            pd_digitos = resultados_dig.get("puntuacion_directa_total", 0)
            self._mostrar_resultados_digitos(resultados_dig)

        # ── Resultados de Dibujos ──
        pd_dibujos = 0
        resultados_dib = None
        if self._dibujos_completado:
            resultados_dib = self.vista_dibujos.obtener_resultados()
            pd_dibujos = resultados_dib.get("puntuacion_directa_total", 0)
            self._mostrar_resultados_dibujos(resultados_dib)

        # ── Baremos ──
        if self._digitos_completado and self._dibujos_completado:
            self._mostrar_baremos(pd_digitos, pd_dibujos, resultados_dig, resultados_dib)

        # ── Botón Exportar PDF ──
        ctk.CTkButton(
            self.frame_resultados,
            text="📄  Exportar Informe PDF",
            font=("Arial", 16, "bold"),
            width=250,
            height=45,
            command=lambda: self._exportar_pdf(
                pd_digitos, pd_dibujos, resultados_dig, resultados_dib
            ),
        ).pack(pady=30)

    def _mostrar_resultados_digitos(self, resultados: dict):
        """Muestra el desglose de resultados de dígitos."""
        self._crear_seccion_titulo("Test de Dígitos")

        nombre_modalidad = {
            "orden_directo": "Orden Directo",
            "orden_inverso": "Orden Inverso",
            "orden_creciente": "Secuenciación",
        }

        for modalidad_key in ["orden_directo", "orden_inverso", "orden_creciente"]:
            datos_mod = resultados.get(modalidad_key, {})
            items = datos_mod.get("items", [])
            total = datos_mod.get("puntuacion_total", 0)

            frame_mod = ctk.CTkFrame(self.frame_resultados, fg_color="gray20", corner_radius=8)
            frame_mod.pack(fill="x", padx=10, pady=5)

            ctk.CTkLabel(
                frame_mod,
                text=f"  {nombre_modalidad.get(modalidad_key, modalidad_key)}  —  Puntuación: {total}",
                font=("Arial", 14, "bold"),
                anchor="w",
            ).pack(fill="x", padx=15, pady=(8, 2))

            # Detalle por ítem
            for item_res in items:
                if item_res.get("es_ejemplo"):
                    continue
                intentos = item_res.get("intentos_resultado", [])
                detalles = []
                for intento in intentos:
                    marca = "✓" if intento.get("correcto") else "✗"
                    detalles.append(
                        f"Int.{intento.get('intento')}: {intento.get('respuesta_usuario', '—')} {marca}"
                    )
                linea = f"    Ítem {item_res['item']}: {' | '.join(detalles)}  →  {item_res.get('puntuacion', 0)} pts"
                ctk.CTkLabel(
                    frame_mod,
                    text=linea,
                    font=("Consolas", 12),
                    anchor="w",
                    text_color="gray70",
                ).pack(fill="x", padx=15, pady=1)

            # Espacio final
            ctk.CTkLabel(frame_mod, text="").pack(pady=2)

        ctk.CTkLabel(
            self.frame_resultados,
            text=f"Puntuación Directa Total (Dígitos): {resultados.get('puntuacion_directa_total', 0)}",
            font=("Arial", 15, "bold"),
            text_color="#4fc3f7",
        ).pack(pady=(5, 15))

    def _mostrar_resultados_dibujos(self, resultados: dict):
        """Muestra el desglose de resultados de dibujos."""
        self._crear_seccion_titulo("Span de Dibujos")

        frame_dib = ctk.CTkFrame(self.frame_resultados, fg_color="gray20", corner_radius=8)
        frame_dib.pack(fill="x", padx=10, pady=5)

        for item_res in resultados.get("items", []):
            if item_res.get("es_ejemplo"):
                continue
            esperado = "".join(item_res.get("respuesta_correcta", []))
            usuario = item_res.get("respuesta_usuario", "—")
            pts = item_res.get("puntuacion", 0)
            texto_pts = f"{pts} pts"
            if pts == 2:
                color = "#4caf50"
            elif pts == 1:
                color = "#ff9800"
            else:
                color = "#f44336"

            linea = f"  Ítem {item_res['item']:>3s}: esperado={esperado}  respuesta={usuario}  →  {texto_pts}"
            ctk.CTkLabel(
                frame_dib,
                text=linea,
                font=("Consolas", 12),
                anchor="w",
                text_color=color,
            ).pack(fill="x", padx=15, pady=1)

        ctk.CTkLabel(frame_dib, text="").pack(pady=2)

        ctk.CTkLabel(
            self.frame_resultados,
            text=f"Puntuación Directa Total (Dibujos): {resultados.get('puntuacion_directa_total', 0)}",
            font=("Arial", 15, "bold"),
            text_color="#4fc3f7",
        ).pack(pady=(5, 15))

    def _mostrar_baremos(self, pd_digitos, pd_dibujos, res_dig, res_dib):
        """Muestra la tabla de conversión de baremos y el IMT."""
        self._crear_seccion_titulo("Conversión de Baremos")

        # Puntuación Escalar
        pe_digitos = self.motor.calcular_puntuacion_escalar(pd_digitos, "DS_d")
        pe_dibujos = self.motor.calcular_puntuacion_escalar(pd_dibujos, "PS_sd")

        frame_baremos = ctk.CTkFrame(self.frame_resultados, fg_color="gray20", corner_radius=8)
        frame_baremos.pack(fill="x", padx=10, pady=5)

        datos_baremo = [
            ("Subtest", "Punt. Directa", "Punt. Escalar"),
            ("Dígitos (DS)", str(pd_digitos), str(pe_digitos or "N/A")),
            ("Span Dibujos (PS)", str(pd_dibujos), str(pe_dibujos or "N/A")),
        ]

        for i, fila in enumerate(datos_baremo):
            frame_fila = ctk.CTkFrame(frame_baremos, fg_color="transparent")
            frame_fila.pack(fill="x", padx=10, pady=2)
            for j, celda in enumerate(fila):
                font = ("Arial", 13, "bold") if i == 0 else ("Arial", 13)
                ctk.CTkLabel(
                    frame_fila, text=celda, font=font, width=180, anchor="center"
                ).pack(side="left", padx=5)

        ctk.CTkLabel(frame_baremos, text="").pack(pady=3)

        # IMT
        if pe_digitos is not None and pe_dibujos is not None:
            imt_data = self.motor.calcular_imt(pe_digitos, pe_dibujos)
            if imt_data:
                frame_imt = ctk.CTkFrame(
                    self.frame_resultados, fg_color="gray20", corner_radius=8
                )
                frame_imt.pack(fill="x", padx=10, pady=5)

                ctk.CTkLabel(
                    frame_imt,
                    text="  Índice de Memoria de Trabajo (IMT / WMI)",
                    font=("Arial", 14, "bold"),
                    anchor="w",
                ).pack(fill="x", padx=15, pady=(8, 5))

                info_lines = [
                    f"  Suma Puntuaciones Escalares: {imt_data['suma_pe']}",
                    f"  IMT (WMI): {imt_data['imt_wmi']}",
                    f"  Rango Percentil: {imt_data['rango_percentil']}",
                    f"  Intervalo Confianza 90%: {imt_data['intervalo_confianza_90']}",
                    f"  Intervalo Confianza 95%: {imt_data['intervalo_confianza_95']}",
                ]
                for line in info_lines:
                    ctk.CTkLabel(
                        frame_imt,
                        text=line,
                        font=("Consolas", 13),
                        anchor="w",
                        text_color="#81c784",
                    ).pack(fill="x", padx=15, pady=1)

                ctk.CTkLabel(frame_imt, text="").pack(pady=3)

        # Discontinuación
        self._mostrar_discontinuacion(res_dig, res_dib)

    def _mostrar_discontinuacion(self, res_dig, res_dib):
        """Muestra los puntos teóricos de discontinuación."""
        self._crear_seccion_titulo("Puntos de Discontinuación (referencia)")

        frame_disc = ctk.CTkFrame(self.frame_resultados, fg_color="gray20", corner_radius=8)
        frame_disc.pack(fill="x", padx=10, pady=5)

        if res_dig:
            for modalidad_key, nombre in [
                ("orden_directo", "Orden Directo"),
                ("orden_inverso", "Orden Inverso"),
                ("orden_creciente", "Secuenciación"),
            ]:
                items_mod = res_dig.get(modalidad_key, {}).get("items", [])
                punto = MotorEvaluacion.detectar_discontinuacion_digitos(items_mod)
                if punto:
                    texto = f"  ⚠ {nombre}: se habría discontinuado en el ítem {punto}"
                    color = "#ff9800"
                else:
                    texto = f"  ✓ {nombre}: no se alcanzó punto de discontinuación"
                    color = "#66bb6a"
                ctk.CTkLabel(
                    frame_disc, text=texto, font=("Arial", 12), anchor="w", text_color=color
                ).pack(fill="x", padx=15, pady=2)

        if res_dib:
            punto = MotorEvaluacion.detectar_discontinuacion_dibujos(
                res_dib.get("items", [])
            )
            if punto:
                texto = f"  ⚠ Span de Dibujos: se habría discontinuado en el ítem {punto}"
                color = "#ff9800"
            else:
                texto = f"  ✓ Span de Dibujos: no se alcanzó punto de discontinuación"
                color = "#66bb6a"
            ctk.CTkLabel(
                frame_disc, text=texto, font=("Arial", 12), anchor="w", text_color=color
            ).pack(fill="x", padx=15, pady=2)

        ctk.CTkLabel(frame_disc, text="").pack(pady=3)

    def _crear_seccion_titulo(self, texto: str):
        """Crea un separador visual con título de sección."""
        ctk.CTkLabel(
            self.frame_resultados,
            text=f"━━  {texto}  ━━",
            font=("Arial", 16, "bold"),
            text_color="gray50",
        ).pack(pady=(15, 5))

    # ─── Exportación PDF ─────────────────────────────────────────────

    def _exportar_pdf(self, pd_digitos, pd_dibujos, res_dig, res_dib):
        """Genera un informe PDF con todos los resultados."""
        try:
            from fpdf import FPDF
        except ImportError:
            messagebox.showerror(
                "Dependencia faltante",
                "Instala fpdf2 para exportar PDF:\n\npip install fpdf2",
            )
            return

        from tkinter import filedialog

        ruta = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF", "*.pdf")],
            title="Guardar informe PDF",
            initialname="informe_wisc_v.pdf",
        )
        if not ruta:
            return

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        # ── Título ──
        pdf.set_font("Helvetica", "B", 22)
        pdf.cell(0, 15, "Informe Simulador WISC-V", ln=True, align="C")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 8, "Memoria de Trabajo - Digitos & Span de Dibujos", ln=True, align="C")
        pdf.ln(10)

        # ── Dígitos ──
        if res_dig:
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "Test de Digitos", ln=True)
            pdf.ln(3)

            nombre_mod = {
                "orden_directo": "Orden Directo",
                "orden_inverso": "Orden Inverso",
                "orden_creciente": "Secuenciacion",
            }

            for mod_key in ["orden_directo", "orden_inverso", "orden_creciente"]:
                datos_mod = res_dig.get(mod_key, {})
                items = datos_mod.get("items", [])
                total = datos_mod.get("puntuacion_total", 0)

                pdf.set_font("Helvetica", "B", 12)
                pdf.cell(0, 8, f"{nombre_mod.get(mod_key, mod_key)} - Total: {total}", ln=True)

                # Tabla
                pdf.set_font("Helvetica", "B", 9)
                pdf.cell(20, 7, "Item", 1, 0, "C")
                pdf.cell(50, 7, "Int.1 Resp.", 1, 0, "C")
                pdf.cell(20, 7, "Int.1", 1, 0, "C")
                pdf.cell(50, 7, "Int.2 Resp.", 1, 0, "C")
                pdf.cell(20, 7, "Int.2", 1, 0, "C")
                pdf.cell(20, 7, "Pts", 1, 1, "C")

                pdf.set_font("Helvetica", "", 9)
                for item_res in items:
                    if item_res.get("es_ejemplo"):
                        continue
                    intentos = item_res.get("intentos_resultado", [])
                    i1 = intentos[0] if len(intentos) > 0 else {}
                    i2 = intentos[1] if len(intentos) > 1 else {}

                    pdf.cell(20, 6, str(item_res["item"]), 1, 0, "C")
                    pdf.cell(50, 6, str(i1.get("respuesta_usuario", "-")), 1, 0, "C")
                    pdf.cell(20, 6, "OK" if i1.get("correcto") else "X", 1, 0, "C")
                    pdf.cell(50, 6, str(i2.get("respuesta_usuario", "-")), 1, 0, "C")
                    pdf.cell(20, 6, "OK" if i2.get("correcto") else "X", 1, 0, "C")
                    pdf.cell(20, 6, str(item_res.get("puntuacion", 0)), 1, 1, "C")

                pdf.ln(5)

            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(
                0, 10,
                f"Puntuacion Directa Total (Digitos): {res_dig.get('puntuacion_directa_total', 0)}",
                ln=True,
            )
            pdf.ln(5)

        # ── Dibujos ──
        if res_dib:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "Span de Dibujos", ln=True)
            pdf.ln(3)

            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(20, 7, "Item", 1, 0, "C")
            pdf.cell(40, 7, "Esperado", 1, 0, "C")
            pdf.cell(40, 7, "Respuesta", 1, 0, "C")
            pdf.cell(20, 7, "Pts", 1, 1, "C")

            pdf.set_font("Helvetica", "", 9)
            for item_res in res_dib.get("items", []):
                if item_res.get("es_ejemplo"):
                    continue
                esperado = "".join(item_res.get("respuesta_correcta", []))
                pdf.cell(20, 6, str(item_res["item"]), 1, 0, "C")
                pdf.cell(40, 6, esperado, 1, 0, "C")
                pdf.cell(40, 6, str(item_res.get("respuesta_usuario", "-")), 1, 0, "C")
                pdf.cell(20, 6, str(item_res.get("puntuacion", 0)), 1, 1, "C")

            pdf.ln(5)
            pdf.set_font("Helvetica", "B", 13)
            pdf.cell(
                0, 10,
                f"Puntuacion Directa Total (Dibujos): {res_dib.get('puntuacion_directa_total', 0)}",
                ln=True,
            )
            pdf.ln(5)

        # ── Baremos ──
        if res_dig and res_dib:
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 16)
            pdf.cell(0, 10, "Conversion de Baremos", ln=True)
            pdf.ln(5)

            pe_digitos = self.motor.calcular_puntuacion_escalar(pd_digitos, "DS_d")
            pe_dibujos = self.motor.calcular_puntuacion_escalar(pd_dibujos, "PS_sd")

            pdf.set_font("Helvetica", "B", 10)
            pdf.cell(60, 8, "Subtest", 1, 0, "C")
            pdf.cell(40, 8, "P. Directa", 1, 0, "C")
            pdf.cell(40, 8, "P. Escalar", 1, 1, "C")

            pdf.set_font("Helvetica", "", 10)
            pdf.cell(60, 7, "Digitos (DS)", 1, 0, "C")
            pdf.cell(40, 7, str(pd_digitos), 1, 0, "C")
            pdf.cell(40, 7, str(pe_digitos or "N/A"), 1, 1, "C")
            pdf.cell(60, 7, "Span Dibujos (PS)", 1, 0, "C")
            pdf.cell(40, 7, str(pd_dibujos), 1, 0, "C")
            pdf.cell(40, 7, str(pe_dibujos or "N/A"), 1, 1, "C")
            pdf.ln(8)

            # IMT
            if pe_digitos is not None and pe_dibujos is not None:
                imt_data = self.motor.calcular_imt(pe_digitos, pe_dibujos)
                if imt_data:
                    pdf.set_font("Helvetica", "B", 14)
                    pdf.cell(0, 10, "Indice de Memoria de Trabajo (IMT / WMI)", ln=True)
                    pdf.ln(3)

                    pdf.set_font("Helvetica", "", 11)
                    info = [
                        f"Suma Puntuaciones Escalares: {imt_data['suma_pe']}",
                        f"IMT (WMI): {imt_data['imt_wmi']}",
                        f"Rango Percentil: {imt_data['rango_percentil']}",
                        f"Intervalo Confianza 90%: {imt_data['intervalo_confianza_90']}",
                        f"Intervalo Confianza 95%: {imt_data['intervalo_confianza_95']}",
                    ]
                    for line in info:
                        pdf.cell(0, 7, line, ln=True)
                    pdf.ln(5)

            # Discontinuación
            pdf.set_font("Helvetica", "B", 14)
            pdf.cell(0, 10, "Puntos de Discontinuacion (referencia)", ln=True)
            pdf.ln(3)
            pdf.set_font("Helvetica", "", 10)

            for mod_key, nombre in [
                ("orden_directo", "Orden Directo"),
                ("orden_inverso", "Orden Inverso"),
                ("orden_creciente", "Secuenciacion"),
            ]:
                items_mod = res_dig.get(mod_key, {}).get("items", [])
                punto = MotorEvaluacion.detectar_discontinuacion_digitos(items_mod)
                if punto:
                    pdf.cell(0, 6, f"  ! {nombre}: discontinuacion en item {punto}", ln=True)
                else:
                    pdf.cell(0, 6, f"  OK {nombre}: sin discontinuacion", ln=True)

            punto_dib = MotorEvaluacion.detectar_discontinuacion_dibujos(
                res_dib.get("items", [])
            )
            if punto_dib:
                pdf.cell(0, 6, f"  ! Span de Dibujos: discontinuacion en item {punto_dib}", ln=True)
            else:
                pdf.cell(0, 6, f"  OK Span de Dibujos: sin discontinuacion", ln=True)

        # Guardar
        try:
            pdf.output(ruta)
            messagebox.showinfo("Éxito", f"Informe guardado en:\n{ruta}")
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo guardar el PDF:\n{e}")


# ─── Punto de Entrada ────────────────────────────────────────────────

if __name__ == "__main__":
    app = App()
    app.mainloop()
