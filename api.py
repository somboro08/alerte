from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'dev-secret-key-change-in-production'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signalalert.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Modèles
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    signalements = db.relationship('Signalement', backref='author', lazy=True)

class Signalement(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    type = db.Column(db.String(20), nullable=False)  # lost, missing, stolen
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(200), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    category = db.Column(db.String(50))
    contact = db.Column(db.String(200))
    reward = db.Column(db.String(100))
    status = db.Column(db.String(20), default='active')  # active, found
    image_url = db.Column(db.String(500))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Initialisation de la base de données
def init_db():
    with app.app_context():
        db.create_all()
        # Créer un utilisateur admin si inexistant
        if not User.query.filter_by(email='admin@signalalert.bj').first():
            admin = User(
                username='admin',
                email='admin@signalalert.bj',
                password='admin123'  # À changer en production
            )
            db.session.add(admin)
            db.session.commit()
            print("✅ Base de données initialisée avec l'utilisateur admin")

# Routes principales
@app.route('/')
def index():
    signalements = Signalement.query.filter_by(status='active').order_by(Signalement.created_at.desc()).limit(6).all()
    
    # Statistiques générales
    stats = {
        'total_signalements': Signalement.query.count(),
        'found_items': Signalement.query.filter_by(status='found').count(),
        'total_users': User.query.count(),
    }
    
    # Statistiques par catégorie
    stats_by_category = {
        'lost': Signalement.query.filter_by(type='lost', status='active').count(),
        'missing': Signalement.query.filter_by(type='missing', status='active').count(),
        'stolen': Signalement.query.filter_by(type='stolen', status='active').count()
    }
    
    return render_template('index.html', 
                          signalements=signalements,
                          stats=stats,
                          stats_by_category=stats_by_category,
                          current_user=current_user)

@app.route('/signalements')
def signalements():
    page = request.args.get('page', 1, type=int)
    type_filter = request.args.get('type', '')
    search = request.args.get('search', '')
    
    query = Signalement.query
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    if search:
        query = query.filter(Signalement.title.contains(search) | Signalement.description.contains(search))
    
    signalements = query.filter_by(status='active')\
                       .order_by(Signalement.created_at.desc())\
                       .paginate(page=page, per_page=12, error_out=False)
    
    return render_template('signalements.html',
                          signalements=signalements,
                          current_filter=type_filter,
                          search_query=search,
                          current_user=current_user)

@app.route('/signalement/<int:id>')
def signalement_detail(id):
    signalement = Signalement.query.get_or_404(id)
    return render_template('signalement_detail.html',
                          signalement=signalement,
                          current_user=current_user)

@app.route('/dashboard')
@login_required
def dashboard():
    user_signalements = Signalement.query.filter_by(user_id=current_user.id)\
                                        .order_by(Signalement.created_at.desc())\
                                        .all()
    return render_template('dashboard.html',
                          signalements=user_signalements,
                          current_user=current_user)

@app.route('/nouveau-signalement', methods=['GET', 'POST'])
@login_required
def nouveau_signalement():
    if request.method == 'POST':
        signalement = Signalement(
            type=request.form['type'],
            title=request.form['title'],
            description=request.form['description'],
            location=request.form['location'],
            date=datetime.strptime(request.form['date'], '%Y-%m-%d'),
            category=request.form.get('category'),
            contact=request.form.get('contact', current_user.email),
            reward=request.form.get('reward'),
            user_id=current_user.id,
            image_url=request.form.get('image_url')
        )
        db.session.add(signalement)
        db.session.commit()
        flash('Signalement créé avec succès !', 'success')
        return redirect(url_for('signalement_detail', id=signalement.id))
    
    return render_template('nouveau_signalement.html', current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # Logique de connexion simplifiée
        user = User.query.filter_by(email=request.form['email']).first()
        if user and user.password == request.form['password']:  # En production, utiliser hash
            login_user(user)
            flash('Connexion réussie !', 'success')
            return redirect(url_for('dashboard'))
        flash('Email ou mot de passe incorrect', 'error')
    
    return render_template('login.html', current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # Vérifier si l'utilisateur existe déjà
        if User.query.filter_by(email=request.form['email']).first():
            flash('Cet email est déjà utilisé', 'error')
            return redirect(url_for('register'))
        
        if User.query.filter_by(username=request.form['username']).first():
            flash('Ce nom d\'utilisateur est déjà pris', 'error')
            return redirect(url_for('register'))
        
        # Création d'utilisateur simplifiée
        user = User(
            username=request.form['username'],
            email=request.form['email'],
            password=request.form['password']  # En production, hash le mot de passe
        )
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Compte créé avec succès !', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('register.html', current_user=current_user)

@app.route('/profile')
@login_required
def profile():
    return render_template('profile.html', 
                          current_user=current_user,
                          now=datetime.utcnow())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('index'))

# API Routes
@app.route('/api/signalements', methods=['GET'])
def api_get_signalements():
    signalements = Signalement.query.filter_by(status='active').all()
    return jsonify([{
        'id': s.id,
        'type': s.type,
        'title': s.title,
        'description': s.description,
        'location': s.location,
        'date': s.date.isoformat(),
        'category': s.category,
        'reward': s.reward,
        'image_url': s.image_url,
        'author': s.author.username if s.author else 'Anonyme'
    } for s in signalements])

@app.route('/api/signalements', methods=['POST'])
@login_required
def api_create_signalement():
    data = request.json
    signalement = Signalement(
        type=data['type'],
        title=data['title'],
        description=data['description'],
        location=data['location'],
        date=datetime.fromisoformat(data['date']),
        category=data.get('category'),
        contact=data.get('contact', current_user.email),
        reward=data.get('reward'),
        user_id=current_user.id
    )
    db.session.add(signalement)
    db.session.commit()
    return jsonify({'message': 'Signalement créé', 'id': signalement.id}), 201

@app.route('/api/stats')
def api_stats():
    return jsonify({
        'total_signalements': Signalement.query.count(),
        'active_signalements': Signalement.query.filter_by(status='active').count(),
        'found_items': Signalement.query.filter_by(status='found').count(),
        'total_users': User.query.count()
    })

@app.route('/api/signalements/<int:id>/found', methods=['PUT'])
@login_required
def api_mark_as_found(id):
    signalement = Signalement.query.get_or_404(id)
    
    # Vérifier que l'utilisateur est le propriétaire
    if signalement.user_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    signalement.status = 'found'
    db.session.commit()
    return jsonify({'message': 'Signalement marqué comme retrouvé'})

# Page 404 personnalisée
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Page 500 personnalisée
@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Créer un favicon
@app.route('/favicon.ico')
def favicon():
    return '', 404  # Temporairement désactivé

if __name__ == '__main__':
    # Initialiser la base de données
    init_db()
    
    # Lancer l'application
    print("🚀 SignalAlert démarré sur http://localhost:5000")
    print("👤 Connectez-vous avec : admin@signalalert.bj / admin123")
    app.run(debug=True, host='0.0.0.0', port=5000)