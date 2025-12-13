# Tool: ask_for_clarification

## 📋 Zadanie (M3/Z8)

Implementacja narzędzia pozwalającego agentowi AI **dopytać użytkownika** gdy pytanie jest niejasne lub zbyt ogólne.

## ✅ Co zostało zaimplementowane

### Nowy tool: `ask_for_clarification`

**Funkcjonalność:**
- Agent AI może wykryć, że pytanie użytkownika jest niedokładne
- Wywołuje tool z pytaniem doprecyzowującym
- Tool wyświetla pytanie użytkownikowi
- Czeka na odpowiedź (input przez stdin)
- Zwraca odpowiedź do agenta AI
- Agent kontynuuje z pełniejszą informacją

**Parametry:**
```json
{
  "question": "Pytanie doprecyzowujące dla użytkownika (required)",
  "context": "Opcjonalny kontekst - dlaczego agent potrzebuje doprecyzowania (optional)"
}
```

## 🔧 Implementacja techniczna

### 1. Komunikacja przez STDIO

```python
# Print to stderr (nie koliduje z protokołem MCP na stdout)
print(clarification_text, file=sys.stderr)
print("\n💬 Twoja odpowiedź: ", file=sys.stderr, end='', flush=True)

# Read from stdin
user_response = input().strip()
```

**Dlaczego stderr?**
- MCP protokół używa stdout do komunikacji JSON między agentem a serwerem
- Wyświetlanie tekstu użytkownikowi na stdout mogłoby zepsuć protokół
- stderr jest bezpieczny dla komunikacji z użytkownikiem

### 2. Flow działania

```
┌─────────────┐
│  Użytkownik │
│  "usuń sesje"│
└──────┬──────┘
       │
       ▼
┌─────────────────────┐
│   Agent AI          │
│   (Claude Code)     │
│   Analizuje pytanie │
└──────┬──────────────┘
       │
       │ Pytanie jest niejasne!
       │
       ▼
┌────────────────────────────────┐
│ Tool: ask_for_clarification    │
│ question: "Które sesje?"       │
│ context: "Nie wiem czy stare   │
│          czy wszystkie"        │
└──────┬─────────────────────────┘
       │
       │ Wyświetla pytanie (stderr)
       ▼
┌─────────────────┐
│   Użytkownik    │
│   Input: "z     │
│   ostatniego    │
│   tygodnia"     │
└──────┬──────────┘
       │
       │ Odpowiedź zwrócona do agenta
       ▼
┌─────────────────────┐
│   Agent AI          │
│   Ma pełniejszą     │
│   informację        │
│   Wykonuje zadanie  │
└─────────────────────┘
```

### 3. Obsługa błędów

```python
try:
    user_response = input().strip()

    if not user_response:
        return [TextContent(
            type="text",
            text="User provided empty response to clarification request."
        )]
    # ... process response

except EOFError:
    # stdin został zamknięty
    return [TextContent(
        type="text",
        text="Error: Could not read user input (EOF)"
    )]
except Exception as e:
    # Inny błąd
    return [TextContent(
        type="text",
        text=f"Error reading user clarification: {str(e)}"
    )]
```

## 📝 Przykłady użycia

### Przykład 1: Niejasne polecenie usunięcia

**Użytkownik:** "usuń sesje"

**Agent AI myśli:** 🤔 "Które sesje? Wszystkie? Tylko stare? Z jakiego okresu?"

**Agent wywołuje:**
```json
{
  "name": "ask_for_clarification",
  "arguments": {
    "question": "Które sesje chcesz usunąć? Podaj okres (np. 'z ostatniego dnia', 'starsze niż tydzień') lub konkretne ID sesji.",
    "context": "Użytkownik poprosił o usunięcie sesji, ale nie określił których dokładnie."
  }
}
```

**Użytkownik widzi:**
```
🤔 **Prośba o doprecyzowanie pytania**

**Kontekst:** Użytkownik poprosił o usunięcie sesji, ale nie określił których dokładnie.

**Pytanie:** Które sesje chcesz usunąć? Podaj okres (np. 'z ostatniego dnia',
'starsze niż tydzień') lub konkretne ID sesji.

---
**Instrukcja:** Proszę podać odpowiedź na powyższe pytanie doprecyzowujące.
Agent AI czeka na Twoją odpowiedź, aby móc kontynuować.

💬 Twoja odpowiedź: _
```

**Użytkownik odpowiada:** "z ostatniego tygodnia"

**Agent otrzymuje:**
```json
{
  "clarification_question": "Które sesje chcesz usunąć?...",
  "context": "Użytkownik poprosił o usunięcie sesji...",
  "user_response": "z ostatniego tygodnia"
}
```

**Agent wykonuje:**
```json
{
  "name": "delete_sessions",
  "arguments": {
    "last_days": 7,
    "confirm": true
  }
}
```

### Przykład 2: Niejasne zapytanie o sesje

**Użytkownik:** "pokaż mi coś"

**Agent wywołuje:**
```json
{
  "name": "ask_for_clarification",
  "arguments": {
    "question": "Co dokładnie chcesz zobaczyć? Listę wszystkich sesji, szczegóły konkretnej sesji, czy coś innego?",
    "context": "Nie mogę określić co użytkownik chce wyświetlić."
  }
}
```

**Użytkownik:** "listę wszystkich sesji"

**Agent wywołuje:** `list_sessions`

## 🎯 Kiedy agent powinien używać tego tool-a?

Agent AI powinien wywołać `ask_for_clarification` gdy:

1. **Brak kluczowych informacji:**
   - "usuń sesje" (nie wiadomo które)
   - "pokaż sesję" (nie wiadomo którą)

2. **Wieloznaczność:**
   - "usuń stare" (co znaczy "stare"?)
   - "pokaż ostatnie" (ile ostatnich?)

3. **Potencjalne niebezpieczeństwo:**
   - "usuń wszystko" (czy na pewno WSZYSTKO?)
   - Operacje destrukcyjne wymagają potwierdzenia

4. **Wybór między opcjami:**
   - "eksportuj" (do jakiego formatu?)
   - "sortuj" (według czego?)

## ⚠️ Uwagi implementacyjne

### Ograniczenia stdin/stdout w MCP

W kontekście MCP:
- **stdout** jest zarezerwowany dla komunikacji protokołu (JSON-RPC)
- **stderr** można używać do komunikacji z użytkownikiem
- **stdin** może być używany, ale trzeba uważać na timing

### Alternatywne podejścia

W prawdziwej implementacji AZØRA (nie przez MCP, ale jako standalone app), można by:

1. **Callback function:**
   ```python
   def ask_user(question: str) -> str:
       # Wyświetl w UI AZØRA
       # Poczekaj na odpowiedź
       return user_input
   ```

2. **Event-driven:**
   ```python
   async def on_clarification_needed(question: str):
       await emit_event("need_clarification", question)
       response = await wait_for_event("user_response")
       return response
   ```

3. **Queue-based:**
   ```python
   clarification_queue.put(question)
   response = response_queue.get()
   ```

## 🧪 Testowanie

Uruchom test:
```bash
cd M3/azor-mcp-server
source .venv/bin/activate
python test_clarification.py
```

Wybierz opcję testową i wprowadź odpowiedź gdy zostaniesz zapytany.

## 🎓 Wnioski

**Zalety:**
- ✅ Agent może automatycznie dopytać o szczegóły
- ✅ Użytkownik nie musi od razu podawać wszystkich informacji
- ✅ Bezpieczniejsze (agent potwierdza przed destrukcyjnymi operacjami)
- ✅ Lepsza user experience - konwersacyjny styl

**Wyzwania:**
- ⚠️ Wymaga synchronicznego inputu (blocking)
- ⚠️ W środowisku MCP komunikacja przez stdin może być skomplikowana
- ⚠️ Trzeba uważać na konflikty stdout (protokół MCP) vs komunikacja z użytkownikiem

**Rekomendacja dla produkcji:**
W prawdziwej implementacji AZØRA warto rozważyć asynchroniczną komunikację z użytkownikiem (callback, events) zamiast blokującego `input()`.
