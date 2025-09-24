import ffmpeg
import os

def to_wav(input_path: str, output_path: str) -> str:

    try:
        (
            ffmpeg
            .input(input_path)
            .output(output_path, format="wav", acodec="pcm_s16le", ac=1, ar="16k")
            .overwrite_output()
            .run(quiet=True)
        )
        return output_path
    except Exception as e:
        raise RuntimeError(f"Hiba a WAV konverziónál: {e}")