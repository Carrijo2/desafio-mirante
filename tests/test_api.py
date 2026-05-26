from fastapi.testclient import TestClient

from app.api import server


def test_health() -> None:
    client = TestClient(server.app)

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_modernize_persists_and_returns_payload(monkeypatch) -> None:
    monkeypatch.setattr(server, "save_history", lambda **kwargs: "history-1")
    client = TestClient(server.app)

    response = client.post(
        "/modernize",
        json={
            "source_code": """
            CREATE OR REPLACE FUNCTION fn_demo() RETURNS INT
            LANGUAGE plpgsql AS $$ BEGIN RETURN 1; END; $$;
            """
        },
    )

    payload = response.json()
    assert response.status_code == 200
    assert payload["id"] == "history-1"
    assert payload["status"] == "sucesso"
    assert "generated_code" in payload
    assert payload["report"]["stages"]["validation"]["ast_parse"] is True


def test_modernize_reports_persistence_failure(monkeypatch) -> None:
    def fail_save(**kwargs):
        raise RuntimeError("db down")

    monkeypatch.setattr(server, "save_history", fail_save)
    client = TestClient(server.app)

    response = client.post(
        "/modernize",
        json={
            "source_code": """
            CREATE OR REPLACE FUNCTION fn_demo() RETURNS INT
            LANGUAGE plpgsql AS $$ BEGIN RETURN 1; END; $$;
            """
        },
    )

    assert response.status_code == 503
    assert response.json()["detail"]["stages"]["persistence"]["status"] == "error"

