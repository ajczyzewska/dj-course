# M3 - Zadanie Domowe: MCP Tools dla AZORA

## Zadanie

Rozbudowa AZØRA o własne MCP tools z function calling.

### Wymagania

✅ Napisz własne MCP tools
✅ Rozbuduj AZØRA (kod bazowy - prace domowe z M1)
✅ Tools:
- Tool 1: listuje sesje/wątki w AZØZE (`~/.azor/*.json`) wraz z datą aktualizacji
- Tool 2: zwraca metadane + treść
- Tool 3: usuwa wybrany wątek/wątki

✅ TEST: Prompt "usuń wątki z ostatniej doby" - agent/model orkiestruje i wykonuje całość

## Implementacja

### 1. Narzędzia MCP (`src/tools/mcp_tools.py`)

Zaimplementowano 3 narzędzia:

#### `list_sessions()`
Listuje wszystkie sesje AZOR z katalogu `~/.azor/*.json`.

**Zwraca:**
```json
{
  "sessions": [
    {
      "session_id": "uuid",
      "file": "nazwa-pliku.json",
      "last_modified": "2025-12-14T22:26:31",
      "model": "gemini-2.0-flash-exp",
      "message_count": 4,
      "title": "Tytuł sesji"
    }
  ],
  "count": 22
}
```

#### `get_session(session_id: str)`
Zwraca pełne metadane i historię konwersacji dla wybranej sesji.

**Parametry:**
- `session_id` (string, required) - UUID sesji

**Zwraca:**
```json
{
  "session_id": "uuid",
  "model": "gemini-2.0-flash-exp",
  "history": [...],
  "last_modified": "2025-12-14T22:26:31",
  "title": "Tytuł"
}
```

#### `delete_sessions(...)`
Usuwa sesje według kryteriów.

**Parametry:**
- `session_ids` (array, optional) - Lista session_id do usunięcia
- `last_hours` (number, optional) - Usuń sesje z ostatnich N godzin
- `last_days` (number, optional) - Usuń sesje z ostatnich N dni
- `confirm` (boolean, **required**) - Musi być `true` (zabezpieczenie)

**Zwraca:**
```json
{
  "deleted_count": 5,
  "deleted": [
    {"session_id": "uuid", "file": "nazwa.json"}
  ],
  "status": "Completed successfully"
}
```

### 2. Function Calling - Gemini API

Wykorzystano Gemini 2.0 Flash z natywnym wsparciem function calling.

**Modyfikacje w `src/llm/gemini_client.py`:**

- Rozszerzono `GeminiChatSessionWrapper` o obsługę function calling
- Dodano automatyczne wykrywanie i wykonywanie wywołań funkcji
- Wyniki narzędzi są automatycznie zwracane do modelu

**Modyfikacje w `src/session/chat_session.py`:**

- Narzędzia MCP są przekazywane do modelu przy tworzeniu sesji
- Tylko dla Gemini (lokalne modele nie wspierają function calling)

### 3. Konfiguracja

**`.env`:**
```bash
ENGINE=GEMINI
MODEL_NAME=gemini-2.0-flash-exp
GEMINI_API_KEY=twój_klucz
```

## Test zadania

### Uruchomienie

```bash
cd M1/azor-chatdog-py
source .venv/bin/activate
python src/run.py
```

### Test prompt

```
usuń wątki z ostatniej doby
```

### Oczekiwane zachowanie

1. **AZOR/Gemini** wywołuje `list_sessions()` aby zobaczyć jakie sesje istnieją
2. **AZOR/Gemini** analizuje wyniki i decyduje o usunięciu
3. **AZOR/Gemini** wywołuje `delete_sessions(last_hours=24, confirm=True)`
4. **AZOR** informuje użytkownika o wynikach

### Przykładowa interakcja

```
Ty: usuń wątki z ostatniej doby

🔧 Wywołanie narzędzia: list_sessions({})
✅ Narzędzie list_sessions wykonane

🔧 Wywołanie narzędzia: delete_sessions({"last_hours": 24, "confirm": true})
✅ Narzędzie delete_sessions wykonane

AZOR: Usunąłem 5 wątków z ostatniej doby. Były to sesje:
- c2eb325c-... (Azor - Przyjaciel)
- 6a6f7e57-... (Azor - Przyjaciel)
- ...
```

## Architektura

```
┌─────────────────────────────────────────────────────┐
│                    Użytkownik                       │
│         "usuń wątki z ostatniej doby"               │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│              AZOR (ChatSession)                     │
│           + Gemini 2.0 Flash API                    │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│          Gemini Function Calling                    │
│  1. Analizuje prompt                                │
│  2. Decyduje które narzędzie użyć                   │
│  3. Zwraca FunctionCall                             │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│       GeminiChatSessionWrapper                      │
│  1. Wykrywa function_call                           │
│  2. Wykonuje narzędzie z tools_map                  │
│  3. Zwraca wynik do modelu                          │
└────────────────────┬────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│           MCP Tools (mcp_tools.py)                  │
│  - list_sessions()                                  │
│  - get_session(session_id)                          │
│  - delete_sessions(...)                             │
└─────────────────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────┐
│          ~/.azor/*.json files                       │
│  (sesje chatów AZORA)                               │
└─────────────────────────────────────────────────────┘
```

## Pliki

Główne pliki implementacji:

- `src/tools/mcp_tools.py` - Implementacja 3 narzędzi MCP
- `src/llm/gemini_client.py` - Function calling w Gemini
- `src/session/chat_session.py` - Integracja narzędzi z sesją
- `.env` - Konfiguracja Gemini API

## Wymagania systemowe

- Python >= 3.9
- Gemini API key (darmowy)
- Biblioteki: `google-genai`, `python-dotenv`, itp. (w `requirements.txt`)

## Uwagi

- Lokalne modele (Gemma, LLaMA) **nie wspierają** function calling w tej implementacji
- Dla zadania używany jest Gemini 2.0 Flash (darmowy tier: 1500 req/dzień)
- Narzędzia działają tylko z plikami sesji w formacie `~/.azor/*-log.json`
- Zabezpieczenie: `delete_sessions` wymaga `confirm=true`
