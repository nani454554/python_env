from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
import os

app = Flask(__name__)

# Configurations
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/mydatabase')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Initialize Redis
redis_client = Redis(host='localhost', port=6379, db=0)

# Model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.name}>'

# Routes
@app.route('/')
def index():
    return "Welcome to the Flask application!"

@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    new_user = User(name=data['name'], email=data['email'])
    db.session.add(new_user)
    db.session.commit()
    return jsonify({'message': 'User created successfully'}), 201

@app.route('/users/<int:id>', methods=['GET'])
def get_user(id):
    # Check cache first
    cached_user = redis_client.get(f'user:{id}')
    if cached_user:
        return jsonify({'user': cached_user.decode('utf-8')}), 200

    # If not cached, fetch from database
    user = User.query.get_or_404(id)
    user_data = {'id': user.id, 'name': user.name, 'email': user.email}
    redis_client.set(f'user:{id}', str(user_data))
    return jsonify({'user': user_data}), 200

if __name__ == '__main__':
    app.run(debug=True)