```
python -m pip install customtkinter pyodbc openpyxl Pillow
python -m pip install pyinstaller

pyinstaller --onefile --noconsole --name "GerenciadorFotos" --add-data "sem-imagem.jpg;." --icon "icone_projeto.ico" main.py
```