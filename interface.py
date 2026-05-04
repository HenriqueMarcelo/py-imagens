import customtkinter as ctk
from colunas import ColunaBusca, ColunaGaleria, ColunaAcao

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class JanelaPrincipal(ctk.CTk):
    def __init__(self, logica_banco):
        super().__init__()
        self.banco = logica_banco
        self.produto_nome_atual = ""
        
        self.title("Gerenciador de Fotos")
        self.geometry("1100x600")

        self.grid_columnconfigure((0, 1, 2), weight=1, uniform="coluna")
        self.grid_rowconfigure(0, weight=1)

        # 1. Coluna 3 (Ação) - Criamos primeiro para poder referenciar
        self.col3 = ColunaAcao(self, self.banco.testar_conexao)
        self.col3.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")

        # 2. Coluna 2 (Galeria) - Passamos a função que avisa a Coluna 3
        self.col2 = ColunaGaleria(self, callback_clique_foto=self.ao_clicar_na_foto)
        self.col2.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        # 3. Coluna 1 (Busca)
        self.col1 = ColunaBusca(self, self.banco, self.ao_selecionar_produto)
        self.col1.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

    def ao_selecionar_produto(self, sucesso, resultado, codigo=""):
        """Chamado quando o produto é buscado na Coluna 1"""
        if sucesso:
            self.produto_nome_atual = resultado
            self.col2.alternar_estado(True, resultado, codigo)
        else:
            self.produto_nome_atual = ""
            self.col2.alternar_estado(False)
        
        # Sempre que buscar um novo produto, limpamos a coluna de ação
        self.col3.resetar()

    def ao_clicar_na_foto(self, numero_foto):
        self.col3.preparar_edicao(numero_foto, self.produto_nome_atual)