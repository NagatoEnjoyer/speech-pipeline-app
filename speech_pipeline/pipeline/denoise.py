import noisereduce as nr
import librosa
import soundfile as sf

def denoise(audio_path: str, output_path: str) -> str:
    # Hang beolvasása
    y, sr = librosa.load(audio_path, sr=None)

    # Zajszűrés (noisereduce automatikusan kiszámítja a zajprofilt)
    reduced_noise = nr.reduce_noise(y=y, sr=sr)

    # Mentés
    sf.write(output_path, reduced_noise, sr)
    return output_path