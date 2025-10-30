from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate
from flask_cors import CORS

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Database Configuration (PostgreSQL)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:1234@localhost:5432/netlend_db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key_here'

# Initialize extensions
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
migrate = Migrate(app, db)

# ----------------------- MODELS -----------------------

# Buyer model
class Buyer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    mortgage_type = db.Column(db.String(120), nullable=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)


# Borrower model
class Borrower(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    loan_amount = db.Column(db.Float, nullable=False)

# ----------------------- ROUTES -----------------------

@app.route('/')
def home():
    return jsonify({"message": "Welcome to NetLend API (Buyers & Borrowers)"})

# -------- Buyer Routes --------

@app.route('/register', methods=['POST'])
def register_buyer():
    data = request.get_json()
    full_name = data.get('full_name')
    email = data.get('email')
    password = data.get('password')

    if not full_name or not email or not password:
        return jsonify({'error': 'All fields are required'}), 400

    if Buyer.query.filter_by(email=email).first():
        return jsonify({'error': 'Email already exists'}), 400

    new_buyer = Buyer(full_name=full_name, email=email)
    new_buyer.set_password(password)
    db.session.add(new_buyer)
    db.session.commit()

    return jsonify({'message': 'Buyer registered successfully'}), 201


@app.route('/login', methods=['POST'])
def login_buyer():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    buyer = Buyer.query.filter_by(email=email).first()

    if buyer and buyer.check_password(password):
        return jsonify({'message': 'Login successful', 'buyer_id': buyer.id})
    else:
        return jsonify({'error': 'Invalid credentials'}), 401

# -------- Borrower Routes --------

@app.route('/borrowers', methods=['POST'])
def add_borrower():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    loan_amount = data.get('loan_amount')

    if not name or not email or not loan_amount:
        return jsonify({'error': 'All fields (name, email, loan_amount) are required'}), 400

    if Borrower.query.filter_by(email=email).first():
        return jsonify({'error': 'Borrower with this email already exists'}), 400

    new_borrower = Borrower(name=name, email=email, loan_amount=loan_amount)
    db.session.add(new_borrower)
    db.session.commit()

    return jsonify({'message': 'Borrower added successfully', 'borrower_id': new_borrower.id}), 201


@app.route('/borrowers', methods=['GET'])
def get_borrowers():
    borrowers = Borrower.query.all()
    result = [
        {'id': b.id, 'name': b.name, 'email': b.email, 'loan_amount': b.loan_amount}
        for b in borrowers
    ]
    return jsonify(result), 200


# ----------------------- MAIN -----------------------
if __name__ == '__main__':
    app.run(port=5001)
