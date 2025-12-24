from flask import Blueprint, request, jsonify, current_app
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import check_password_hash
from itsdangerous import URLSafeTimedSerializer
from models import db, User
from mail_utils import send_verification_email, send_password_reset_email
import re

auth_bp = Blueprint('auth', __name__)

def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

@auth_bp.route('/api/register', methods=['POST'])
def register():
    data = request.json
    
    # Validation des données
    if not all(k in data for k in ['username', 'email', 'password']):
        return jsonify({'error': 'Données manquantes'}), 400
    
    if not validate_email(data['email']):
        return jsonify({'error': 'Email invalide'}), 400
    
    if len(data['password']) < 6:
        return jsonify({'error': 'Mot de passe trop court (min 6 caractères)'}), 400
    
    # Vérifier si l'utilisateur existe déjà
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 400
    
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'error': 'Email déjà utilisé'}), 400
    
    # Créer l'utilisateur
    user = User(
        username=data['username'],
        email=data['email'],
        first_name=data.get('first_name', ''),
        last_name=data.get('last_name', ''),
        phone=data.get('phone', '')
    )
    user.set_password(data['password'])
    
    db.session.add(user)
    db.session.commit()
    
    # Envoyer email de vérification
    try:
        send_verification_email(current_app.extensions['mail'], user)
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'envoi de l'email: {e}")
    
    return jsonify({
        'message': 'Compte créé avec succès. Veuillez vérifier votre email.',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    
    if not all(k in data for k in ['email', 'password']):
        return jsonify({'error': 'Email et mot de passe requis'}), 400
    
    user = User.query.filter_by(email=data['email']).first()
    
    if not user or not user.check_password(data['password']):
        return jsonify({'error': 'Email ou mot de passe incorrect'}), 401
    
    if not user.is_active:
        return jsonify({'error': 'Compte désactivé'}), 403
    
    login_user(user, remember=data.get('remember', False))
    
    # Mettre à jour la dernière connexion
    from datetime import datetime
    user.last_login = datetime.utcnow()
    db.session.commit()
    
    return jsonify({
        'message': 'Connexion réussie',
        'user': user.to_dict()
    })

@auth_bp.route('/api/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Déconnexion réussie'})

@auth_bp.route('/api/verify-email/<token>', methods=['GET'])
def verify_email(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    try:
        email = s.loads(token, max_age=3600)  # Token valide 1 heure
    except:
        return jsonify({'error': 'Token invalide ou expiré'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    if user.is_verified:
        return jsonify({'message': 'Email déjà vérifié'})
    
    user.is_verified = True
    db.session.commit()
    
    return jsonify({'message': 'Email vérifié avec succès'})

@auth_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    email = request.json.get('email')
    
    if not email:
        return jsonify({'error': 'Email requis'}), 400
    
    user = User.query.filter_by(email=email).first()
    if user:
        send_password_reset_email(current_app.extensions['mail'], user)
    
    # Pour des raisons de sécurité, on ne précise pas si l'email existe
    return jsonify({'message': 'Si votre email existe, vous recevrez un lien de réinitialisation'})

@auth_bp.route('/api/reset-password/<token>', methods=['POST'])
def reset_password(token):
    s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
    
    try:
        email = s.loads(token, max_age=3600)
    except:
        return jsonify({'error': 'Token invalide ou expiré'}), 400
    
    data = request.json
    if not data.get('password'):
        return jsonify({'error': 'Nouveau mot de passe requis'}), 400
    
    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({'error': 'Utilisateur non trouvé'}), 404
    
    user.set_password(data['password'])
    db.session.commit()
    
    return jsonify({'message': 'Mot de passe réinitialisé avec succès'})

@auth_bp.route('/api/profile', methods=['GET'])
@login_required
def get_profile():
    return jsonify(current_user.to_dict())

@auth_bp.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.json
    
    if 'email' in data and data['email'] != current_user.email:
        if User.query.filter_by(email=data['email']).first():
            return jsonify({'error': 'Email déjà utilisé'}), 400
        current_user.email = data['email']
        current_user.is_verified = False
    
    if 'username' in data and data['username'] != current_user.username:
        if User.query.filter_by(username=data['username']).first():
            return jsonify({'error': 'Nom d\'utilisateur déjà utilisé'}), 400
        current_user.username = data['username']
    
    if 'first_name' in data:
        current_user.first_name = data['first_name']
    
    if 'last_name' in data:
        current_user.last_name = data['last_name']
    
    if 'phone' in data:
        current_user.phone = data['phone']
    
    db.session.commit()
    
    return jsonify({
        'message': 'Profil mis à jour',
        'user': current_user.to_dict()
    })