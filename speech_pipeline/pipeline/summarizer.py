
import logging
import torch
from transformers import pipeline, AutoTokenizer

MODEL = "sshleifer/distilbart-cnn-12-6"
_summarizer = None
_tokenizer = None
_DEVICE = 0 if torch.cuda.is_available() else -1

def _init_models():
    global _summarizer, _tokenizer
    if _summarizer is None or _tokenizer is None:
        logging.info("Inicializálom a summarizer modellt és tokenizert...")
        _tokenizer = AutoTokenizer.from_pretrained(MODEL)
        _summarizer = pipeline("summarization", model=MODEL, tokenizer=_tokenizer, device=_DEVICE)
    return _tokenizer, _summarizer

def _determine_safe_chunk_size(default=800, reserve=50):

    tokenizer, _ = _init_models()
    max_len = tokenizer.model_max_length
    if max_len is None or max_len > 1000000:
        max_len = 1024
    safe = min(default, max_len - reserve)
    if safe <= 0:
        safe = 512
    return safe

def chunk_by_tokens(text: str, chunk_size: int = None, overlap: int = 50):

    tokenizer, _ = _init_models()
    if chunk_size is None:
        chunk_size = _determine_safe_chunk_size()
    tokens = tokenizer.encode(text, add_special_tokens=False)
    if len(tokens) == 0:
        return []

    chunks = []
    i = 0
    step = max(chunk_size - overlap, 1)
    while i < len(tokens):
        ids = tokens[i: i + chunk_size]
        chunk_text = tokenizer.decode(ids, skip_special_tokens=True, clean_up_tokenization_spaces=True)
        chunks.append(chunk_text)
        i += step
    return chunks

def summarize_long_text(text: str, chunk_size: int = None, overlap: int = 50) -> str:

    if not text or not text.strip():
        return "Nincs elegendő szöveg az összegzéshez."

    tokenizer, summarizer = _init_models()
    if chunk_size is None:
        chunk_size = _determine_safe_chunk_size()

    chunks = chunk_by_tokens(text, chunk_size=chunk_size, overlap=overlap)
    logging.info(f"Összefoglalás: {len(chunks)} chunk elkészítve (chunk_size={chunk_size}, overlap={overlap}).")

    summaries = []
    for idx, chunk in enumerate(chunks, start=1):
        if not chunk.strip():
            continue
        try:
            out = summarizer(chunk, max_length=300, min_length=100, do_sample=False)
            s = out[0]["summary_text"]
            summaries.append(s)
            logging.info(f"Chunk {idx}/{len(chunks)} összegzése kész.")
        except Exception as e:
            logging.error(f"Hiba a chunk {idx} összegzése közben: {e}")
            continue

    if not summaries:
        return "Összegzés nem állítható elő (töredékes vagy üres input)."

    combined = " ".join(summaries)
    if len(summaries) > 1:
        try:
            final = summarizer(combined, max_length=150, min_length=50, do_sample=False)[0]["summary_text"]
            return final
        except Exception as e:
            logging.error(f"Hiba a végső összegzés készítésekor: {e}")
            return combined

    return summaries[0]
