import pytest
from app import app, db, User
from flask import json

@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://user:password@localhost/test_db'
    with app.test_client() as client:
        with app.app_context():
            try:
                db.create_all()
                yield client
            except Exception as e:
                print(f"Error during setup: {e}")
            finally:
                db.drop_all()

def test_create_user(client):
    response = client.post('/users', json={'name': 'John Doe', 'email': 'john@example.com'})
    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully'

def test_get_user(client):
    user = User(name='John Doe', email='john@example.com')
    db.session.add(user)
    db.session.commit()

    response = client.get(f'/users/{user.id}')
    assert response.status_code == 200
    assert response.json['user']['name'] == 'John Doe'
    assert response.json['user']['email'] == 'john@example.com'