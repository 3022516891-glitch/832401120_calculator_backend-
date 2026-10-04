from unittest.mock import Mock

import pytest

from app import database
from app.database import database_url, execute_query


def test_vercel_requires_external_database(monkeypatch):
    monkeypatch.setenv("VERCEL", "1")
    with pytest.raises(RuntimeError, match="DATABASE_URL"):
        database_url()


def test_database_url_validation(monkeypatch):
    monkeypatch.setenv("DATABASE_URL", "sqlite:///calculator.db")
    with pytest.raises(ValueError, match="PostgreSQL"):
        database_url()


def test_postgres_parameters_are_not_interpolated():
    connection = Mock()
    expression = "1+2'; DROP TABLE calculation_history; --"
    execute_query(connection, "SELECT * FROM calculation_history WHERE expression = ?", (expression,))
    connection.execute.assert_called_once_with(
        "SELECT * FROM calculation_history WHERE expression = %s", (expression,),
    )


@pytest.mark.parametrize("fails", [False, True])
def test_postgres_connection_cleanup(monkeypatch, fails):
    import psycopg

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:example@localhost/test")
    connection = Mock()
    connect = Mock(return_value=connection)
    monkeypatch.setattr(psycopg, "connect", connect)
    if fails:
        with pytest.raises(RuntimeError, match="test error"):
            with database.get_connection():
                raise RuntimeError("test error")
        connection.rollback.assert_called_once()
        connection.commit.assert_not_called()
    else:
        with database.get_connection() as actual:
            assert actual is connection
        connection.commit.assert_called_once()
        connection.rollback.assert_not_called()
    connection.close.assert_called_once()
    assert connect.call_args.kwargs["prepare_threshold"] is None


def test_postgres_table_initialization(monkeypatch):
    import psycopg

    monkeypatch.setenv("DATABASE_URL", "postgresql://user:example@localhost/test")
    connection = Mock()
    monkeypatch.setattr(psycopg, "connect", Mock(return_value=connection))
    database.initialize_database()
    query = connection.execute.call_args.args[0]
    assert "BIGSERIAL" in query
    assert "angle_mode" in query
    assert "PRAGMA" not in query
    connection.commit.assert_called_once()
