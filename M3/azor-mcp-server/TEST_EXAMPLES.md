# Przykłady testowania AZØR MCP Server

## Test 1: Lista sesji (list_sessions)

Wywołaj tool `list_sessions` bez parametrów.

**Oczekiwany wynik:**
```json
{
  "name": "list_sessions",
  "arguments": {}
}
```

Odpowiedź powinna zawierać listę wszystkich sesji z katalogu `~/.azor/` wraz z:
- session_id
- nazwą pliku
- datą ostatniej modyfikacji
- modelem
- liczbą wiadomości

## Test 2: Pobierz szczegóły sesji (get_session)

Wybierz session_id z wyniku poprzedniego testu i wywołaj:

**Przykład:**
```json
{
  "name": "get_session",
  "arguments": {
    "session_id": "0432f3da-42fd-40c7-8b7d-52afaabf9ca5"
  }
}
```

**Oczekiwany wynik:**
Pełna treść sesji z metadanymi i historią konwersacji.

## Test 3: Usuń sesje z ostatniej doby (delete_sessions)

**UWAGA:** To jest destrukcyjna operacja! Upewnij się, że masz backup ważnych sesji.

**Przykład - najpierw DRY RUN (bez confirm):**
```json
{
  "name": "delete_sessions",
  "arguments": {
    "last_hours": 24,
    "confirm": false
  }
}
```

**Oczekiwany wynik:** Błąd informujący, że `confirm` musi być `true`.

**Przykład - właściwe usunięcie:**
```json
{
  "name": "delete_sessions",
  "arguments": {
    "last_hours": 24,
    "confirm": true
  }
}
```

**Oczekiwany wynik:** Lista usuniętych sesji.

## Test 4: Prompt agenta (zadanie z HOMEWORK.md)

**Prompt:** "usuń wątki z ostatniej doby"

**Oczekiwane zachowanie agenta:**
1. Agent powinien najpierw wywołać `list_sessions`, aby sprawdzić jakie sesje istnieją
2. Następnie agent powinien wywołać `delete_sessions` z parametrami:
   - `last_hours: 24`
   - `confirm: true`

## Test 5: Usuń konkretne sesje

```json
{
  "name": "delete_sessions",
  "arguments": {
    "session_ids": ["0432f3da-42fd-40c7-8b7d-52afaabf9ca5"],
    "confirm": true
  }
}
```

## Test 6: Usuń sesje z ostatniego tygodnia

```json
{
  "name": "delete_sessions",
  "arguments": {
    "last_days": 7,
    "confirm": true
  }
}
```

## Testowanie w mcp-inspector

1. Uruchom inspector:
```bash
cd M3/azor-mcp-server
source .venv/bin/activate
npx @modelcontextprotocol/inspector python -m azor_mcp.server
```

2. Przeglądarka otworzy się automatycznie na `http://localhost:6274/...`

3. W interfejsie Inspector:
   - Kliknij "Tools" aby zobaczyć dostępne narzędzia
   - Kliknij na każde narzędzie aby zobaczyć jego schema i wypróbować
   - Wprowadź parametry i kliknij "Call Tool"

## Testowanie z Claude Code

1. Dodaj do konfiguracji Claude Code (np. `~/.config/claude/claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "azor": {
      "command": "python",
      "args": ["-m", "azor_mcp.server"],
      "env": {
        "PATH": "/Users/agnieszka/repos/dj/dj-course/M3/azor-mcp-server/.venv/bin:/usr/local/bin:/usr/bin:/bin"
      }
    }
  }
}
```

2. Zrestartuj Claude Code

3. Sprawdź czy tools są dostępne - Claude Code powinien móc je używać automatycznie

4. Przetestuj prompt: **"usuń wątki z ostatniej doby"**
