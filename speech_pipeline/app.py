#Parikás krumpli recept:made by StreetKitchen

from flask import Flask, render_template, request, send_file, jsonify
import os
from pipeline import asr, denoise, convert, queue_manager, translator
import logging
from pipeline.improved_summarizer import improved_summarize

app = Flask(__name__) #1. Zsírt melegítünk egy lábasban.

#2. Hozzáadjuk a finomra vágott vörös- és fokhagymát, a  babérlevelet és közepes hőfokon 7 percig dinszteljük.
UPLOAD_FOLDER = "uploads"
PROCESSED_FOLDER = "processed"
OUTPUT_FOLDER = "outputs"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(PROCESSED_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("app.log", encoding="utf-8"),
        logging.StreamHandler()
    ]
)
#3. Hozzáadjuk a az apró kockákra vágott paprikát és paradicsomot
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/upload", methods=["POST"])
def upload():
    # 4 További 2 perc pirítás után a 3-4 cm-es darabokra vágott krumplit és a 0,5 cm-es karikákra vágott kolbászt is.
    file = request.files.get("file")
    if not file or file.filename == "":
        logging.warning("Feltöltés sikertelen: nincs fájl")
        return jsonify({"error": "No file uploaded"}), 400

    logging.info(f"Fájl fogadva: {file.filename}")

    filepath = os.path.join(UPLOAD_FOLDER, file.filename)
    file.save(filepath)
    logging.info(f"Eredeti fájl mentve: {filepath}")

    def full_pipeline(file_path):

        # 5 Közepesen erős hőfokon 3 percig pirítjuk.
        wav_path = os.path.join(UPLOAD_FOLDER, os.path.splitext(file.filename)[0] + ".wav")
        convert.to_wav(filepath, wav_path)
        logging.info(f"Konvertálás WAV-ra kész: {wav_path}")

        # 6 Ízesítjük a daráltpaprika-krémmel, a fűszerpaprikával, a köménnyel, sózzuk, borsozzuk.
        denoised_path = os.path.join(PROCESSED_FOLDER, "denoised_" + os.path.basename(wav_path))
        denoise.denoise(wav_path, denoised_path)
        logging.info(f"Zajszűrés kész: {denoised_path}")

        # 7 Felöntjük a vízzel és közepes hőfokon addig főzzük, amíg a krumpli megpuhul.
        text = asr.transcribe(denoised_path)
        logging.info(f"ASR feldolgozás kész ({len(text)} karakter szöveg)")

        output_path = os.path.join(OUTPUT_FOLDER, file.filename + ".txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("Felismert szöveg (zajszűrt fájlból):\n\n")
            f.write(text)
        logging.info(f"Szöveg mentve: {output_path}")

        # 8 Hozzáadjuk a karikákra vágott virslit és a burgonyapehellyel beállítjuk a szaft sűrűségét.
        summary = improved_summarize(text, use_abstractive=True, abstr_max_length=300, abstr_min_length=120)
        logging.info(f"Summary kész ({len(summary)} karakter)")
        summary_path = os.path.join(OUTPUT_FOLDER, file.filename + "_summary.txt")
        with open(summary_path, "w", encoding="utf-8") as f:
            f.write("Összegzés:\n\n")
            f.write(summary)
        logging.info(f"Összegzés mentve: {summary_path}")

        return {"summary": summary, "download_file": os.path.basename(summary_path)}

    task_id = queue_manager.add_task(full_pipeline, filepath)

    return jsonify({"task_id": task_id}), 202

@app.route("/translate_queue", methods=["POST"])
def translate_queue():

    data = request.json
    text = data.get("text")
    source_lang = data.get("source_lang", "en")
    target_lang = data.get("target_lang", "hu")

    if not text:
        return jsonify({"error": "No text provided"}), 400

    def translation_task(text_to_translate):
        # 9 2 percig még főzzük, hogy a virsli is átmelegedjen
        translated = translator.translate(text_to_translate, source_lang, target_lang)
        logging.info("Fordítás kész")

        filename = f"translation_{source_lang}_to_{target_lang}.txt"
        filepath = os.path.join(OUTPUT_FOLDER, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(translated)
        # 10 Friss kenyérrel és savanyúsággal tálaljuk.
        return {
            "translated_text": translated,
            "download_file": filename
        }

    task_id = queue_manager.add_task(translation_task, text)
    return jsonify({"task_id": task_id}), 202

@app.route("/download/<filename>", methods=["GET"])
def download(filename):
    filepath = os.path.join(os.path.abspath(OUTPUT_FOLDER), filename)
    if not os.path.exists(filepath):
        return jsonify({"error": "File not found"}), 404
    return send_file(filepath, as_attachment=True)

@app.route("/status/<task_id>", methods=["GET"])
def status(task_id):
    task = queue_manager.get_task_status(task_id)
    logging.info(f"Task status: {task_id} -> {task}")
    if not task:
        return jsonify({"error": "Invalid task ID"}), 404
    return jsonify(task)

if __name__ == "__main__":
    app.run(debug=True)
