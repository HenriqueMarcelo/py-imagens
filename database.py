import pyodbc

class BancoDados:
    def __init__(self, dsn="Vem1"):
        self.dsn = dsn

    def testar_conexao(self):
        try:
            conn = pyodbc.connect(rf'DSN={self.dsn};')
            conn.close()
            return True, "Conexão estabelecida com sucesso!"
        except Exception as e:
            return False, str(e)

    def obter_produtos_fake(self):
        # Simulação de dados para a interface
        return [{"id": str(i).zfill(3), "nome": f"Produto Exemplo {i}"} for i in range(25)]