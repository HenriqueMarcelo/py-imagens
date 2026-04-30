import customtkinter as ctk
from colunas import ColunaBusca, ColunaGaleria, ColunaAcao

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JanelaPrincipal(ctk.CTk):
    def __init__(self, logica_banco):
        super().__init__()
        self.banco = logica_banco
        
        self.title("Gerenciador de Fotos")
        self.geometry("1100x600")

        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="coluna")
        self.grid_rowconfigure(0, weight=1)

        # 1. Criar as colunas
        self.col2 = ColunaGaleria(self)
        self.col2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # Passamos uma função (callback) para a Coluna 1
        self.col1 = ColunaBusca(self, self.banco, self.ao_selecionar_produto)
        self.col1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.col3 = ColunaAcao(self, self.banco.testar_conexao)
        self.col3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

    def ao_selecionar_produto(self, sucesso, resultado):
        """Esta função é chamada sempre que uma busca termina"""
        if sucesso:
            self.col2.mostrar_galeria(resultado)
        else:
            self.col2.resetar_galeria()