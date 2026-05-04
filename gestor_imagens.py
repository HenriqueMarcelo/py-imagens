import os

class GestorImagens:
    def __init__(self):
        self.caminho_fotos = r"C:\MGMobile\Vemovel\fotos"
        self.extensoes = [".gif", ".jpg", ".jpeg", ".png"]

    def buscar_fotos_produto(self, codigo_15):
        """
        Retorna apenas uma lista com os caminhos (strings) das 4 fotos.
        Se não encontrar, a posição será None.
        """
        caminhos_encontrados = [None, None, None, None]

        for i in range(4):
            sufixo = "" if i == 0 else f"_{i + 1}"
            
            for ext in self.extensoes:
                nome_arquivo = f"{codigo_15}{sufixo}{ext}"
                caminho_completo = os.path.join(self.caminho_fotos, nome_arquivo)

                if os.path.exists(caminho_completo):
                    caminhos_encontrados[i] = caminho_completo
                    break # Pula para o próximo índice (foto_2, etc)
                    
        return caminhos_encontrados