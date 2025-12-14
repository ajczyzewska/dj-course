# Changelog - M3: MCP Tools Integration

## Dodane pliki

### Narzędzia MCP
- `src/tools/__init__.py` - Inicjalizacja modułu tools
- `src/tools/mcp_tools.py` - Implementacja 3 narzędzi MCP:
  - `list_sessions()` - listuje sesje
  - `get_session(session_id)` - pobiera szczegóły sesji
  - `delete_sessions(...)` - usuwa sesje
- `src/tools/README.md` - Dokumentacja narzędzi

### Dokumentacja
- `M3_HOMEWORK_MCP.md` - Dokumentacja zadania domowego M3

## Zmodyfikowane pliki

### Function Calling
- `src/llm/gemini_client.py`:
  - Dodano import `json`, `Callable`
  - Rozszerzono `GeminiChatSessionWrapper` o:
    - `tools_map` w konstruktorze
    - `_handle_function_call()` - wykonywanie narzędzi
    - Automatyczne wykrywanie function calls w `send_message()`
  - Rozszerzono `create_chat_session()` o parametry:
    - `tools: Optional[List[Dict]]`
    - `tools_map: Optional[Dict[str, Callable]]`
  - Konwersja definicji narzędzi do formatu Gemini

### Integracja z sesją
- `src/session/chat_session.py`:
  - Import `TOOLS_DEFINITIONS`, `TOOLS_MAP` z `tools.mcp_tools`
  - W `_initialize_llm_session()`:
    - Przekazywanie narzędzi do Gemini
    - Warunkowe dodawanie tools (tylko dla Gemini)

### Konfiguracja
- `.env`:
  - Zmiana `ENGINE=LLAMA_CPP` → `ENGINE=GEMINI`
  - Zmiana `MODEL_NAME` → `gemini-2.0-flash-exp`
  - Zakomentowanie konfiguracji lokalnego modelu

## Funkcjonalność

Model Gemini automatycznie:
1. Wykrywa kiedy użytkownik chce zarządzać sesjami
2. Wywołuje odpowiednie narzędzie
3. Przetwarza wyniki
4. Odpowiada użytkownikowi

## Test

Prompt: "usuń wątki z ostatniej doby"

Rezultat:
- Model wywołuje `list_sessions()`
- Model wywołuje `delete_sessions(last_hours=24, confirm=True)`
- Użytkownik otrzymuje informację o usuniętych sesjach

## Wymagania

- Gemini API key (darmowy tier)
- Biblioteka `google-genai` (już w requirements.txt)
