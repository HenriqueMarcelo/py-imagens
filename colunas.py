import customtkinter as ctk

class ColunaLista(ctk.CTkFrame):
    def __init__(self, master, produtos):
        super().__init__(master)
        
        self.entrada_busca = ctk.CTkEntry(self, placeholder_text="Buscar produto...")
        self.entrada_busca.pack(fill="x", padx=10, pady=(10, 5))

        self.scroll = ctk.CTkScrollableFrame(self, label_text="Produtos")
        self.scroll.pack(fill="both", expand=True, padx=10, pady=10)

        for prod in produtos:
            btn = ctk.CTkButton(self.scroll, text=f"{prod['id']} - {prod['nome']}", 
                                anchor="w", fg_color="transparent", text_color="white", hover_color="#2b2b2b")
            btn.pack(fill="x")

class ColunaGaleria(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        ctk.CTkLabel(self, text="Imagens do Produto", font=("Roboto", 16, "bold")).pack(pady=10)
        
        self.grid_fotos = ctk.CTkFrame(self, fg_color="transparent")
        self.grid_fotos.pack(expand=True)

        for i in range(4):
            txt = "Imagem" if i < 2 else "+"
            btn = ctk.CTkButton(self.grid_fotos, text=txt, width=120, height=120, corner_radius=10)
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)

class ColunaAcao(ctk.CTkFrame):
    def __init__(self, master, callback_teste):
        super().__init__(master)
        
        ctk.CTkButton(self, text="Escolher no computador").pack(fill="x", padx=20, pady=(20, 5))
        ctk.CTkButton(self, text="Buscar no Google").pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self, text="Colar Imagem").pack(fill="x", padx=20, pady=5)

        self.preview = ctk.CTkLabel(self, text="Pré-visualização", width=200, height=200, 
                                    fg_color="#1a1a1a", corner_radius=10)
        self.preview.pack(pady=20)

        ctk.CTkButton(self, text="Salvar", fg_color="green").pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(self, text="Testar ODBC", command=callback_teste).pack(fill="x", padx=20, pady=5)