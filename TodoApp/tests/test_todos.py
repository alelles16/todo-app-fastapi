import pytest

from sqlalchemy import create_engine, StaticPool, text
from sqlalchemy.orm import sessionmaker
from ..database import Base
from ..main import app
from ..routers.todos import get_db, get_current_user
from ..models import Todos
from fastapi.testclient import TestClient
from fastapi import status

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


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user

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

def test_read_one_authenticated(test_todo):
    response = client.get('/todo/1')
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
            'title': 'First Todo',
            'priority': 5,
            'owner': 1,
            'complete': False,
            'id': 1,
            'description': 'This is the description'
    }

def test_read_one_authenticated_not_found(test_todo):
    response = client.get('/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found.'}

def test_create_todo(test_todo):
    request_data = {
        'title': 'New todo',
        'description': 'This is the description',
        'priority': 5,
        'complete': False
    }
    response = client.post('/todo/', json=request_data)
    assert response.status_code == status.HTTP_201_CREATED
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 2).first()
    assert model.title == request_data['title']
    assert model.description == request_data['description']
    assert model.priority == request_data['priority']
    assert model.complete == request_data['complete']
    assert model.owner == 1

def test_update_todo(test_todo):
    request_data = {
        'title': 'New todo title',
        'description': 'Learning new description',
        'priority': 4,
        'complete': False
    }
    response = client.put('/todo/1', json=request_data)
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model.title == request_data['title']
    assert model.description == request_data['description']
    assert model.priority == request_data['priority']
    assert model.complete == request_data['complete']

def test_update_todo_not_found(test_todo):
    request_data = {
        'title': 'New todo title',
        'description': 'Learning new description',
        'priority': 4,
        'complete': False
    }
    response = client.put('/todo/999', json=request_data)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}

def test_delete_todo(test_todo):
    response = client.delete('/todo/1')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Todos).filter(Todos.id == 1).first()
    assert model is None

def test_delete_todo_not_found(test_todo):
    response = client.delete('/todo/999')
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Todo not found'}
