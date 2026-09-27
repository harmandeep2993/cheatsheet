"""Database engine, session factory and the FastAPI dependency that hands out one session per request."""

from collections.abc import Iterator

from fastapi import Request
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker
from sqlalchemy.pool import StaticPool

IN_MEMORY_SQLITE = "sqlite://"


class Base(DeclarativeBase):
    """Parent class of every ORM table in this service."""


def create_db_engine(database_url: str) -> Engine:
    """Create the engine, with the SQLite tweaks needed for tests and local runs."""
    if not database_url.startswith("sqlite"):
        return create_engine(database_url, pool_pre_ping=True)
    # SQLite objects may be used from FastAPI's worker threads
    connect_args = {"check_same_thread": False}
    if database_url == IN_MEMORY_SQLITE:
        # Each new connection would get an empty in-memory database; StaticPool keeps exactly one
        return create_engine(database_url, connect_args=connect_args, poolclass=StaticPool)
    return create_engine(database_url, connect_args=connect_args)


def create_session_factory(engine: Engine) -> sessionmaker[Session]:
    """Factory that opens sessions bound to the engine."""
    return sessionmaker(bind=engine, expire_on_commit=False)


def get_session(request: Request) -> Iterator[Session]:
    """FastAPI dependency: one session per request, always closed afterwards."""
    session = request.app.state.session_factory()
    try:
        yield session
    finally:
        session.close()
