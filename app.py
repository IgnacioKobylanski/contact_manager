from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from dotenv import load_dotenv
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

# Ruta para agregar un contacto (POST)
@app.route('/contacts', methods=['POST'])
def add_contact():
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

if __name__ == '__main__':
    app.run(debug=True)
