import scipy.io.wavfile as wavfile
from transformers import pipeline
import argparse

# Dostępne modele
MODELS = {
    "small": "suno/bark-small",  # ~1.5GB - szybszy, mniej zasobożerny
    "large": "suno/bark",        # ~5GB - lepsza jakość
}

def generate_speech_from_text(text_to_speak, output_filename="example-output.wav", model_size="small"):
    """
    Generuje mowę na podstawie tekstu i zapisuje ją do pliku WAV.
    Używa potoku 'text-to-speech' z modelu suno/bark.

    :param text_to_speak: Tekst do syntezy.
    :param output_filename: Nazwa pliku wyjściowego (domyślnie .wav).
    :param model_size: Rozmiar modelu ('small' lub 'large').
    """
    try:
        model_name = MODELS.get(model_size, MODELS["small"])
        print(f"Ładowanie modelu Text-to-Speech ({model_name})...")
        synthesizer = pipeline("text-to-speech", model_name)
        print("Model załadowany.")

        print(f"Syntetyzowanie mowy dla tekstu: '{text_to_speak[:50]}...'")
        speech = synthesizer(text_to_speak)

        sampling_rate = speech["sampling_rate"]
        audio_data = speech["audio"][0]

        wavfile.write(output_filename, rate=sampling_rate, data=audio_data)
        print(f"\n✅ Sukces! Plik audio zapisany jako: {output_filename}")

    except ImportError as e:
        print(f"\nBłąd importu: {e}")
        print("Upewnij się, że zainstalowałeś wszystkie biblioteki z requirements.txt (np. pip install -r requirements.txt).")
    except Exception as e:
        print(f"\nWystąpił błąd: {e}")

def clear_output_files():
    import glob
    import os
    for filename in glob.glob("output*"):
        try:
            os.remove(filename)
            print(f"Usunięto plik: {filename}")
        except Exception as e:
            print(f"Nie udało się usunąć pliku {filename}: {e}")

texts = [
    "Anielka idź uczyć się angielskiego a Panda idzie spać",
    "[angry] Tata uspokój sie "
]
# zerknij na plik texts.py

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Text-to-Speech z modelem Bark")
    parser.add_argument("--model", choices=["small", "large"], default="small",
                        help="Rozmiar modelu: 'small' (~1.5GB) lub 'large' (~5GB)")
    args = parser.parse_args()

    clear_output_files()
    for i, text in enumerate(texts):
        output_filename = f"output_{i+1}.wav"
        generate_speech_from_text(text, output_filename, model_size=args.model)
