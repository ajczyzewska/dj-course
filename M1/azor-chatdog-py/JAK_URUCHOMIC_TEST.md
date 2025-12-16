# Jak przetestować funkcję "Doprecyzuj pytanie"

## Opcja 1: Uruchom interaktywnie

### Komendy:
```bash
cd /Users/agnieszka/repos/dj/dj-course/M1/azor-chatdog-py
python src/run.py
```

### Co wpisać:
```
> zrób to
```

### Co zobaczysz (oczekiwany output):

```
/Users/agnieszka/Library/Python/3.9/lib/python/site-packages/urllib3/__init__.py:35: NotOpenSSLWarning: urllib3 v2 only supports OpenSSL 1.1.1+, currently the 'ssl' module is compiled with 'LibreSSL 2.8.3'. See: https://github.com/urllib3/urllib3/issues/3020
  warnings.warn(
   ------------.
  ( Woof Woof! )
   ------------'
      \
       \

       ,////,
      /  ' ,)
     (ò____/
    /  ~ \
   |  /   `----.
   | |         |
  /   \        |
 ~   / \
~   |   \
   /     \
  '       '

🤖 Przygotowywanie klienta Gemini...
✅ Klient Gemini gotowy do użycia (Model: gemini-2.0-flash-exp, Key: AIza...Pc0)
ℹ️  Loaded session: xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
ℹ️  Using model: gemini-2.0-flash-exp
ℹ️  Type /help for available commands

>  zrób to

🔧 Wywołanie narzędzia: ask_for_clarification({"question": "Co dokładnie chcesz, żebym zrobił?"})
🤔 AZØR potrzebuje doprecyzowania...

AZOR: Co dokładnie chcesz, żebym zrobił?
>  napisz funkcję sortującą listę
✅ Narzędzie ask_for_clarification wykonane

AZOR: Dobrze! Oto funkcja sortująca listę w Pythonie:

```python
def sortuj_liste(lista):
    """
    Sortuje listę rosnąco.

    Args:
        lista: Lista do posortowania

    Returns:
        Posortowana lista
    """
    return sorted(lista)

# Przykład użycia:
moja_lista = [5, 2, 8, 1, 9]
posortowana = sortuj_liste(moja_lista)
print(posortowana)  # [1, 2, 5, 8, 9]
```

Czy chcesz, żebym dodał więcej opcji (np. sortowanie malejące, sortowanie obiektów)?
```

## Kluczowe momenty do zaobserwowania:

### 1️⃣ **Wywołanie narzędzia** (to chcesz zobaczyć!)
```
🔧 Wywołanie narzędzia: ask_for_clarification({"question": "..."})
```
To pokazuje, że model zdecydował się użyć narzędzia!

### 2️⃣ **Interakcja z użytkownikiem**
```
🤔 AZØR potrzebuje doprecyzowania...

AZOR: Co dokładnie chcesz, żebym zrobił?
>  [tutaj wpisujesz odpowiedź]
```

### 3️⃣ **Potwierdzenie wykonania**
```
✅ Narzędzie ask_for_clarification wykonane
```

### 4️⃣ **Odpowiedź z kontekstem**
Model teraz wie, że chodzi o funkcję sortującą i odpowiada konkretnie.

## Opcja 2: Użyj gotowego skryptu testowego

```bash
cd /Users/agnieszka/repos/dj/dj-course/M1/azor-chatdog-py
./test_clarification.sh
```

## Inne przykłady testowe

### Przykład 1: "pomóż mi"
```
> pomóż mi
```
Oczekiwane: Model zapyta "W czym mogę Ci pomóc?" lub podobnie

### Przykład 2: "jak to zrobić?"
```
> jak to zrobić?
```
Oczekiwane: Model zapyta "Co konkretnie chcesz zrobić?"

### Przykład 3: "napisz kod"
```
> napisz kod
```
Oczekiwane: Model zapyta o szczegóły (język, co ma robić kod)

### Przykład 4: Pytanie JEST jasne (NIE powinien dopytywać)
```
> Napisz funkcję w Pythonie, która oblicza silnię liczby naturalnej n
```
Oczekiwane: Model OD RAZU napisze funkcję, BEZ dopytywania

## Weryfikacja w logach

Jeśli chcesz zobaczyć pełną historię wywołań narzędzi:
```bash
cat ~/.azor/azor-wal.json | tail -20
```

## Troubleshooting

### Problem: Model nie dopytuje, tylko od razu próbuje odpowiedzieć
**Rozwiązanie:**
- Użyj BARDZO ogólnego pytania: "zrób to", "pomóż", "co?"
- Sprawdź czy ENGINE=GEMINI w .env
- Sprawdź czy model to gemini-2.0-flash-exp lub nowszy

### Problem: Błąd "ModuleNotFoundError"
**Rozwiązanie:**
```bash
# Upewnij się że jesteś w odpowiednim katalogu:
cd /Users/agnieszka/repos/dj/dj-course/M1/azor-chatdog-py

# I uruchamiasz z tego katalogu:
python src/run.py
# NIE: python -m src.run
```

### Problem: Brak wywołania narzędzia (nie widzę 🔧)
**Rozwiązanie:**
1. Sprawdź czy ENGINE=GEMINI (w .env)
2. Sprawdź czy masz najnowszą wersję kodu
3. Spróbuj BARDZO ogólnego pytania

## Debug mode - sprawdzenie czy narzędzie jest załadowane

Możesz dodać tymczasowy print w kodzie:

```python
# W pliku src/session/chat_session.py, linia ~74
print(f"DEBUG: Załadowano narzędzia: {[t['name'] for t in all_tools]}")
```

To pokaże przy starcie:
```
DEBUG: Załadowano narzędzia: ['list_sessions', 'get_session', 'delete_sessions', 'ask_for_clarification']
```
