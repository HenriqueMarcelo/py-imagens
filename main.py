from database import BancoDados
from interface import JanelaPrincipal
import customtkinter as ctk

def main():
    # 1. Inicia a lógica
    db = BancoDados(dsn="Vem1")
    
    # 2. Inicia a interface e passa o DB para ela
    app = JanelaPrincipal(logica_banco=db)
    
    # 3. Loop principal
    app.mainloop()

if __name__ == "__main__":
    main()