@echo off
echo [INFO] Virtualis kornyezet aktivalása...
call .venv\Scripts\activate

echo [INFO] Konyvtarak telepitese...
pip install -r requirements.txt

cd speech_pipeline

echo [INFO] Flask szerver inditasa...
python app.py

pause
