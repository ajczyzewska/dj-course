# EPUB to Audiobook Converter

Konwertuje pliki EPUB na audiobooki używając modelu XTTS v2.

## Wymagania

```bash
# Zainstaluj ffmpeg (do konwersji na MP3)
brew install ffmpeg

# Zależności Python (już zainstalowane)
pip3 install ebooklib beautifulsoup4 pydub
```

## Użycie

### Podstawowe

```bash
cd /Users/agnieszka/repos/dj/dj-course/M2/text-to-speach-xtts

# Konwertuj EPUB (użyje sample-agent.wav jako głos)
python3 epub_to_audiobook.py /sciezka/do/ksiazka.epub
```

### Z własnym głosem

```bash
python3 epub_to_audiobook.py ksiazka.epub --speaker moj_glos.wav
```

Plik głosu powinien być:
- Format: WAV
- Długość: 5-15 sekund
- Jakość: wyraźna mowa bez szumów

### Wznowienie po przerwaniu

```bash
# Przerwij w dowolnym momencie (Ctrl+C)
# Wznów później:
python3 epub_to_audiobook.py ksiazka.epub --resume
```

### Wszystkie opcje

```bash
python3 epub_to_audiobook.py ksiazka.epub \
    --speaker glos.wav \
    --output moj_katalog \
    --chunk-size 500
```

| Opcja | Opis | Domyślnie |
|-------|------|-----------|
| `--speaker` | Plik WAV z próbką głosu | sample-agent.wav |
| `--output` | Katalog wyjściowy | nazwa_ksiazki_audio |
| `--resume` | Wznów od checkpointu | - |
| `--chunk-size` | Max znaków na fragment | 400 |

## Output

```
ksiazka_audio/
├── 01_Wstep.mp3
├── 02_Rozdzial_1.mp3
├── 03_Rozdzial_2.mp3
├── 04_Rozdzial_3.mp3
└── ...
```

## Szacowany czas

| Rozmiar książki | Znaki | Czas generowania |
|-----------------|-------|------------------|
| Krótka (100 stron) | ~40,000 | ~1-2 godziny |
| Średnia (200 stron) | ~80,000 | ~3-4 godziny |
| Długa (300+ stron) | ~120,000+ | ~5-8 godzin |

*Czasy dla MacBook Air M1. Na starszym sprzęcie może być dłużej.*

## Wskazówki

### Jakość audio

- **Chunk size 300-400** - optymalna jakość dla polskiego
- **Chunk size 500+** - szybciej, ale mogą być błędy w wymowie

### Pamięć

Model XTTS zajmuje ~2GB RAM. Zamknij niepotrzebne aplikacje.

### Uruchomienie na noc

```bash
# Uruchom w tle i zapisz logi
nohup python3 epub_to_audiobook.py ksiazka.epub > audiobook.log 2>&1 &

# Sprawdź postęp
tail -f audiobook.log
```

### Problemy

**"Nie znaleziono pliku głosu"**
- Upewnij się że `sample-agent.wav` jest w tym samym katalogu
- Lub użyj `--speaker /pelna/sciezka/do/glosu.wav`

**"Błąd przy fragmencie X"**
- Niektóre fragmenty mogą się nie powieść (za długie/dziwne znaki)
- Skrypt kontynuuje z następnymi

**Brak dźwięku w MP3**
- Sprawdź czy masz zainstalowany ffmpeg: `ffmpeg -version`
