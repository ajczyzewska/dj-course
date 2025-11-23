#!/usr/bin/env python3
"""
EPUB to Audiobook Converter using XTTS v2

Konwertuje plik EPUB na audiobooka z podziałem na rozdziały.
Obsługuje checkpoint do wznowienia po przerwaniu.

Użycie:
    python epub_to_audiobook.py book.epub
    python epub_to_audiobook.py book.epub --speaker voice.wav
    python epub_to_audiobook.py book.epub --resume  # wznowienie
"""

import argparse
import json
import os
import re
import sys
import warnings
from pathlib import Path
from typing import List, Optional

import ebooklib
from bs4 import BeautifulSoup
from ebooklib import epub
from pydub import AudioSegment
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from TTS.api import TTS

warnings.filterwarnings("ignore", category=UserWarning)

console = Console()

# Konfiguracja
CHUNK_SIZE = 400  # Maksymalna liczba znaków na fragment
MIN_CHUNK_SIZE = 50  # Minimalna liczba znaków
OUTPUT_FORMAT = "mp3"  # Format wyjściowy (mp3 lub wav)


def extract_chapters_from_epub(epub_path: str) -> List[dict]:
    """
    Wyciąga rozdziały z pliku EPUB.

    Returns:
        Lista słowników z 'title' i 'content' dla każdego rozdziału.
    """
    book = epub.read_epub(epub_path)
    chapters = []

    for item in book.get_items():
        if item.get_type() == ebooklib.ITEM_DOCUMENT:
            content = item.get_content().decode('utf-8')
            soup = BeautifulSoup(content, 'html.parser')

            # Wyciągnij tytuł rozdziału
            title = None
            for tag in ['h1', 'h2', 'h3', 'title']:
                title_tag = soup.find(tag)
                if title_tag:
                    title = title_tag.get_text().strip()
                    break

            if not title:
                title = item.get_name().replace('.xhtml', '').replace('.html', '')

            # Wyciągnij tekst
            text = soup.get_text(separator=' ')
            text = clean_text(text)

            if len(text) > MIN_CHUNK_SIZE:
                chapters.append({
                    'title': sanitize_filename(title),
                    'content': text
                })

    return chapters


def clean_text(text: str) -> str:
    """Czyści tekst z niepotrzebnych znaków i formatowania."""
    # Usuń wielokrotne spacje i nowe linie
    text = re.sub(r'\s+', ' ', text)
    # Usuń znaki specjalne które mogą przeszkadzać w TTS
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]', '', text)
    # Zamień cudzysłowy na standardowe
    text = text.replace('"', '"').replace('"', '"')
    text = text.replace(''', "'").replace(''', "'")
    return text.strip()


def sanitize_filename(name: str) -> str:
    """Zamienia tytuł na bezpieczną nazwę pliku."""
    # Usuń znaki niedozwolone w nazwach plików
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    # Zamień spacje na podkreślenia
    name = re.sub(r'\s+', '_', name)
    # Ogranicz długość
    return name[:50]


def split_into_chunks(text: str, max_size: int = CHUNK_SIZE) -> List[str]:
    """
    Dzieli tekst na mniejsze fragmenty, starając się dzielić na zdaniach.
    """
    sentences = re.split(r'(?<=[.!?])\s+', text)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_size:
            if current_chunk:
                current_chunk += " " + sentence
            else:
                current_chunk = sentence
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())

            # Jeśli zdanie jest za długie, podziel je
            if len(sentence) > max_size:
                words = sentence.split()
                current_chunk = ""
                for word in words:
                    if len(current_chunk) + len(word) + 1 <= max_size:
                        if current_chunk:
                            current_chunk += " " + word
                        else:
                            current_chunk = word
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = word
            else:
                current_chunk = sentence

    if current_chunk:
        chunks.append(current_chunk.strip())

    return [c for c in chunks if len(c) >= MIN_CHUNK_SIZE]


def load_checkpoint(checkpoint_path: str) -> dict:
    """Wczytuje checkpoint z pliku."""
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r') as f:
            return json.load(f)
    return {'completed_chapters': [], 'current_chapter': 0, 'current_chunk': 0}


def save_checkpoint(checkpoint_path: str, data: dict):
    """Zapisuje checkpoint do pliku."""
    with open(checkpoint_path, 'w') as f:
        json.dump(data, f)


def generate_chapter_audio(
    tts: TTS,
    chapter: dict,
    chapter_idx: int,
    output_dir: str,
    speaker_wav: str,
    checkpoint_path: str,
    checkpoint: dict
) -> Optional[str]:
    """
    Generuje audio dla jednego rozdziału.

    Returns:
        Ścieżka do wygenerowanego pliku audio lub None w przypadku błędu.
    """
    title = chapter['title']
    content = chapter['content']
    chunks = split_into_chunks(content)

    if not chunks:
        return None

    temp_dir = os.path.join(output_dir, 'temp')
    os.makedirs(temp_dir, exist_ok=True)

    audio_segments = []
    start_chunk = 0

    # Sprawdź checkpoint dla tego rozdziału
    if checkpoint['current_chapter'] == chapter_idx:
        start_chunk = checkpoint['current_chunk']

    console.print(f"\n[bold cyan]📖 Rozdział {chapter_idx + 1}: {title}[/bold cyan]")
    console.print(f"   Fragmentów: {len(chunks)}, znaków: {len(content)}")

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(f"Generowanie...", total=len(chunks))
        progress.update(task, completed=start_chunk)

        for i, chunk in enumerate(chunks):
            if i < start_chunk:
                continue

            chunk_file = os.path.join(temp_dir, f"chapter_{chapter_idx:03d}_chunk_{i:04d}.wav")

            try:
                tts.tts_to_file(
                    text=chunk,
                    file_path=chunk_file,
                    speaker_wav=speaker_wav,
                    language="pl"
                )
                audio_segments.append(chunk_file)

                # Aktualizuj checkpoint
                checkpoint['current_chapter'] = chapter_idx
                checkpoint['current_chunk'] = i + 1
                save_checkpoint(checkpoint_path, checkpoint)

            except Exception as e:
                console.print(f"[red]Błąd przy fragmencie {i}: {e}[/red]")
                continue

            progress.update(task, advance=1)

    # Połącz wszystkie fragmenty w jeden plik
    if audio_segments:
        output_file = os.path.join(
            output_dir,
            f"{chapter_idx + 1:02d}_{title}.{OUTPUT_FORMAT}"
        )

        console.print(f"   Łączenie fragmentów...")
        combined = AudioSegment.empty()

        for segment_file in audio_segments:
            if os.path.exists(segment_file):
                segment = AudioSegment.from_wav(segment_file)
                combined += segment
                # Dodaj krótką pauzę między fragmentami
                combined += AudioSegment.silent(duration=300)

        # Eksportuj
        if OUTPUT_FORMAT == "mp3":
            combined.export(output_file, format="mp3", bitrate="192k")
        else:
            combined.export(output_file, format="wav")

        # Wyczyść pliki tymczasowe
        for segment_file in audio_segments:
            if os.path.exists(segment_file):
                os.remove(segment_file)

        console.print(f"   [green]✅ Zapisano: {output_file}[/green]")
        return output_file

    return None


def main():
    parser = argparse.ArgumentParser(
        description="Konwertuje EPUB na audiobooka używając XTTS v2"
    )
    parser.add_argument("epub_file", help="Ścieżka do pliku EPUB")
    parser.add_argument(
        "--speaker",
        default=None,
        help="Plik WAV z próbką głosu (domyślnie: sample-agent.wav)"
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Katalog wyjściowy (domyślnie: nazwa_książki_audio)"
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Wznów od ostatniego checkpointu"
    )
    parser.add_argument(
        "--chunk-size",
        type=int,
        default=CHUNK_SIZE,
        help=f"Maksymalna wielkość fragmentu (domyślnie: {CHUNK_SIZE})"
    )

    args = parser.parse_args()

    # Sprawdź plik EPUB
    if not os.path.exists(args.epub_file):
        console.print(f"[red]Błąd: Plik nie istnieje: {args.epub_file}[/red]")
        sys.exit(1)

    # Ustaw katalog wyjściowy
    if args.output:
        output_dir = args.output
    else:
        book_name = Path(args.epub_file).stem
        output_dir = f"{book_name}_audio"

    os.makedirs(output_dir, exist_ok=True)

    # Ustaw plik głosu
    speaker_wav = args.speaker
    if not speaker_wav:
        # Szukaj domyślnego pliku
        default_speakers = ["sample-agent.wav", "speaker.wav", "voice.wav"]
        script_dir = os.path.dirname(os.path.abspath(__file__))
        for name in default_speakers:
            path = os.path.join(script_dir, name)
            if os.path.exists(path):
                speaker_wav = path
                break

    if not speaker_wav or not os.path.exists(speaker_wav):
        console.print("[red]Błąd: Nie znaleziono pliku głosu. Użyj --speaker[/red]")
        sys.exit(1)

    # Checkpoint
    checkpoint_path = os.path.join(output_dir, ".checkpoint.json")

    if args.resume:
        checkpoint = load_checkpoint(checkpoint_path)
        console.print(f"[yellow]Wznawiam od rozdziału {checkpoint['current_chapter'] + 1}[/yellow]")
    else:
        checkpoint = {'completed_chapters': [], 'current_chapter': 0, 'current_chunk': 0}

    # Wyciągnij rozdziały
    console.print(f"\n[bold yellow]📚 Wczytuję EPUB: {args.epub_file}[/bold yellow]")
    chapters = extract_chapters_from_epub(args.epub_file)

    if not chapters:
        console.print("[red]Błąd: Nie znaleziono rozdziałów w pliku EPUB[/red]")
        sys.exit(1)

    console.print(f"   Znaleziono rozdziałów: {len(chapters)}")

    total_chars = sum(len(ch['content']) for ch in chapters)
    console.print(f"   Łączna liczba znaków: {total_chars:,}")

    # Szacowany czas
    estimated_minutes = (total_chars / CHUNK_SIZE) * 8 / 60  # ~8s per chunk
    console.print(f"   Szacowany czas: ~{estimated_minutes:.0f} minut")

    # Załaduj model TTS
    console.print(f"\n[bold yellow]🤖 Ładowanie modelu TTS...[/bold yellow]")
    try:
        tts = TTS("tts_models/multilingual/multi-dataset/xtts_v2").to("cpu")
        console.print("[green]✅ Model załadowany[/green]")
    except Exception as e:
        console.print(f"[red]Błąd ładowania modelu: {e}[/red]")
        sys.exit(1)

    console.print(f"   Używam głosu: {speaker_wav}")
    console.print(f"   Katalog wyjściowy: {output_dir}")

    # Generuj audio dla każdego rozdziału
    start_chapter = checkpoint['current_chapter']

    for i, chapter in enumerate(chapters):
        if i < start_chapter:
            continue

        if chapter['title'] in checkpoint['completed_chapters']:
            console.print(f"[dim]Pomijam rozdział {i + 1} (już ukończony)[/dim]")
            continue

        result = generate_chapter_audio(
            tts=tts,
            chapter=chapter,
            chapter_idx=i,
            output_dir=output_dir,
            speaker_wav=speaker_wav,
            checkpoint_path=checkpoint_path,
            checkpoint=checkpoint
        )

        if result:
            checkpoint['completed_chapters'].append(chapter['title'])
            checkpoint['current_chapter'] = i + 1
            checkpoint['current_chunk'] = 0
            save_checkpoint(checkpoint_path, checkpoint)

    # Wyczyść temp
    temp_dir = os.path.join(output_dir, 'temp')
    if os.path.exists(temp_dir):
        try:
            os.rmdir(temp_dir)
        except:
            pass

    # Usuń checkpoint po zakończeniu
    if os.path.exists(checkpoint_path):
        os.remove(checkpoint_path)

    console.print(f"\n[bold green]🎉 Zakończono! Pliki audio w: {output_dir}[/bold green]")


if __name__ == "__main__":
    main()
