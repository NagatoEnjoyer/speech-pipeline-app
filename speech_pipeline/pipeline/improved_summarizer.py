# pipeline/summarizer_improved.py
import math
import logging
from typing import List
from transformers import pipeline, AutoTokenizer
from sentence_transformers import SentenceTransformer, util
import nltk

# pont egyszer lefutó letöltés ha kell
try:
    nltk.data.find("tokenizers/punkt")
except LookupError:
    nltk.download("punkt")

# új NLTK-nál kellhet
nltk.download('punkt_tab')
try:
    nltk.data.find("tokenizers/punkt_tab")
except LookupError:
    nltk.download("popular")

# embedding modell (kicsi, gyors, jó)
_EMB_MODEL_NAME = "all-MiniLM-L6-v2"
_emb_model = SentenceTransformer(_EMB_MODEL_NAME)

# abstractive summarizer (opcionális, konfigurálható)
_ABSTR_MODEL_NAME = "facebook/bart-large-cnn"
_abstr_summarizer = None  # lazy init

def _get_abstr_summarizer():
    global _abstr_summarizer
    if _abstr_summarizer is None:
        logging.info("Betöltöm az abstraktív summarizer modellt...")
        _abstr_summarizer = pipeline("summarization", model=_ABSTR_MODEL_NAME)
    return _abstr_summarizer

def _sent_tokenize(text: str) -> List[str]:
    return nltk.tokenize.sent_tokenize(text)

def extract_top_sentences(text: str, max_sentences: int = None) -> List[str]:

    sents = _sent_tokenize(text)
    if not sents:
        return []

    if max_sentences is None:
        n = len(sents)
        max_sentences = max(3, min(30, math.ceil(n / 15)))

    embeddings = _emb_model.encode(sents, convert_to_tensor=True)
    centroid = embeddings.mean(dim=0)
    sims = util.cos_sim(embeddings, centroid).squeeze(1).cpu().tolist()

    idx_scores = list(enumerate(sims))
    idx_scores.sort(key=lambda x: x[1], reverse=True)
    top_idx = sorted([i for i, _ in idx_scores[:max_sentences]])

    selected = [sents[i] for i in top_idx]
    return selected

def improved_summarize(text: str, use_abstractive: bool = True,
                       abstr_max_length: int = 300, abstr_min_length: int = 120) -> str:

    if not text or not text.strip():
        return "Nincs elegendő szöveg az összegzéshez."

    #1 extractive: top mondatok
    extracted_sents = extract_top_sentences(text, max_sentences=None)
    if not extracted_sents:
        return "Nincs összegzésre elegendő tartalom."

    extractive_summary = " ".join(extracted_sents)

    #2 opcionális abstraktív feldolgozás
    if use_abstractive:
        try:
            summarizer = _get_abstr_summarizer()
            # ha túl hosszú a extractive_summary, chunkoljuk token-szinten (simple fallback)
            out = summarizer(extractive_summary, max_length=abstr_max_length, min_length=abstr_min_length, do_sample=False)
            return out[0]["summary_text"]
        except Exception as e:
            logging.error(f"Abstractive summarizer hiba: {e}. Visszaadom az extractive summary-t.")
            return extractive_summary

    return extractive_summary
