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

    def buscar_produto_por_codigo(self, codigo):
        try:
            conn = pyodbc.connect(rf'DSN={self.dsn};')
            cursor = conn.cursor()
            # Usar parameterized query é mais seguro e performático
            cursor.execute("SELECT Descricao FROM Produtos WHERE Codigo = ?", (codigo,))
            row = cursor.fetchone()
            
            cursor.close()
            conn.close()

            if row:
                return True, str(row.Descricao)
            else:
                return False, "Nenhum produto encontrado."
        except Exception as e:
            return False, f"Erro no banco: {str(e)}"