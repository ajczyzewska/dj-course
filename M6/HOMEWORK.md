# Zadanie 1

Uzupełnij setup deliveroo:
- Dodaj rejestr obrazów docker 🐳
- Napisz skrypt shell który:
  - Buduje obraz
  - Pushuje go do ww. rejestru
- Do rejestru dodaj jakiś UI
- Wrzuć screena z otagowanym obrazem

# Zadanie 2

Wraz z Deep Research wygeneruj docker-compose.yml:
- server mongo + mongo-express (admin UI) + redis
- server: node.js/TS/express albo golang/gin
- apka zawiera 2 endpointy:
  - GET /invoices
  - POST /invoices
    odpowiednio czytające/modyfikujące db + zapisujące/aktualizujące kesz redisowy
- uruchom i upewnij się, że działa poprawnie
- wypróbuj inne LLMy - i porównaj precyzję

# Zadanie 3

Reguły dla Dockerfile i Docker Compose
- weź transkrypcje z tego modułu
- zmontuj (wraz z LLMem) best practices dla Dockerfile i docker-compose.yml
- iteruj (np. z innym LLMem/agentem)
- zweryfikuj samodzielnie

# Zadanie 4

Zoptymalizuj obrazy apek frontendowych:
- `deliveroo/tms-frontend` (react)
Opcjonalnie:
- `deliveroo/customer-portal` (vue/nuxt)
- `deliveroo/wms-frontend` (angular)
Przeanalizuj obrazy z `dive` - przed i po optymalizacji.

Sprawdź, czy możesz zastosować mechanizm docker [**Cache Mount**](https://docs.docker.com/build/cache/optimize/#use-cache-mounts) aby zwiększyć optymalizację.

Kontenery mają być uruchomione nie spod roota.

# Zadanie 5

Zintegruj dockera z MCP:
- Ustaw wybrany serwer MCP dla dockera
- Wykorzystaj `wms-api` które rzuca błędem dla `GET /employees`
- Agent/LLM ma mieć dostęp do błędów z SQL (brakująca kolumna na tabeli `party`)

# Zadanie 6

Wykorzystaj setup Dev Containers z repo:
- Uruchom `wms-api` pod devcontainers
- Dodaj do setupu reverse proxy nginx tak,
aby na `/` szedł forward `wms-api`
- Wykorzystaj Deep Research
- Podziel się nie tylko rozwiązaniem, ale i **ewentualnym procesem nauki**

Zmodyfikuj docker-compose dla `wms-api` tak, aby oprzeć go o [compose/watch](https://docs.docker.com/compose/how-tos/file-watch/).

# Zadanie 7

Aplikacja pythonowa `wms-api` ma wyłącznie server developerski.
Dostosuj setup tak, aby dodać serwer produkcyjny WSGI:
- np. Gunicorn (green unicorn)

Rozbuduj docker-compose
(np. ten mniejszy z dev containers):
- dodaj profile `dev` i `prod`
- sprawdź czy compose uruchamia je odpowiednio

# Zadanie 8

Rozbuduj któryś serwis deliveroo:
- `wms-api`
- `tms-api`
I wygeneruj kilka przykładowych testów
(CRUD na bazie) w oparciu o test containers:
- `GET /<kolekcja>`
- `DELETE /<kolekcja>/id`
- `PUT_lub_PATCH /<kolekcja>/id`

## Rozwiązanie — `wms-api` + `storage_request`

### Co zostało zrobione

Rozbudowano `wms-api` o nowy zasób `/storage-requests` (kolekcja `storage_request` w bazie)
oraz napisano 10 testów integracyjnych z Testcontainers.

**Nowe pliki:**
- `src/routes/storage_requests.py` — blueprint z 3 endpointami
- `tests/test_storage_requests.py` — testy integracyjne
- `tests/__init__.py` — marker pakietu

**Zmienione pliki:**
- `src/application.py` — rejestracja blueprintu
- `requirements.txt` — dodano `pytest`, `pytest-flask`, `testcontainers[postgres]`

### Endpointy

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| `GET` | `/storage-requests/` | Lista wszystkich zgłoszeń magazynowych (JOIN z `party` po nazwę kontrahenta) |
| `DELETE` | `/storage-requests/<id>` | Usuwa zgłoszenie; 404 jeśli nie istnieje |
| `PATCH` | `/storage-requests/<id>` | Zmienia status (`PENDING` / `ACCEPTED` / `REJECTED`); walidacja, 400 dla złego statusu |

### Jak działają Testcontainers

Testcontainers to biblioteka (dostępna w Javie, Pythonie, Go i innych) która pozwala **zarządzać kontenerami Dockera programmatycznie z poziomu kodu testowego**. Zamiast utrzymywać osobną bazę testową lub mockować warstwę danych, testy same startują prawdziwy kontener z prawdziwą bazą — i same go usuwają po zakończeniu.

#### Problem, który rozwiązuje

Testy integracyjne dla warstwy bazodanowej mają zwykle dwa złe wyjścia:

| Podejście | Problem |
|-----------|---------|
| Mock bazy danych | Nie testuje prawdziwego SQL, dialektów, constraintów |
| Współdzielona baza testowa | Stan brudny między testami, konflikty w CI, "działa u mnie" |
| Lokalna baza na stałe | Wymaga setup po każdym `git clone`, różne wersje między devami |

Testcontainers rozwiązuje to przez **efemeryczne kontenery** — każdy run testów dostaje czystą bazę, identyczną na każdej maszynie (lokalnie i w CI), bo obraz Dockera jest deterministyczny.

#### Jak to działa krok po kroku

```
pytest start
    │
    ▼
PostgresContainer("postgres:17-alpine")
    │  ① biblioteka wysyła request do Docker daemon (przez socket /var/run/docker.sock)
    │  ② Docker pobiera obraz (lub bierze z cache)
    │  ③ Docker startuje kontener na losowym wolnym porcie hosta (np. 54321)
    │  ④ Testcontainers czeka aż Postgres zacznie akceptować połączenia (health check)
    ▼
pg.get_connection_url()
    │  zwraca: postgresql+psycopg2://test:test@localhost:54321/test
    ▼
create_engine(url)  ←  normalne SQLAlchemy, nic specjalnego
    │
    ▼
[testy działają na prawdziwym Postgresie]
    │
    ▼
koniec bloku `with`
    │  kontener jest zatrzymywany i usuwany
    ▼
pytest end
```

Losowy port jest kluczowy — dzięki niemu wiele suite'ów może działać równolegle bez konfliktów, i nie ma kolizji z lokalną bazą na 5432.

#### `scope="module"` — jeden kontener na plik

```python
@pytest.fixture(scope="module")
def postgres_engine():
    with PostgresContainer("postgres:17-alpine") as pg:
        ...
        yield engine   # kontener żyje dopóki yield nie wróci
```

`scope="module"` oznacza: utwórz fixture **raz na cały moduł testowy** (plik), nie per test. Kontener startuje ~2-3s, więc uruchamianie go dla każdego z 10 testów z osobna byłoby nieakceptowalne. Zamiast tego wszystkie testy w pliku współdzielą jeden kontener i jedną bazę — dlatego ważna jest izolacja danych (każdy test wstawia i usuwa własne wiersze).

#### Gdzie Testcontainers jest szczególnie wartościowy

- Testy z prawdziwymi constraintami (FK, CHECK, UNIQUE) — mock ich nie sprawdzi
- Testy migracji schematu (Flyway, Alembic) — wertujesz czy migracja rzeczywiście przechodzi
- Testy specyficznych funkcji bazy (JSONB w Postgresie, window functions, CTE) — zachowanie SQLite się różni
- CI/CD — działa identycznie jak lokalnie, bo kontener = ten sam obraz

#### W tym projekcie

```python
# podmiana silnika produkcyjnego na testowy
with patch.object(database, 'db_engine', postgres_engine):
    import application
    yield application.app
```

`patch.object` zastępuje `db_engine` w module `database` na czas testów. Moduły Pythona są singletonami — po pierwszym imporcie ten sam obiekt jest współdzielony w całym procesie. Podmiana jednego atrybutu wystarcza, żeby wszystkie route'y automatycznie trafiały do kontenera testowego, bez żadnych zmian w kodzie produkcyjnym.
