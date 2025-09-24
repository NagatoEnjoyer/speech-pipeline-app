@echo off
echo [INFO] Virtuális környezet aktiválása...
call .venv\Scripts\activate

echo [INFO] Könyvtárak telepítése...
pip install -r requirements.txt

echo [INFO] Flask szerver indítása...
python app.py

pause
