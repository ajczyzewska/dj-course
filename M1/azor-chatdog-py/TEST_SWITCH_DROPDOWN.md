# Test funkcji `/switch` z dropdown

## Zaimplementowane funkcjonalności

### 1. **Rozbudowana komenda `/switch`**
- `/switch` - pokazuje interaktywny dropdown z listą sesji
- `/switch <ID>` - bezpośrednie przełączenie (zgodność wstecz)

### 2. **Wsparcie dla tytułów**
- Dropdown wyświetla tytuły sesji (jeśli istnieją)
- Format: `Tytuł (ilość wiadomości, data, ID: krótkie...)`
- Dla sesji bez tytułu: `pełne-ID (ilość wiadomości, data)`

### 3. **Interaktywny wybór**
- Nawigacja: strzałki ↑↓
- Zaznaczenie: SPACE
- Potwierdzenie: ENTER
- Anulowanie: Ctrl+C lub ESC

## Jak przetestować

### Krok 1: Stwórz testowe sesje

```bash
cd /Users/agnieszka/repos/dj/dj-course/M1/azor-chatdog-py
python create_test_sessions.py
```

To utworzy 3 testowe sesje:
1. "Rozmowa o pogodzie" (z tytułem)
2. "Nauka TypeScript" (z tytułem)
3. Sesja bez tytułu (pokazuje ID)

### Krok 2: Uruchom AZØRA

```bash
source .venv/bin/activate
python src/run.py
```

### Krok 3: Przetestuj `/switch`

#### Test 1: Dropdown (BEZ argumentu)
```
TY: /switch
```
Powinien się pojawić **interaktywny dialog** z listą sesji!

#### Test 2: Bezpośrednie przełączenie (Z argumentem)
```
TY: /session list
TY: /switch test-session-weather
```

#### Test 3: Sprawdź help
```
TY: /help
```
Powinno pokazać: `/switch [ID]` z opisem dropdown

### Krok 4: Sprawdź wyświetlanie tytułów

Po przełączeniu sesji z tytułem:
- Komunikat powinien pokazać tytuł zamiast ID
- Przykład: `Przełączono na sesję: Rozmowa o pogodzie`

## Różnice między wersjami

### TypeScript (azor-chatdog-js)
- Używa `inquirer` z `selectFromList()`
- Format dropdown: lista wyboru

### Python (azor-chatdog-py)
- Używa `prompt_toolkit` z `radiolist_dialog()`
- Format dropdown: radio buttons z checkboxami
- Bardziej wizualny interfejs

## Pliki zmodyfikowane

### Python
1. `src/commands/session_switch.py` - NOWY plik z funkcją dropdown
2. `src/command_handler.py` - zaktualizowana obsługa `/switch`
3. `src/cli/console.py` - zaktualizowany help

### TypeScript (już zrobione)
1. `src/commands/sessionSwitch.ts` - NOWY plik z funkcją dropdown
2. `src/commandHandler.ts` - zaktualizowana obsługa `/switch`
3. `src/cli/console.ts` - zaktualizowany help
4. `src/types/index.ts` - dodano pole `title`
5. `src/session/chatSession.ts` - wsparcie dla tytułów
6. `src/files/sessionFiles.ts` - zapis/odczyt tytułów

## Troubleshooting

### Problem: "Brak zapisanych sesji"
Rozwiązanie: Uruchom `python create_test_sessions.py`

### Problem: Import error dla session_switch
Rozwiązanie: Upewnij się, że plik `src/commands/session_switch.py` istnieje

### Problem: Dropdown się nie pojawia
Rozwiązanie: Sprawdź czy `prompt_toolkit` jest zainstalowany:
```bash
pip install prompt_toolkit
```
