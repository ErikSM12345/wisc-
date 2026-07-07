import customtkinter as ctk
import pygame
import threading
import time
import os
from motor import MotorEvaluacion

class VistaDigitos(ctk.CTkFrame):
    def __init__(self, master, motor: MotorEvaluacion, **kwargs):
        super().__init__(master, **kwargs)
        self.motor = motor
        
        # Simulación de un estímulo (nivel actual)
        self.estimulo_actual = [2, 9, 5, 8]
        
        # Inicializar el mixer de audio
        pygame.mixer.init()
        
        self.setup_ui()
        
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        
        # Título
        self.lbl_titulo = ctk.CTkLabel(self, text="Prueba de Dígitos", font=("Arial", 20, "bold"))
        self.lbl_titulo.grid(row=0, column=0, pady=(20, 10))
        
        # Selector de Modalidad
        self.modalidad_var = ctk.StringVar(value="Directos")
        self.combo_modalidad = ctk.CTkComboBox(
            self, 
            values=["Directos", "Inversos", "Secuenciación"],
            variable=self.modalidad_var,
            state="readonly"
        )
        self.combo_modalidad.grid(row=1, column=0, pady=10)
        
        # Botón para lanzar audio
        self.btn_audio = ctk.CTkButton(
            self, 
            text="Lanzar Audio", 
            command=self.lanzar_audio
        )
        self.btn_audio.grid(row=2, column=0, pady=10)
        
        # Caja de texto (bloqueada por defecto)
        self.entrada_respuesta = ctk.CTkEntry(
            self, 
            placeholder_text="Ingrese los dígitos...", 
            width=200,
            state="disabled"
        )
        self.entrada_respuesta.grid(row=3, column=0, pady=10)
        
        # Botón para evaluar
        self.btn_evaluar = ctk.CTkButton(
            self, 
            text="Evaluar", 
            command=self.evaluar,
            state="disabled"
        )
        self.btn_evaluar.grid(row=4, column=0, pady=10)
        
        # Etiqueta para mostrar resultados
        self.lbl_resultado = ctk.CTkLabel(self, text="", font=("Arial", 14))
        self.lbl_resultado.grid(row=5, column=0, pady=20)
        
    def lanzar_audio(self):
        """Bloquea la UI e inicia la reproducción en un hilo separado."""
        self.btn_audio.configure(state="disabled")
        self.combo_modalidad.configure(state="disabled")
        self.entrada_respuesta.configure(state="disabled")
        self.btn_evaluar.configure(state="disabled")
        self.entrada_respuesta.delete(0, ctk.END)
        self.lbl_resultado.configure(text="Escuchando audio...", text_color="yellow")
        
        # Usar threading para no bloquear la UI con los tiempos de espera
        threading.Thread(target=self._reproducir_secuencia, daemon=True).start()
        
    def _reproducir_secuencia(self):
        """Reproduce la secuencia de audios simulados con 1 segundo de pausa entre ellos."""
        for num in self.estimulo_actual:
            ruta_audio = f"assets/audio/{num}.wav"
            
            # Simulamos que existe el audio e intentamos reproducirlo
            if os.path.exists(ruta_audio):
                try:
                    sonido = pygame.mixer.Sound(ruta_audio)
                    sonido.play()
                    # Esperar a que termine de reproducirse el sonido actual
                    while pygame.mixer.get_busy():
                        time.sleep(0.1)
                except Exception as e:
                    print(f"Error reproduciendo {ruta_audio}: {e}")
            else:
                # Si no existe, simulamos su tiempo de reproducción para propósitos de la prueba
                print(f"[Simulación] Reproduciendo audio de: {num}")
                time.sleep(0.5)
            
            # 1 segundo de silencio entre números
            time.sleep(1.0)
            
        # Habilitar la entrada desde el hilo principal
        self.after(0, self._finalizar_audio)
        
    def _finalizar_audio(self):
        """Habilita la caja de texto y la prepara para la entrada del usuario."""
        self.lbl_resultado.configure(text="¡Ingrese su respuesta!", text_color="white")
        self.entrada_respuesta.configure(state="normal")
        self.btn_evaluar.configure(state="normal")
        self.combo_modalidad.configure(state="normal")
        self.btn_audio.configure(state="normal")
        
        # Dar foco automáticamente a la caja de texto
        self.entrada_respuesta.focus()
        
    def evaluar(self):
        """Llama a MotorEvaluacion dependiendo de la modalidad elegida."""
        respuesta_usuario = self.entrada_respuesta.get()
        modalidad = self.modalidad_var.get()
        
        if not respuesta_usuario.strip():
            self.lbl_resultado.configure(text="Por favor, ingrese una respuesta.", text_color="orange")
            return
            
        es_correcto = False
        
        try:
            if modalidad == "Directos":
                es_correcto = self.motor.evaluar_digitos_directos(respuesta_usuario, self.estimulo_actual)
            elif modalidad == "Inversos":
                es_correcto = self.motor.evaluar_digitos_inversos(respuesta_usuario, self.estimulo_actual)
            elif modalidad == "Secuenciación":
                es_correcto = self.motor.evaluar_digitos_secuenciacion(respuesta_usuario, self.estimulo_actual)
                
            if es_correcto:
                self.lbl_resultado.configure(text="¡Correcto! Respuesta válida.", text_color="green")
            else:
                self.lbl_resultado.configure(text="Incorrecto. Intente nuevamente.", text_color="red")
        except Exception as e:
            self.lbl_resultado.configure(text=f"Error al evaluar: {str(e)}", text_color="red")
