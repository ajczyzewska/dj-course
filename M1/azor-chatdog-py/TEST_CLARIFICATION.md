# Test funkcji "Doprecyzuj pytanie"

## Jak przetestować

1. Uruchom AZØRA:
```bash
cd M1/azor-chatdog-py
python src/run.py
```

2. Zadaj niejasne pytanie, np:
```
> zrób to
```

3. Oczekiwane zachowanie:
- Model powinien rozpoznać, że pytanie jest niejasne
- Wywoła narzędzie `ask_for_clarification`
- Zobaczysz:
  ```
  🤔 AZØR potrzebuje doprecyzowania...

  AZOR: Co dokładnie chcesz, żebym zrobił?
  ```

4. Odpowiedz z większą liczbą szczegółów:
```
> Napisz funkcję sortującą listę
```

5. Model powinien teraz odpowiedzieć z pełnym kontekstem

## Przykładowe scenariusze testowe

### Test 1: Bardzo ogólne polecenie
```
> pomóż mi
```
Oczekiwana reakcja: Model poprosi o doprecyzowanie, w czym ma pomóc

### Test 2: Brak kontekstu
```
> jak to zrobić?
```
Oczekiwana reakcja: Model zapyta, co konkretnie chcesz zrobić

### Test 3: Niejednoznaczność
```
> napisz kod
```
Oczekiwana reakcja: Model zapyta, jaki kod (w jakim języku, co ma robić)

### Test 4: Pytanie jest jasne (nie powinien dopytywać)
```
> Napisz funkcję w Pythonie, która sortuje listę liczb rosnąco
```
Oczekiwana reakcja: Model odpowie bez dopytywania

## Weryfikacja działania narzędzia

Podczas wykonywania narzędzia zobaczysz w konsoli:
```
🔧 Wywołanie narzędzia: ask_for_clarification({"question": "..."})
✅ Narzędzie ask_for_clarification wykonane
```

## Troubleshooting

### Jeśli model nie dopytuje:
1. Sprawdź czy używasz Gemini (ENGINE=GEMINI w .env)
2. Sprawdź czy system prompt został zaktualizowany
3. Spróbuj bardziej ogólnego pytania

### Jeśli pojawia się błąd importu:
```bash
# Sprawdź czy jesteś w odpowiednim katalogu
pwd
# Powinno być: .../M1/azor-chatdog-py

# Uruchom z katalogu głównego projektu:
python src/run.py
```

## Debug mode

Jeśli chcesz zobaczyć szczegóły wywołania:
- Sprawdź logi w `~/.azor/azor-wal.json`
- Każde wywołanie narzędzia jest logowane

## Uwaga o API Gemini

Funkcja działa tylko z Gemini API, które wspiera function calling.
Jeśli używasz lokalnego LLaMA, narzędzie nie będzie działać (brak wsparcia dla tools).
