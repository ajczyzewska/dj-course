"""
Komenda /audio - generuje plik audio z ostatniej odpowiedzi asystenta.
Używa modelu XTTS v2 do syntezy mowy.
"""

import os
import warnings
from typing import List, Dict
from cli import console

# Suppress TTS warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Lazy loading TTS to avoid slow imports
_tts_instance = None

def get_tts():
    """Lazy load TTS model."""
    global _tts_instance
    if _tts_instance is None:
        try:
            from TTS.api import TTS
            console.print_info("Ładowanie modelu TTS (może potrwać chwilę)...")
            _tts_instance = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
            console.print_info("Model TTS załadowany.")
        except ImportError:
            console.print_error("Błąd: Biblioteka TTS nie jest zainstalowana.")
            console.print_info("Zainstaluj: pip install coqui-tts")
            return None
        except Exception as e:
            console.print_error(f"Błąd ładowania modelu TTS: {e}")
            return None
    return _tts_instance


def get_last_assistant_response(history: List[Dict]) -> str:
    """
    Wyciąga ostatnią odpowiedź asystenta z historii.

    Args:
        history: Lista wiadomości w formacie {"role": "user|model", "parts": [{"text": "..."}]}

    Returns:
        Tekst ostatniej odpowiedzi asystenta lub pusty string.
    """
    # Przejdź od końca szukając ostatniej odpowiedzi modelu
    for message in reversed(history):
        role = message.get("role", "")
        if role == "model":
            if 'parts' in message and message['parts']:
                return message['parts'][0].get('text', '')
    return ""


def export_last_response_to_audio(
    history: List[Dict],
    session_id: str,
    assistant_name: str,
    speaker_wav: str = None
):
    """
    Generuje plik audio z ostatniej odpowiedzi asystenta.

    Args:
        history: Lista wiadomości sesji.
        session_id: ID sesji.
        assistant_name: Nazwa asystenta.
        speaker_wav: Opcjonalna ścieżka do pliku z próbką głosu.
    """
    if not history:
        console.print_info("Historia sesji jest pusta. Nie można wygenerować audio.")
        return

    # Pobierz ostatnią odpowiedź
    last_response = get_last_assistant_response(history)

    if not last_response:
        console.print_info("Brak odpowiedzi asystenta w historii.")
        return

    # Ogranicz długość tekstu (XTTS działa lepiej z krótszymi fragmentami)
    max_chars = 1000
    if len(last_response) > max_chars:
        console.print_info(f"Tekst jest długi ({len(last_response)} znaków). Generuję tylko pierwsze {max_chars} znaków.")
        last_response = last_response[:max_chars] + "..."

    # Znajdź plik głosu
    if not speaker_wav:
        # Szukaj w różnych lokalizacjach
        possible_paths = [
            "speaker.wav",
            "sample-agent.wav",
            os.path.join(os.path.dirname(__file__), "..", "..", "speaker.wav"),
            os.path.expanduser("~/speaker.wav"),
        ]
        for path in possible_paths:
            if os.path.exists(path):
                speaker_wav = path
                break

    if not speaker_wav or not os.path.exists(speaker_wav):
        console.print_error("Błąd: Nie znaleziono pliku głosu (speaker.wav).")
        console.print_info("Umieść plik speaker.wav w katalogu projektu lub użyj zmiennej SPEAKER_WAV.")
        return

    # Załaduj TTS
    tts = get_tts()
    if not tts:
        return

    # Generuj audio
    output_filename = f"{session_id}_audio.wav"

    console.print_info(f"Generowanie audio dla odpowiedzi {assistant_name}...")
    console.print_info(f"Tekst: \"{last_response[:100]}{'...' if len(last_response) > 100 else ''}\"")

    try:
        tts.tts_to_file(
            text=last_response,
            file_path=output_filename,
            speaker_wav=speaker_wav,
            language="pl"
        )
        console.print_info(f"✅ Audio zapisane jako: {output_filename}")

    except Exception as e:
        console.print_error(f"Błąd generowania audio: {e}")
