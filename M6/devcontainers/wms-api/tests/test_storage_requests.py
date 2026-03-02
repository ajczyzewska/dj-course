"""
Integration tests for /storage-requests endpoints.
Uses Testcontainers to spin up a real PostgreSQL instance.
"""
import sys
import os
import pytest
from unittest.mock import patch
from sqlalchemy import create_engine, text
from testcontainers.postgres import PostgresContainer

# ---------------------------------------------------------------------------
# Path setup — allow imports from src/
# ---------------------------------------------------------------------------
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# ---------------------------------------------------------------------------
# Minimal DDL required by the storage_request endpoints
# (only the tables we actually need; referential integrity is preserved)
# ---------------------------------------------------------------------------
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS location (
    location_id SERIAL PRIMARY KEY,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    postal_code TEXT NOT NULL,
    country TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS warehouse (
    warehouse_id SERIAL PRIMARY KEY,
    location_id INTEGER NOT NULL REFERENCES location(location_id),
    name TEXT NOT NULL,
    description TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS party (
    party_id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    data JSONB,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS storage_request (
    request_id SERIAL PRIMARY KEY,
    issuing_party_id INTEGER NOT NULL REFERENCES party(party_id),
    warehouse_id INTEGER NOT NULL REFERENCES warehouse(warehouse_id),
    requested_entry_date TIMESTAMP NOT NULL,
    requested_exit_date TIMESTAMP NOT NULL,
    status TEXT NOT NULL
        CHECK (status IN ('PENDING','ACCEPTED','REJECTED'))
        DEFAULT 'PENDING',
    decisive_party_id INTEGER REFERENCES party(party_id),
    decision_date TIMESTAMP
);
"""

SEED_SQL = """
INSERT INTO location (address, city, postal_code, country)
VALUES ('ul. Magazynowa 1', 'Warszawa', '00-001', 'PL')
RETURNING location_id;
"""


# ---------------------------------------------------------------------------
# Module-scoped Postgres container — started once for all tests
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def postgres_engine():
    with PostgresContainer("postgres:17-alpine") as pg:
        engine = create_engine(pg.get_connection_url())
        with engine.begin() as conn:
            conn.execute(text(SCHEMA_SQL))
            loc_id = conn.execute(text(SEED_SQL)).scalar()
            conn.execute(
                text("INSERT INTO warehouse (location_id, name, description) VALUES (:loc, 'WH-1', 'Test warehouse')"),
                {'loc': loc_id}
            )
            conn.execute(
                text("INSERT INTO party (name, data) VALUES ('Testowy Kontrahent', '{\"type\": \"contractor_company\"}')")
            )
        yield engine


@pytest.fixture(scope="module")
def app_with_db(postgres_engine):
    """Create Flask app with database.db_engine patched to the test engine."""
    import database
    with patch.object(database, 'db_engine', postgres_engine):
        import application
        application.app.config['TESTING'] = True
        yield application.app


@pytest.fixture(scope="module")
def client(app_with_db):
    return app_with_db.test_client()


# ---------------------------------------------------------------------------
# Helper: insert a fresh storage_request, return its request_id
# ---------------------------------------------------------------------------
def _insert_request(engine, status='PENDING') -> int:
    with engine.begin() as conn:
        row = conn.execute(text("""
            INSERT INTO storage_request
                (issuing_party_id, warehouse_id, requested_entry_date, requested_exit_date, status)
            SELECT p.party_id, w.warehouse_id,
                   NOW() + INTERVAL '1 day', NOW() + INTERVAL '7 days', :status
            FROM party p, warehouse w
            LIMIT 1
            RETURNING request_id
        """), {'status': status}).fetchone()
    return row[0]


def _delete_request(engine, request_id: int):
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM storage_request WHERE request_id = :id"), {'id': request_id})


# ===========================================================================
# Tests
# ===========================================================================

class TestGetStorageRequests:
    def test_returns_list_with_data(self, client, postgres_engine):
        req_id = _insert_request(postgres_engine)
        try:
            response = client.get('/storage-requests/')
            assert response.status_code == 200
            data = response.get_json()
            assert isinstance(data, list)
            assert len(data) >= 1
            ids = [item['id'] for item in data]
            assert str(req_id) in ids
        finally:
            _delete_request(postgres_engine, req_id)

    def test_returns_empty_list_when_no_requests(self, client, postgres_engine):
        # Ensure no requests exist
        with postgres_engine.begin() as conn:
            conn.execute(text("DELETE FROM storage_request"))

        response = client.get('/storage-requests/')
        assert response.status_code == 200
        assert response.get_json() == []

    def test_response_fields_structure(self, client, postgres_engine):
        req_id = _insert_request(postgres_engine)
        try:
            response = client.get('/storage-requests/')
            data = response.get_json()
            item = next(i for i in data if i['id'] == str(req_id))
            assert 'contractorId' in item
            assert 'contractorName' in item
            assert 'status' in item
        finally:
            _delete_request(postgres_engine, req_id)


class TestDeleteStorageRequest:
    def test_delete_existing_request(self, client, postgres_engine):
        req_id = _insert_request(postgres_engine)
        response = client.delete(f'/storage-requests/{req_id}')
        assert response.status_code == 200
        assert 'deleted successfully' in response.get_json()['message']

    def test_delete_nonexistent_request_returns_404(self, client):
        response = client.delete('/storage-requests/999999')
        assert response.status_code == 404
        assert 'not found' in response.get_json()['error'].lower()


class TestPatchStorageRequestStatus:
    def test_patch_status_to_accepted(self, client, postgres_engine):
        req_id = _insert_request(postgres_engine)
        try:
            response = client.patch(
                f'/storage-requests/{req_id}',
                json={'status': 'ACCEPTED'},
                content_type='application/json'
            )
            assert response.status_code == 200
            assert 'ACCEPTED' in response.get_json()['message']
        finally:
            _delete_request(postgres_engine, req_id)

    def test_patch_status_to_rejected(self, client, postgres_engine):
        req_id = _insert_request(postgres_engine)
        try:
            response = client.patch(
                f'/storage-requests/{req_id}',
                json={'status': 'REJECTED'},
                content_type='application/json'
            )
            assert response.status_code == 200
            assert 'REJECTED' in response.get_json()['message']
        finally:
            _delete_request(postgres_engine, req_id)

    def test_patch_status_case_insensitive(self, client, postgres_engine):
        req_id = _insert_request(postgres_engine)
        try:
            response = client.patch(
                f'/storage-requests/{req_id}',
                json={'status': 'accepted'},
                content_type='application/json'
            )
            assert response.status_code == 200
        finally:
            _delete_request(postgres_engine, req_id)

    def test_patch_invalid_status_returns_400(self, client, postgres_engine):
        req_id = _insert_request(postgres_engine)
        try:
            response = client.patch(
                f'/storage-requests/{req_id}',
                json={'status': 'INVALID_STATUS'},
                content_type='application/json'
            )
            assert response.status_code == 400
            assert 'error' in response.get_json()
        finally:
            _delete_request(postgres_engine, req_id)

    def test_patch_nonexistent_request_returns_404(self, client):
        response = client.patch(
            '/storage-requests/999999',
            json={'status': 'ACCEPTED'},
            content_type='application/json'
        )
        assert response.status_code == 404
        assert 'not found' in response.get_json()['error'].lower()
