import pytest

from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient
from ..database import Base
from ..main import app
from ..models import Todos


DATABASE_URL = "postgresql://postgres:123456@localhost:5432/TodoApplicationDatabaseTest"

engine = create_engine(
    DATABASE_URL,
    poolclass=StaticPool,
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_get_current_user():
    return {'username': 'test_user', 'id': 1, 'user_role': 'admin'}


client = TestClient(app)

@pytest.fixture()
def test_user():
    db = TestingSessionLocal()
    db.execute(text("INSERT INTO users (id, username) VALUES (1, 'test_user')"))
    db.commit()
    yield {'id': 1, 'username': 'test_user'}
    db.execute(text("DELETE FROM users;"))
    db.execute(text("ALTER SEQUENCE users_id_seq RESTART WITH 1;"))
    db.commit()


@pytest.fixture()
def test_todo(test_user):
    todo = Todos(
        title='First Todo',
        description='This is the description',
        priority=5,
        complete=False,
        owner=1,
    )
    db = TestingSessionLocal()
    db.add(todo)
    db.commit()
    yield todo
    with engine.connect() as conn:
        conn.execute(text("DELETE FROM todos;"))
        conn.execute(text("ALTER SEQUENCE todos_id_seq RESTART WITH 1;"))
        conn.commit()
