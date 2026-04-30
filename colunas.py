import customtkinter as ctk
import threading
from tkinter import messagebox

class ColunaBusca(ctk.CTkFrame):
    def __init__(self, master, banco):
        # Definimos uma largura sugerida aqui
        super().__init__(master, width=200) 
        
        # ESSA LINHA É A CHAVE: impede que o frame mude de tamanho pelo conteúdo
        self.pack_propagate(False) 
        self.banco = banco
        
        # Título/Instrução
        self.label_titulo = ctk.CTkLabel(self, text="Busca de Produto", font=("Roboto", 16, "bold"))
        self.label_titulo.pack(pady=(20, 10))

        # Input de Código
        self.entrada_codigo = ctk.CTkEntry(self, placeholder_text="Digite o código e aperte Enter")
        self.entrada_codigo.pack(fill="x", padx=20, pady=10)
        
        # Bind da tecla Enter (<Return>)
        self.entrada_codigo.bind("<Return>", self.executar_busca)

        # Área de Resultado
        self.frame_resultado = ctk.CTkFrame(self, fg_color="transparent")
        self.container_resultado = ctk.CTkFrame(self, fg_color="transparent")
        self.container_resultado.pack(fill="both", expand=True, padx=20, pady=20)

        self.label_descricao = ctk.CTkLabel(
            self.container_resultado, 
            text="Aguardando busca...", 
            wraplength=250, # Faz o texto quebrar linha se for muito longo
            font=("Roboto", 14)
        )
        self.label_descricao.pack(expand=True)

    def executar_busca(self, event=None):
        codigo = self.entrada_codigo.get().strip()
        if not codigo:
            return

        codigo = codigo.zfill(15)

        # Limpa o texto e mostra que está processando
        self.label_descricao.configure(text="Buscando...", text_color="gray")
        
        # Executa em Thread para a UI não travar durante a resposta do Access
        thread = threading.Thread(target=self.thread_busca, args=(codigo,))
        thread.daemon = True
        thread.start()

    def thread_busca(self, codigo):
        sucesso, resultado = self.banco.buscar_produto_por_codigo(codigo)
        # Atualiza a tela de volta na Thread principal
        self.after(0, self.atualizar_interface, sucesso, resultado)

    def atualizar_interface(self, sucesso, resultado):
        if sucesso:
            self.label_descricao.configure(text=resultado, text_color="white")
        else:
            self.label_descricao.configure(text=resultado, text_color="#FF5555") # Vermelho suave

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
        ctk.CTkButton(
            self,
            text="Testar ODBC",
            command=lambda: messagebox.showinfo("Teste ODBC", callback_teste()[1])
        ).pack(fill="x", padx=20, pady=5)