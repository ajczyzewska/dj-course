# MCP Tools dla AZORA

Narzędzia do zarządzania sesjami AZORA używane przez model AI przez function calling.

## Narzędzia

### list_sessions()
Listuje wszystkie sesje z `~/.azor/*.json`

### get_session(session_id: str)
Zwraca pełną historię wybranej sesji

### delete_sessions(...)
Usuwa sesje według kryteriów (IDs lub czasu)

## Użycie

Narzędzia są automatycznie dostępne dla Gemini API z function calling.
Model sam decyduje kiedy je użyć na podstawie promptu użytkownika.

Przykład:
```
Użytkownik: "usuń wątki z ostatniej doby"
Model: wywołuje delete_sessions(last_hours=24, confirm=True)
```

## Implementacja

Zobacz `mcp_tools.py` dla szczegółów implementacji.
