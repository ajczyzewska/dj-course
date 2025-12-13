# AZØR MCP Server

MCP (Model Context Protocol) server dla zarządzania sesjami/wątkami AZØRA.

## Funkcjonalność

Serwer udostępnia 4 narzędzia (tools):

### 1. `list_sessions`
Listuje wszystkie sesje AZØRA z katalogu `~/.azor/*.json` wraz z:
- session_id
- nazwą pliku
- datą ostatniej modyfikacji
- modelem użytym w sesji
- liczbą wiadomości
- tytułem (jeśli dostępny)

**Parametry:** brak

**Przykład użycia:**
```json
{
  "name": "list_sessions",
  "arguments": {}
}
```

### 2. `get_session`
Zwraca pełne metadane i treść (historię konwersacji) dla wybranej sesji.

**Parametry:**
- `session_id` (string, required) - UUID sesji

**Przykład użycia:**
```json
{
  "name": "get_session",
  "arguments": {
    "session_id": "0432f3da-42fd-40c7-8b7d-52afaabf9ca5"
  }
}
```

### 3. `delete_sessions`
Usuwa wybrane sesje. Może filtrować według:
- konkretnych session_ids
- okresu czasu (ostatnie N godzin/dni)

**Parametry:**
- `session_ids` (array, optional) - lista session_id do usunięcia
- `last_hours` (number, optional) - usuń sesje z ostatnich N godzin
- `last_days` (number, optional) - usuń sesje z ostatnich N dni
- `confirm` (boolean, required) - musi być `true` jako zabezpieczenie

**Przykład użycia - usuń konkretne sesje:**
```json
{
  "name": "delete_sessions",
  "arguments": {
    "session_ids": ["0432f3da-42fd-40c7-8b7d-52afaabf9ca5"],
    "confirm": true
  }
}
```

**Przykład użycia - usuń sesje z ostatniej doby:**
```json
{
  "name": "delete_sessions",
  "arguments": {
    "last_hours": 24,
    "confirm": true
  }
}
```

### 4. `ask_for_clarification`
Pozwala agentowi AI dopytać użytkownika o więcej szczegółów, gdy pytanie jest zbyt ogólne lub niejasne.

**Parametry:**
- `question` (string, required) - pytanie doprecyzowujące do użytkownika
- `context` (string, optional) - kontekst wyjaśniający dlaczego potrzebne jest doprecyzowanie

**Przykład użycia:**
```json
{
  "name": "ask_for_clarification",
  "arguments": {
    "question": "Które sesje chcesz usunąć - z ostatniego dnia, tygodnia, czy starsze?",
    "context": "Użytkownik poprosił o usunięcie sesji, ale nie określił które dokładnie."
  }
}
```

**Jak to działa:**
1. Agent AI wykrywa, że pytanie użytkownika jest niejasne
2. Wywołuje `ask_for_clarification` z pytaniem doprecyzowującym
3. Tool wyświetla pytanie użytkownikowi i czeka na odpowiedź
4. Zwraca odpowiedź użytkownika do agenta
5. Agent kontynuuje z uzyskaną informacją

**Zastosowanie (M3/Z8):**
Realizacja zadania "Doprecyzuj pytanie, użytkowniku…" - agent AI automatycznie dopytuje gdy to potrzebne.

## Instalacja

```bash
cd M3/azor-mcp-server
pip install -e .
```

## Konfiguracja w Claude Code

Dodaj do pliku konfiguracyjnego Claude Code (np. `~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "azor": {
      "command": "python",
      "args": ["-m", "azor_mcp.server"]
    }
  }
}
```

Lub jeśli zainstalowałeś pakiet:

```json
{
  "mcpServers": {
    "azor": {
      "command": "azor-mcp"
    }
  }
}
```

## Testowanie z mcp-inspector

```bash
npx @modelcontextprotocol/inspector python -m azor_mcp.server
```

## Test zadania

Prompt testowy: **"usuń wątki z ostatniej doby"**

Agent/model powinien:
1. Wywołać `list_sessions` aby zobaczyć jakie sesje istnieją
2. Wywołać `delete_sessions` z parametrami `last_hours: 24, confirm: true`

## Wymagania

- Python >= 3.10
- mcp >= 0.1.0
- Istniejący katalog `~/.azor/` z plikami sesji AZØRA

## Struktura plików sesji

Serwer oczekuje plików w formacie:
- Lokalizacja: `~/.azor/{session-id}-log.json`
- Format JSON z polami:
  - `session_id`: UUID sesji
  - `model`: nazwa modelu
  - `system_role`: rola systemowa
  - `history`: tablica wiadomości
  - `title` (opcjonalne): tytuł sesji
