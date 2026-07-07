import customtkinter as ctk
from PIL import Image
from motor import MotorEvaluacion

class VistaDibujos(ctk.CTkFrame):
    def __init__(self, master, motor=None, **kwargs):
        super().__init__(master, **kwargs)
        self.motor = motor
        
        # Datos de prueba para la evaluación
        self.respuesta_actual = ["A", "B", "C"]
        
        # Título
        self.lbl_titulo = ctk.CTkLabel(self, text="Test de Span de Dibujos", font=("Inter", 20, "bold"))
        self.lbl_titulo.pack(pady=(20, 10))
        
        # Botón para mostrar el estímulo
        self.btn_mostrar = ctk.CTkButton(self, text="Mostrar Estímulo", command=self.mostrar_estimulo)
        self.btn_mostrar.pack(pady=10)
        
        # Label para contener la imagen (oculto inicialmente)
        self.img_label = ctk.CTkLabel(self, text="")
        
        # Campos de respuesta (ocultos inicialmente)
        self.entry_respuesta = ctk.CTkEntry(self, placeholder_text="Ej: A B C", width=200)
        self.btn_evaluar = ctk.CTkButton(self, text="Evaluar Respuesta", command=self.evaluar)
        
        # Label para el resultado
        self.lbl_resultado = ctk.CTkLabel(self, text="", font=("Inter", 16, "bold"))
        self.lbl_resultado.pack(pady=10)

    def mostrar_estimulo(self):
        # Generar una imagen sólida dummy con Pillow
        dummy_image = Image.new('RGB', (400, 300), color=(70, 130, 180)) # Azul acero
        self.ctk_image = ctk.CTkImage(light_image=dummy_image, dark_image=dummy_image, size=(400, 300))
        
        self.img_label.configure(image=self.ctk_image)
        self.img_label.pack(pady=10)
        
        # Deshabilitar botón mientras se muestra la imagen
        self.btn_mostrar.configure(state="disabled")
        
        # Ocultar controles de respuesta si estaban visibles
        self.entry_respuesta.pack_forget()
        self.btn_evaluar.pack_forget()
        self.lbl_resultado.configure(text="")
        
        # Iniciar temporizador de 5 segundos exactos (5000 ms)
        self.after(5000, self.ocultar_estimulo)

    def ocultar_estimulo(self):
        # Ocultar la imagen de la pantalla
        self.img_label.pack_forget()
        
        # Habilitar el botón nuevamente
        self.btn_mostrar.configure(state="normal")
        
        # Mostrar controles de respuesta
        self.entry_respuesta.pack(pady=10)
        self.entry_respuesta.delete(0, 'end')
        self.btn_evaluar.pack(pady=10)
        
        # Foco automático para que el usuario pueda escribir inmediatamente
        self.entry_respuesta.focus()

    def evaluar(self):
        user_input = self.entry_respuesta.get()
        
        # Evaluar conectando con el motor
        es_correcto = MotorEvaluacion.evaluar_dibujos(user_input, self.respuesta_actual)
        
        if es_correcto:
            self.lbl_resultado.configure(text="¡Respuesta Correcta!", text_color="#2ecc71") # Verde
        else:
            esperado = "".join(self.respuesta_actual).upper()
            self.lbl_resultado.configure(text=f"Incorrecto. Se esperaba: {esperado}", text_color="#e74c3c") # Rojo
