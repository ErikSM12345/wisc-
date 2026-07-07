import customtkinter
from interfaz_digitos import VistaDigitos
from interfaz_dibujos import VistaDibujos

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

class App(customtkinter.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("Simulador WISC-V")
        self.geometry("1024x768")
        
        # Crear CTkTabview central
        self.tabview = customtkinter.CTkTabview(self)
        self.tabview.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Añadir las pestañas
        self.tab_digitos = self.tabview.add("Test de Dígitos")
        self.tab_dibujos = self.tabview.add("Span de Dibujos")
        
        # Instanciar las vistas dentro de sus respectivas pestañas
        self.vista_digitos = VistaDigitos(master=self.tab_digitos)
        self.vista_digitos.pack(fill="both", expand=True)
        
        self.vista_dibujos = VistaDibujos(master=self.tab_dibujos)
        self.vista_dibujos.pack(fill="both", expand=True)

if __name__ == "__main__":
    app = App()
    app.mainloop()
