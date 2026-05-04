import customtkinter as ctk
import threading
import os
from tkinter import messagebox
from PIL import Image, ImageGrab
import logging
from gestor_imagens import GestorImagens
import webbrowser
import urllib.parse

logging.basicConfig(level=logging.INFO)


class ColunaBusca(ctk.CTkFrame):
    def __init__(self, master, banco, callback_selecao):
        super().__init__(master, width=250)
        self.pack_propagate(False)
        self.banco = banco
        self.callback_selecao = callback_selecao

        self.label_titulo = ctk.CTkLabel(self, text="Busca de Produto", font=("Roboto", 16, "bold"))
        self.label_titulo.pack(pady=(20, 10))

        self.entrada_codigo = ctk.CTkEntry(self, placeholder_text="Digite o código")
        self.entrada_codigo.pack(fill="x", padx=20, pady=10)
        self.entrada_codigo.bind("<Return>", self.executar_busca)

        self.label_descricao = ctk.CTkLabel(self, text="Aguardando busca...", wraplength=200)
        self.label_descricao.pack(pady=20)

    def executar_busca(self, event=None):
        codigo = self.entrada_codigo.get().strip()
        if not codigo:
            return
        codigo = codigo.zfill(15)
        self.label_descricao.configure(text="Buscando...", text_color="gray")
        thread = threading.Thread(target=self.thread_busca, args=(codigo,))
        thread.daemon = True
        thread.start()

    def thread_busca(self, codigo):
        sucesso, resultado = self.banco.buscar_produto_por_codigo(codigo)
        self.after(0, self.finalizar, sucesso, resultado, codigo)

    def finalizar(self, sucesso, resultado, codigo):
        self.label_descricao.configure(
            text=f"[{codigo}]\n{resultado}" if sucesso else resultado,
            text_color="white" if sucesso else "#FF5555"
        )
        self.callback_selecao(sucesso, resultado, codigo)


class ColunaGaleria(ctk.CTkFrame):
    def __init__(self, master, callback_clique_foto):
        super().__init__(master)
        self.pack_propagate(False)
        self.callback_clique_foto = callback_clique_foto

        self.gestor = GestorImagens()
        self._cache_renderizado = {}
        self.caminho_padrao = "./sem-imagem.jpg"
        self.img_padrao_ctk = self._gerar_imagem_padrao()

        self.frame_vazio = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vazio.pack(expand=True, fill="both")
        self.label_aviso = ctk.CTkLabel(self.frame_vazio, text="Selecione um item",
                                        font=("Roboto", 16, "italic"), text_color="gray")
        self.label_aviso.pack(expand=True)

        self.frame_fotos = ctk.CTkFrame(self, fg_color="transparent")
        self.label_titulo = ctk.CTkLabel(self.frame_fotos, text="Imagens do Produto",
                                         font=("Roboto", 16, "bold"))
        self.label_titulo.pack(pady=10)
        self.grid_fotos = ctk.CTkFrame(self.frame_fotos, fg_color="transparent")
        self.grid_fotos.pack(expand=True)

        self.quadrados = []
        for i in range(4):
            btn = ctk.CTkButton(
                self.grid_fotos,
                text="", image=self.img_padrao_ctk,
                width=150, height=150, corner_radius=10,
                cursor="hand2", fg_color="#2b2b2b",
                command=lambda idx=i: self.callback_clique_foto(idx + 1)
            )
            btn.grid(row=i // 2, column=i % 2, padx=10, pady=10)
            self.quadrados.append(btn)

    def _gerar_imagem_padrao(self):
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
        largura_fixa = 120

        for i in range(4):
            caminho = caminhos[i]
            try:
                img_pil = Image.open(caminho).convert("RGB") if caminho else Image.open(self.caminho_padrao).convert("RGB")
                largura_original, altura_original = img_pil.size
                proporcao = largura_fixa / largura_original
                altura_proporcional = int(altura_original * proporcao)
                img_ctk = ctk.CTkImage(light_image=img_pil, dark_image=img_pil,
                                       size=(largura_fixa, altura_proporcional))
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
        self.pack_propagate(False)
        self.callback_teste = callback_teste
        self.descricao_atual = ""
        self.numero_foto_atual = None
        self.codigo_produto_atual = None
        self.imagem_colada = None  # Armazena a PIL Image colada temporariamente

        # --- Estado Inicial ---
        self.frame_vazio = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_vazio.pack(expand=True, fill="both")
        self.label_msg = ctk.CTkLabel(
            self.frame_vazio,
            text="Selecione qual imagem\ndeseja modificar/incluir",
            font=("Roboto", 14, "italic"),
            text_color="gray"
        )
        self.label_msg.pack(expand=True)

        # --- Estado Ativo ---
        self.frame_acoes = ctk.CTkFrame(self, fg_color="transparent")

        self.label_info_foto = ctk.CTkLabel(self.frame_acoes, text="Editando Imagem X",
                                            font=("Roboto", 16, "bold"), text_color="#3b8ed0")
        self.label_info_foto.pack(pady=(20, 10))

        ctk.CTkButton(self.frame_acoes, text="Escolher no computador", cursor="hand2").pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(
            self.frame_acoes,
            text="Buscar no Google",
            cursor="hand2",
            command=self.abrir_google
        ).pack(fill="x", padx=20, pady=5)
        ctk.CTkButton(
            self.frame_acoes,
            text="Colar Imagem",
            cursor="hand2",
            command=self.colar_imagem  # <-- NOVO
        ).pack(fill="x", padx=20, pady=5)

        self.preview = ctk.CTkLabel(
            self.frame_acoes, text="Pré-visualização",
            width=200, height=200, fg_color="#1a1a1a", corner_radius=10
        )
        self.preview.pack(pady=20)

        ctk.CTkButton(
            self.frame_acoes,
            text="Salvar Alteração",
            fg_color="green",
            cursor="hand2",
            command=self.salvar_alteracao  # <-- NOVO
        ).pack(fill="x", padx=20, pady=5)

        ctk.CTkButton(
            self.frame_acoes,
            text="Testar ODBC",
            command=lambda: messagebox.showinfo("Teste ODBC", self.callback_teste()[1]),
            cursor="hand2"
        ).pack(fill="x", padx=20, pady=5)

    def preparar_edicao(self, numero_foto, descricao_produto, codigo_produto=""):
        self.descricao_atual = descricao_produto
        self.numero_foto_atual = numero_foto
        self.codigo_produto_atual = codigo_produto
        self.imagem_colada = None
        self.frame_vazio.pack_forget()
        self.frame_acoes.pack(expand=True, fill="both")
        self.label_info_foto.configure(text=f"Editando Imagem Número {numero_foto}")
        
        # Reseta o preview corretamente
        self.preview.configure(image=ctk.CTkImage(
            light_image=Image.new("RGB", (1, 1)),
            dark_image=Image.new("RGB", (1, 1)),
            size=(1, 1)
        ), text="Pré-visualização")
        self.preview.image = None

    def colar_imagem(self):
        try:
            img = ImageGrab.grabclipboard()
        except Exception as e:
            messagebox.showerror("Erro", f"Não foi possível acessar a área de transferência:\n{e}")
            return

        if img is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem encontrada na área de transferência.")
            return

        if not isinstance(img, Image.Image):
            messagebox.showwarning("Aviso", "O conteúdo da área de transferência não é uma imagem.")
            return

        self.imagem_colada = img.convert("RGB")  # Original preservada

        # Cópia apenas para o preview
        preview_img = self.imagem_colada.copy()
        preview_img.thumbnail((190, 190), Image.LANCZOS)

        img_ctk = ctk.CTkImage(
            light_image=preview_img,
            dark_image=preview_img,
            size=preview_img.size
        )
        self.preview.configure(image=img_ctk, text="")
        self.preview.image = img_ctk

    def salvar_alteracao(self):
        """Salva a imagem colada em disco como .jpg, substituindo versões anteriores."""
        if self.imagem_colada is None:
            messagebox.showwarning("Aviso", "Nenhuma imagem para salvar. Cole uma imagem primeiro.")
            return

        if not self.codigo_produto_atual:
            messagebox.showwarning("Aviso", "Código do produto não identificado.")
            return

        gestor = GestorImagens()
        caminho_fotos = gestor.caminho_fotos
        extensoes = gestor.extensoes

        # Monta o nome base (sufixo vazio para foto 1, _2 para foto 2, etc.)
        sufixo = "" if self.numero_foto_atual == 1 else f"_{self.numero_foto_atual}"
        nome_base = f"{self.codigo_produto_atual}{sufixo}"

        # Remove arquivos existentes em qualquer formato suportado
        for ext in extensoes:
            caminho_existente = os.path.join(caminho_fotos, f"{nome_base}{ext}")
            if os.path.exists(caminho_existente):
                try:
                    os.remove(caminho_existente)
                    logging.info(f"Arquivo anterior removido: {caminho_existente}")
                except Exception as e:
                    messagebox.showerror("Erro", f"Não foi possível remover arquivo anterior:\n{e}")
                    return

        # Salva a nova imagem como .jpg
        caminho_destino = os.path.join(caminho_fotos, f"{nome_base}.jpg")
        try:
            os.makedirs(caminho_fotos, exist_ok=True)
            self.imagem_colada.save(caminho_destino, "JPEG", quality=95)
            messagebox.showinfo("Sucesso", f"Imagem salva em:\n{caminho_destino}")
            logging.info(f"Imagem salva: {caminho_destino}")
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao salvar imagem:\n{e}")

    def abrir_google(self):
        if self.descricao_atual:
            termo_busca = urllib.parse.quote(self.descricao_atual.strip())
            url = f"https://www.google.com/search?&tbm=isch&q={termo_busca}"
            webbrowser.open(url)

    def resetar(self):
        self.frame_acoes.pack_forget()
        self.frame_vazio.pack(expand=True, fill="both")
        self.imagem_colada = None
        self.numero_foto_atual = None
        self.codigo_produto_atual = None