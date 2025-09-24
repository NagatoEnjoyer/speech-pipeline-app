import logging
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import torch

MODEL_NAME = "facebook/m2m100_1.2B"

# Lazy betöltés a modul indításakor
_tokenizer = None
_model = None

def _load_model():
    global _tokenizer, _model
    if _model is None or _tokenizer is None:
        logging.info("Betöltöm a M2M100 1.2B fordító modellt CPU-ra...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
        _model = AutoModelForSeq2SeqLM.from_pretrained(
            MODEL_NAME,
            device_map={"": "cpu"},
            dtype=torch.float32
        )
        logging.info("Fordító modell betöltve.")

def translate(text: str, src_lang="en", tgt_lang="hu") -> str:

    if not text.strip():
        return "Nincs szöveg a fordításhoz."

    _load_model()

    _tokenizer.src_lang = src_lang
    encoded = _tokenizer(text, return_tensors="pt")
    try:
        generated_tokens = _model.generate(
            **encoded,
            forced_bos_token_id=_tokenizer.get_lang_id(tgt_lang),
            max_length=400
        )
        return _tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
    except Exception as e:
        logging.error(f"Fordítás hiba: {e}")
        return "[Fordítás sikertelen]"
