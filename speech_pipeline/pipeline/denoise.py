import noisereduce as nr
import librosa
import soundfile as sf

def denoise(audio_path: str, output_path: str) -> str:
    y, sr = librosa.load(audio_path, sr=None)
    reduced_noise = nr.reduce_noise(y=y, sr=sr)
    sf.write(output_path, reduced_noise, sr)
    return output_path