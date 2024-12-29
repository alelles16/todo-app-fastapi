from .utils import *
from ..routers.users import get_db, get_current_user
from fastapi import status


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_current_user] = override_get_current_user


def test_return_user(test_user):
    response = client.get('/users')
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['username'] == test_user.username
    assert response.json()['email'] == test_user.email
    assert response.json()['id'] == test_user.id
    assert response.json()['first_name'] == test_user.first_name
    assert response.json()['last_name'] == test_user.last_name
    assert response.json()['role'] == test_user.role

def test_change_password(test_user):
    response = client.put('/users/change_password', json={'password': 'password', 'new_password': 'test123'})
    assert response.status_code == status.HTTP_204_NO_CONTENT

def test_change_password_invalid(test_user):
    response = client.put('/users/change_password', json={'password': '<PASSWORD>', 'new_password': '<PASSWORD>'})
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_change_phone_number(test_user):
    response = client.put('/users/phone_number/32112312')
    assert response.status_code == status.HTTP_204_NO_CONTENT
    db = TestingSessionLocal()
    model = db.query(Users).filter(Users.id == test_user.id).first()
    assert model.phone_number == '32112312'
