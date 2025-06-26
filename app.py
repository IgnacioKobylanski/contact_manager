from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
import os

load_dotenv()

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DB_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Modelo Contact
class Contact(db.Model):
    __tablename__ = 'contacts'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    company = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

# Modelo User
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, server_default=db.func.current_timestamp())

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

# Ruta para obtener todos los contactos
@app.route('/contacts', methods=['GET'])
def get_contacts():
    contacts = Contact.query.all()
    result = []
    for c in contacts:
        result.append({
            'id': c.id,
            'name': c.name,
            'email': c.email,
            'phone': c.phone,
            'company': c.company,
            'created_at': c.created_at.isoformat()
        })
    return jsonify(result)

# Ruta para obtener un contacto por ID
@app.route('/contacts/<int:id>', methods=['GET'])
def get_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404

    result = {
        'id': contact.id,
        'name': contact.name,
        'email': contact.email,
        'phone': contact.phone,
        'company': contact.company,
        'created_at': contact.created_at.isoformat()
    }
    return jsonify(result)

# Ruta para agregar un contacto (POST)
@app.route('/contacts', methods=['POST'])
def add_contact():
    print("Raw data:", request.data)
    print("JSON data:", request.get_json())

    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    company = data.get('company')

    if not name or not email:
        return jsonify({'error': 'Name and email are required'}), 400

    existing = Contact.query.filter_by(email=email).first()
    if existing:
        return jsonify({'error': 'Email already exists'}), 400

    new_contact = Contact(
        name=name,
        email=email,
        phone=phone,
        company=company
    )

    db.session.add(new_contact)
    db.session.commit()

    return jsonify({'message': 'Contact added', 'id': new_contact.id}), 201


# Ruta para actualizar un contacto
@app.route('/contacts/<int:id>', methods=['PUT'])
def update_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404

    data = request.get_json()

    contact.name = data.get('name', contact.name)
    contact.email = data.get('email', contact.email)
    contact.phone = data.get('phone', contact.phone)
    contact.company = data.get('company', contact.company)

    db.session.commit()

    return jsonify({'message': 'Contact updated'})

# Ruta para eliminar un contacto
@app.route('/contacts/<int:id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get(id)
    if not contact:
        return jsonify({'error': 'Contact not found'}), 404

    db.session.delete(contact)
    db.session.commit()

    return jsonify({'message': 'Contact deleted'})

# Rutas User
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    existing_user = User.query.filter_by(email=email).first()
    if existing_user:
        return jsonify({'error': 'Email already registered'}), 400

    new_user = User(email=email)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({'message': 'User registered successfully'}), 201

# Rutas login usuarios
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data:
        return jsonify({'error': 'No input data provided'}), 400

    email = data.get('email')
    password = data.get('password')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    return jsonify({'message': 'Login successful'}), 200



@app.route('/test-json', methods=['POST'])
def test_json():
    print("Raw data:", request.data)
    print("JSON data:", request.get_json())
    return jsonify({'message': 'Received data'}), 200


if __name__ == '__main__':
    app.run(debug=True)
