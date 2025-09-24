# Speech Recognition & Processing Web App

Ez a projekt egy **webes alkalmazás**, amely képes:
- Hangfájlok zajszűrésére
- Beszédfelismerésre (ASR)
- Automatikus szövegösszegzésre
- Fordításra több nyelv között
- Az eredmények letöltésére

A feldolgozás lépései **sorban, automatikusan** történnek, a felhasználó közben státuszjelzést és folyamatjelző spinnert lát.

---

## Követelmények

- **Python 3.9+**
- FFmpeg telepítve és elérhető a PATH-ban
- Virtuális környezet ajánlott

---

## Telepítés Windows rendszeren

1. Klónozd vagy másold le a projektet egy mappába.  
2. Nyisd meg a start.bat fájlt (Ez telepít minden szükséges csomagot)
3. Ezután a böngészőben nyisd meg: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Használat 

1. Fájl feltöltése

    - Tölts fel egy hangfájlt (.mp3, .wav, stb.).

    - A rendszer automatikusan:
    
        - WAV formátumba konvertálja,
        
        - zajszűrést végez,
        
        - felismeri a szöveget,
        
        - összegzést készít.

2. Eredmények megjelenítése

    - A felismert szöveg és az összegzés letölthető.
    
    - Az összegzés a böngészőben is megjelenik.

3. Fordítás

    - Válaszd ki a forrás- és célnyelvet.
    
    - A fordítás közben spinner jelzi a feldolgozást.
    
    - Az eredményt szintén le lehet tölteni TXT formátumban.

## Külső elemek

A projekt a következő külső könyvtárakat és modelleket használja:

- **Flask** – webes felület létrehozásához
- **openai-whisper** – automatikus beszédfelismeréshez
- **torch** – modellek futtatásához
- **noisereduce** – zajszűréshez
- **librosa** – hangfájl feldolgozáshoz
- **soundfile** – WAV fájlok olvasása/írása
- **nltk** – mondatok tokenizálásához
- **transformers** – summarizer és fordító modellekhez
- **sentence-transformers** – extractive summarizer embeddingekhez
- **accelerate** – nagyobb modellek CPU/GPU kezeléséhez

## Ismert korlátok

A nagyobb modellek CPU-n lassabbak.

GPU esetén a feldolgozás jelentősen gyorsul.



Internetkapcsolat szükséges a modellek első letöltéséhez.
