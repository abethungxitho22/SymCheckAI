"""
SymCheck AI - Medical Triage System
Base backend with user auth
"""

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///symcheck.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access your medical history.'

# ================================================================
# DATABASE MODELS
# ================================================================

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    medical_histories = db.relationship('MedicalHistory', backref='user', lazy=True)

class MedicalHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    session_id = db.Column(db.String(100), nullable=False)
    symptoms = db.Column(db.Text, nullable=False)
    conversation = db.Column(db.Text)  # JSON
    final_conditions = db.Column(db.Text)  # JSON
    urgency = db.Column(db.String(50))
    confidence = db.Column(db.Float)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ================================================================
# AUTHENTICATION ROUTES
# ================================================================

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        if User.query.filter_by(email=email).first():
            flash('Email already registered.')
            return redirect(url_for('register'))
        
        hashed = generate_password_hash(password)
        user = User(email=email, password_hash=hashed)
        db.session.add(user)
        db.session.commit()
        
        login_user(user)
        flash('Registration successful!')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('dashboard'))
        
        flash('Invalid email or password.')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/dashboard')
@login_required
def dashboard():
    histories = MedicalHistory.query.filter_by(user_id=current_user.id).order_by(MedicalHistory.created_at.desc()).all()
    return render_template('dashboard.html', histories=histories)

@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html')

# ================================================================
# API ROUTES
# ================================================================

@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze():
    """Placeholder for AI analysis - will be implemented next"""
    data = request.get_json()
    user_message = data.get('message', '')
    
    # Placeholder response
    return jsonify({
        'response': f"Received your message: '{user_message}'. AI integration coming soon!",
        'confidence': 0,
        'assessment_ready': False
    })

@app.route('/api/save-assessment', methods=['POST'])
@login_required
def save_assessment():
    data = request.get_json()
    
    history = MedicalHistory(
        user_id=current_user.id,
        session_id=data.get('session_id', ''),
        symptoms=data.get('symptoms', ''),
        conversation=json.dumps(data.get('conversation', [])),
        final_conditions=json.dumps(data.get('conditions', [])),
        urgency=data.get('urgency', ''),
        confidence=data.get('confidence', 0)
    )
    db.session.add(history)
    db.session.commit()
    
    return jsonify({'success': True})

# ================================================================
# MAIN
# ================================================================

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    print("=" * 60)
    print("🩺 SymCheck AI - Medical Triage System")
    print("=" * 60)
    print("\n📍 http://127.0.0.1:5000")
    print("\n⚠️ NOT MEDICAL ADVICE - For educational purposes only")
    print("\nPress Ctrl+C to stop\n")
    app.run(debug=True, port=5000)