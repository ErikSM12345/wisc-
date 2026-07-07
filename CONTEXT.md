Contexto del Proyecto: Simulador WISC-V

1. Visión General

Estamos desarrollando una aplicación de escritorio en Python para simular dos pruebas de evaluación psicométrica del test WISC-V: "Dígitos" y "Span de Dibujos". La prioridad es la precisión lógica y un manejo estricto del tiempo (sin latencia y sin bloquear la UI principal).

2. Stack Tecnológico Estricto

Lenguaje: Python 3.12+ (Entorno Virtual aislado).

UI: customtkinter (Obligatorio usar clases orientadas a objetos, modo oscuro, sin tkinter clásico expuesto).

Audio: pygame-ce (pygame.mixer específicamente) para reproducción asíncrona de archivos .wav pregrabados de voces de IA.

Imágenes: Pillow (PIL) para manejo de imágenes temporizadas.

Datos: Archivo estático data/datos.json (Ya existente).

3. Estructura de Directorios

wisc-v-app/
├── data/
│ └── datos.json
├── assets/
│ ├── audio/ (Archivos como 1.wav, 2.wav, intro.wav)
│ └── img/ (Archivos .png de los estímulos visuales)
└── src/
├── **init**.py
├── main.py (Punto de entrada, menú de navegación)
├── motor.py (Lógica backend, parsing de JSON, evaluación)
├── interfaz_digitos.py (Vista del Test 1)
└── interfaz_dibujos.py (Vista del Test 2)

4. Reglas Lógicas del Motor (motor.py)

El archivo datos.json ya está creado. Las respuestas del usuario deben ser evaluadas según 3 reglas (Testeables y modulares):

Dígitos Directos: Input del usuario == Array Original.

Dígitos Inversos: Input del usuario == Array Original invertido (ej. [::-1]).

Dígitos Secuenciación: Input del usuario == Array Original ordenado de menor a mayor (ej. sorted()).

Dibujos: Comparación de cadenas de letras (ignorar espacios y mayúsculas).

5. Reglas Críticas de Interfaz Gráfica

No usar time.sleep() jamás en el hilo principal. Congela CustomTkinter.

Gestión de Audio: Usar .after() de Tkinter o threading para encolar los números con 1 segundo de pausa, de forma que el usuario vea la UI viva mientras escucha. La caja de texto se desactiva durante la reproducción y se auto-enfoca al terminar.

Gestión Visual: En el test de dibujos, mostrar la imagen y disparar un .after(5000, funcion_ocultar). A los 5.0s exactos, la imagen desaparece y aparece el campo de respuesta.
