import customtkinter as ctk
import threading
import os
from tkinter import messagebox
from PIL import Image
import logging
from gestor_imagens import GestorImagens

logging.basicConfig(level=logging.INFO)

class ColunaBusca(ctk.CTkFrame):
    def __init__(self, master, banco, callback_selecao):
        super().__init__(master, width=250) 
        self.pack_propagate(False) 
        self.banco = banco
        self.callback_selecao = callback_selecao

        # 1. Título
        self.label_titulo = ctk.CTkLabel(self, text="Busca de Produto", font=("Roboto", 16, "bold"))
        self.label_titulo.pack(pady=(20, 10))

        # 2. Input
        self.entrada_codigo = ctk.CTkEntry(self, placeholder_text="Digite o código")
        self.entrada_codigo.pack(fill="x", padx=20, pady=10)
        
        # --- ESSA LINHA FAZ A BUSCA VOLTAR A FUNCIONAR ---
        self.entrada_codigo.bind("<Return>", self.executar_busca)

        # 3. Resultado
        self.label_descricao = ctk.CTkLabel(self, text="Aguardando busca...", wraplength=200)
        self.label_descricao.pack(pady=20)

    def executar_busca(self, event=None):
        codigo = self.entrada_codigo.get().strip()
        if not codigo: 
            return
            
        codigo = codigo.zfill(15)
        self.label_descricao.configure(text="Buscando...", text_color="gray")
        
        # Uso do threading para não travar a UI
        thread = threading.Thread(target=self.thread_busca, args=(codigo,))
        thread.daemon = True
        thread.start()

    def thread_busca(self, codigo):
        sucesso, resultado = self.banco.buscar_produto_por_codigo(codigo)
        # after(0, ...) garante que a atualização ocorra na thread principal do Tkinter
        self.after(0, self.finalizar, sucesso, resultado, codigo)

    def finalizar(self, sucesso, resultado, codigo):
        self.label_descricao.configure(
            text=f"[{codigo}]\n{resultado}" if sucesso else resultado, 
            text_color="white" if sucesso else "#FF5555"
        )
        self.callback_selecao(sucesso, resultado, codigo)

class ColunaGaleria(ctk.CTkFrame):
    def __init__(self, master):
        super().__init__(master)
        self.pack_propagate(False)
        
        self.gestor = GestorImagens()
        self._cache_renderizado = {}

        # --- Carregamento da Imagem Padrão ---
        self.caminho_padrao = "./sem-imagem.jpg"
        self.img_padrao_ctk = self._gerar_imagem_padrao()

        # --- Interface ---
        self.frame_vazio = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vazio.pack(expand=True, fill="both")
        self.label_aviso = ctk.CTkLabel(self.frame_vazio, text="Selecione um item", font=("Roboto", 16, "italic"), text_color="gray")
        self.label_aviso.pack(expand=True)

        self.frame_fotos = ctk.CTkFrame(self, fg_color="transparent")
        self.label_titulo = ctk.CTkLabel(self.frame_fotos, text="Imagens do Produto", font=("Roboto", 16, "bold"))
        self.label_titulo.pack(pady=10)
        self.grid_fotos = ctk.CTkFrame(self.frame_fotos, fg_color="transparent")
        self.grid_fotos.pack(expand=True)

        self.quadrados = []
        for i in range(4):
            # Iniciamos o botão já com a imagem padrão
            btn = ctk.CTkButton(
                self.grid_fotos, 
                text="", 
                image=self.img_padrao_ctk,
                width=150, 
                height=150, 
                corner_radius=10,
                cursor="hand2",
                fg_color="#2b2b2b" # Cor de fundo neutra
            )
            btn.grid(row=i//2, column=i%2, padx=10, pady=10)
            self.quadrados.append(btn)

    def _gerar_imagem_padrao(self):
        """Carrega a imagem de fallback da raiz do projeto"""
        try:
            if os.path.exists(self.caminho_padrao):
                img_pil = Image.open(self.caminho_padrao).convert("RGB")
                return ctk.CTkImage(light_image=img_pil, dark_image=img_pil, size=(120, 120))
        except Exception as e:
            logging.error(f"Erro ao carregar imagem padrão: {e}")
        return None

    def alternar_estado(self, ativo, nome="", codigo=""):
        if ativo:
            self.frame_vazio.pack_forget()
            self.frame_fotos.pack(expand=True, fill="both")
            self.label_titulo.configure(text=f"Imagens: {nome[:25]}...")
            self.carregar_fotos_disco(codigo)
        else:
            self.frame_fotos.pack_forget()
            self.frame_vazio.pack(expand=True, fill="both")

    def carregar_fotos_disco(self, codigo_15):
        caminhos = self.gestor.buscar_fotos_produto(codigo_15)
        self._cache_renderizado.clear()
        self._cache_renderizado[codigo_15] = []

        largura_fixa = 120 # Define a largura que você quer manter fixa

        for i in range(4):
            caminho = caminhos[i]
            
            # Escolhe entre a foto encontrada ou a padrão
            try:
                if caminho:
                    img_pil = Image.open(caminho).convert("RGB")
                else:
                    img_pil = Image.open(self.caminho_padrao).convert("RGB")

                # --- LÓGICA DE PROPORÇÃO (Aspect Ratio) ---
                largura_original, altura_original = img_pil.size
                proporcao = largura_fixa / largura_original
                altura_proporcional = int(altura_original * proporcao)

                img_ctk = ctk.CTkImage(
                    light_image=img_pil,
                    dark_image=img_pil,
                    size=(largura_fixa, altura_proporcional) # Largura fixa, altura calculada
                )
                
                # Cache e Configuração
                self._cache_renderizado[codigo_15].append(img_ctk)
                self._cache_renderizado[codigo_15].append(img_pil)
                
                self.quadrados[i].configure(image=img_ctk, text="")
                self.quadrados[i].image = img_ctk 
                
            except Exception as e:
                logging.error(f"Erro ao processar imagem no índice {i}: {e}")
                self.quadrados[i].configure(image=None, text="Erro")

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