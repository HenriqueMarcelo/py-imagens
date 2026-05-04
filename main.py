# main.py
import sys
from database import BancoDados
from interface import JanelaPrincipal

def main():
    db = BancoDados(dsn="Vem1")
    app = JanelaPrincipal(logica_banco=db)

    # Se passou um código como argumento, dispara a busca após a janela carregar
    if len(sys.argv) > 1:
        codigo = sys.argv[1].strip()
        app.after(100, lambda: app.buscar_codigo_inicial(codigo))

    app.mainloop()

if __name__ == "__main__":
    main()