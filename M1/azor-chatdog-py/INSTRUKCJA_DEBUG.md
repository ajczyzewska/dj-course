# 🔍 Instrukcja debugowania - Sprawdzenie tool call

## Krok 1: Uruchom AZØRA z debugowaniem

```bash
cd /Users/agnieszka/repos/dj/dj-course/M1/azor-chatdog-py
python src/run.py
```

## Krok 2: Co zobaczysz przy starcie

```
🤖 Przygotowywanie klienta Gemini...
✅ Klient Gemini gotowy do użycia (Model: gemini-2.0-flash-exp, Key: AIza...Pc0)
🔧 Załadowano narzędzia: list_sessions, get_session, delete_sessions, ask_for_clarification
                                                                        ^^^^^^^^^^^^^^^^^^^^^^^^
                                                                        ✅ NARZĘDZIE ZAŁADOWANE!
```

## Krok 3: Wpisz testowe pytanie

```
> zrób to
```

## Krok 4: Co POWINIENEŚ zobaczyć (z DEBUG logami)

```
> zrób to

🔍 DEBUG: Otrzymano odpowiedź z 1 kandydatami
🔍 DEBUG: Liczba parts w odpowiedzi: 1
🔍 DEBUG: Part 0: has function_call=True, has text=False
                  ^^^^^^^^^^^^^^^^^^^^
                  ✅ FUNCTION CALL WYKRYTY!

🎯 DEBUG: ZNALEZIONO FUNCTION CALL!
🔧 Wywołanie narzędzia: ask_for_clarification({"question": "Co dokładnie chcesz, żebym zrobił?"})
🤔 AZØR potrzebuje doprecyzowania...

AZOR: Co dokładnie chcesz, żebym zrobił?
>
```

## Co oznaczają logi DEBUG:

### ✅ DOBRE znaki (function call działa):
```
🔍 DEBUG: Part 0: has function_call=True, has text=False
🎯 DEBUG: ZNALEZIONO FUNCTION CALL!
🔧 Wywołanie narzędzia: ask_for_clarification(...)
```

### ❌ ZŁE znaki (function call NIE działa):
```
🔍 DEBUG: Part 0: has function_call=False, has text=True
```
To znaczy że model zwrócił tekst zamiast function call.

## Krok 5: Inne pytania testowe

Spróbuj kolejnych:

```
> pomóż mi
> napisz kod
> co?
```

## Troubleshooting

### Jeśli widzisz `has_function_call=False`:

Model nie wywołał narzędzia. Możliwe przyczyny:

1. **Model jest zbyt pomocny** - próbuje odgadnąć intencje zamiast dopytać
2. **System prompt nie jest wystarczająco jasny**
3. **Model nie rozpoznaje sytuacji jako wymagającej doprecyzowania**

### Rozwiązanie: Jeszcze prostsze pytanie

Spróbuj EKSTREMALNIE niejasnego pytania:
```
> co?
> huh?
> ???
```

### Jeśli nadal nie działa:

Sprawdź czy API key jest poprawny:
```bash
cat .env | grep GEMINI_API_KEY
```

Sprawdź model (musi wspierać function calling):
```bash
cat .env | grep MODEL_NAME
```

## Usuwanie DEBUG logów

Jeśli chcesz usunąć szczegółowe logi DEBUG, edytuj:
`src/llm/gemini_client.py` - usuń linijki z `console.print_info` zawierające "DEBUG"
