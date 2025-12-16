# Funkcja "Doprecyzuj pytanie" w AZØRZE

## Opis

Zaimplementowano funkcjonalność pozwalającą modelowi na interaktywne dopytywanie użytkownika, gdy pytanie jest niewystarczająco precyzyjne. Model może teraz używać narzędzia `ask_for_clarification` do uzyskania dodatkowych informacji.

## Implementacja

### Python (`azor-chatdog-py`)

**Lokalizacja plików:**
- `M1/azor-chatdog-py/src/tools/clarification_tool.py` - definicja narzędzia
- `M1/azor-chatdog-py/src/session/chat_session.py` - integracja z sesją czatu
- `M1/azor-chatdog-py/src/assistant/azor.py` - zaktualizowany system prompt

**Kluczowe komponenty:**
```python
def ask_for_clarification(question: str) -> str:
    """
    Pyta użytkownika o doprecyzowanie, gdy pytanie jest niejasne.

    Args:
        question: Pytanie doprecyzowujące od modelu

    Returns:
        Odpowiedź użytkownika
    """
```

### TypeScript (`azor-chatdog-js`)

**Lokalizacja plików:**
- `M1/azor-chatdog-js/src/tools/clarificationTool.ts` - definicja narzędzia
- `M1/azor-chatdog-js/src/llm/geminiClient.ts` - rozszerzone o function calling
- `M1/azor-chatdog-js/src/session/chatSession.ts` - integracja z sesją czatu
- `M1/azor-chatdog-js/src/assistant/azor.ts` - zaktualizowany system prompt
- `M1/azor-chatdog-js/src/types/index.ts` - nowe typy dla tools

**Kluczowe komponenty:**
```typescript
export async function askForClarification(question: string): Promise<string> {
  // Wyświetla pytanie użytkownikowi
  // Pobiera odpowiedź
  // Zwraca ją do modelu
}
```

## Jak działa?

1. **Użytkownik zadaje niejasne pytanie**, np.:
   - "zrób to"
   - "napraw błąd"
   - "pomóż mi"

2. **Model rozpoznaje niejednoznaczność** i wywołuje narzędzie `ask_for_clarification`

3. **System wyświetla pytanie doprecyzowujące**, np.:
   ```
   🤔 AZØR potrzebuje doprecyzowania...

   AZOR: Co dokładnie chcesz, żebym zrobił?
   ```

4. **Użytkownik odpowiada** z większą ilością szczegółów

5. **Model kontynuuje** z pełnym kontekstem

## Przykładowe scenariusze użycia

### Scenariusz 1: Niejasne polecenie
```
Użytkownik: zrób to
AZØR: 🤔 Doprecyzowanie...
      Co dokładnie mam zrobić?
Użytkownik: Napisz funkcję sortującą listę liczb
AZØR: Jasne! Oto funkcja sortująca...
```

### Scenariusz 2: Brak kontekstu
```
Użytkownik: jak to zrobić?
AZØR: 🤔 Doprecyzowanie...
      Co konkretnie chcesz zrobić?
Użytkownik: Chcę połączyć się z bazą danych PostgreSQL
AZØR: Aby połączyć się z PostgreSQL...
```

### Scenariusz 3: Wiele możliwości
```
Użytkownik: napisz API endpoint
AZØR: 🤔 Doprecyzowanie...
      Jaki endpoint mam utworzyć? (GET/POST/PUT/DELETE)?
      Jakie dane ma obsługiwać?
Użytkownik: POST endpoint do tworzenia użytkowników
AZØR: Oto endpoint POST /users...
```

## Konfiguracja system prompt

Model został poinstruowany, aby używać clarification w odpowiednich sytuacjach:

```
WAŻNE: Jeśli pytanie użytkownika jest niejasne, niejednoznaczne
lub brakuje Ci informacji do udzielenia odpowiedzi - użyj narzędzia
'ask_for_clarification', aby doprecyzować pytanie.
Nie zgaduj intencji użytkownika - dopytaj!

Przykłady sytuacji gdy powinieneś użyć ask_for_clarification:
- Pytanie jest zbyt ogólne ("zrób to", "napraw błąd", "pomóż mi")
- Brakuje kontekstu ("jak to zrobić?" - co konkretnie?)
- Jest wiele możliwych interpretacji
- Nie wiesz, jakiego szczegółu dotyczy pytanie

Nie przesadzaj - jeśli pytanie jest jasne, odpowiedz normalnie.
```

## Testowanie

### Test Python
```bash
cd M1/azor-chatdog-py
python -m src.run

# W sesji czatu:
> zrób to
# Model powinien zapytać o doprecyzowanie
```

### Test TypeScript
```bash
cd M1/azor-chatdog-js
npm start

# W sesji czatu:
> zrób to
# Model powinien zapytać o doprecyzowanie
```

## Uwagi techniczne

### Wsparcie dla różnych klientów LLM

- **Gemini API** - pełne wsparcie dla function calling ✅
- **LLaMA (local)** - obecnie bez wsparcia dla tools ⚠️

### Flow wywołania narzędzia

1. Użytkownik → `sendMessage(text)` → LLM
2. LLM decyduje o wywołaniu tool → `functionCall: ask_for_clarification`
3. System → `askForClarification(question)` → wyświetla pytanie
4. Użytkownik → podaje odpowiedź
5. System → zwraca odpowiedź do LLM jako `functionResponse`
6. LLM → generuje finalną odpowiedź z pełnym kontekstem
7. System → wyświetla odpowiedź użytkownikowi

### Obsługa błędów

- Jeśli użytkownik nie poda odpowiedzi (pusty input) → zwraca "Użytkownik nie podał odpowiedzi"
- Jeśli wystąpi błąd podczas wykonania narzędzia → błąd jest przekazywany do modelu
- Model otrzymuje informację o błędzie i może się dostosować

## Rozszerzenia (możliwe kierunki rozwoju)

1. **Multi-step clarification** - model może zadawać wiele pytań doprecyzowujących
2. **Structured clarification** - predefiniowane szablony pytań
3. **Context retention** - zapamiętywanie wcześniejszych doprecyzowań w sesji
4. **Proactive clarification** - model przewiduje potrzebę doprecyzowania przed rozpoczęciem zadania
5. **Clarification history** - zapisywanie historii doprecyzowań w sesji

## Zgodność z M1/Z11

Ta implementacja realizuje projekt z zadania M1/Z11, gdzie zaprojektowano rozwiązanie pozwalające modelowi na interaktywne doprecyzowanie pytań użytkownika.

**Kluczowe założenia z projektu:**
✅ Model sam decyduje, kiedy potrzebuje doprecyzowania
✅ Wykorzystanie function calling / tool use
✅ Interaktywny flow: pytanie → doprecyzowanie → odpowiedź
✅ Wsparcie dla różnych klientów LLM (z odpowiednimi ograniczeniami)
