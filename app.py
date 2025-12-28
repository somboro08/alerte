from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, send_from_directory, send_file
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from datetime import datetime, timedelta
import os
import secrets
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from werkzeug.security import generate_password_hash, check_password_hash
import qrcode
from PIL import Image
from PIL import Image as PILImage # Alias to avoid conflict with `Image` module name
import io

from werkzeug.utils import secure_filename
import uuid
from flask_wtf.csrf import generate_csrf # New import for CSRF token

app = Flask(__name__, 
            static_folder='static',
            template_folder='templates',
            static_url_path='/static')

# Dans app.py, après l'initialisation de Flask
def nl2br(value):
    """Convertit les retours à la ligne en balises <br>"""
    if value:
        return value.replace('\n', '<br>')
    return value

# Ajoutez le filtre à Jinja
app.jinja_env.filters['nl2br'] = nl2br

def resize_and_save_image(image_stream, max_long_side, save_path, quality=85):
    """
    Redimensionne et compresse une image.
    :param image_stream: Le flux du fichier image (ex: request.files['image']).
    :param max_long_side: La longueur maximale souhaitée pour le côté le plus long de l'image.
    :param save_path: Le chemin complet où sauvegarder l'image.
    :param quality: La qualité de compression pour les images JPEG (0-100).
    :return: True si l'opération réussit, False sinon.
    """
    try:
        img = PILImage.open(image_stream)
        
        # Redimensionner l'image si nécessaire
        width, height = img.size
        if max(width, height) > max_long_side:
            if width > height:
                new_width = max_long_side
                new_height = int(max_long_side * height / width)
            else:
                new_height = max_long_side
                new_width = int(max_long_side * width / height)
            img = img.resize((new_width, new_height), PILImage.LANCZOS)
        
        # Sauvegarder l'image en optimisant
        img.save(save_path, optimize=True, quality=quality)
        return True
    except Exception as e:
        print(f"Erreur lors du redimensionnement et de la sauvegarde de l'image: {e}")
        return False

# Configuration for file uploads
UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'images')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure the upload folder exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration: Use PostgreSQL on Render if DATABASE_URL is set, otherwise use SQLite
database_url = os.environ.get('DATABASE_URL')
if database_url:
    # Adapt for pg8000 driver if necessary (Render uses pg8000 by default)
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+pg8000://", 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    print(f"DEBUG: Using PostgreSQL database from DATABASE_URL: {database_url}")
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///signalalert.db'
    print("DEBUG: Using SQLite database.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_ENABLED'] = True
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME', '')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD', '')
app.config['MAIL_DEFAULT_SENDER'] = 'support@signalalert.bj'
app.config['RESET_TOKEN_EXPIRATION'] = 3600

db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'


# Modèles
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    signalements = db.relationship('Signalement', backref='author', lazy=True)
    comments = db.relationship('Comment', backref='author', lazy=True)
    reset_tokens = db.relationship('PasswordResetToken', backref='user', lazy=True, cascade='all, delete-orphan')
    notifications = db.relationship('Notification', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

class PasswordResetToken(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(100), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    used = db.Column(db.Boolean, default=False)
    
    def is_valid(self):
        return not self.used and datetime.utcnow() < self.expires_at

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
    qr_code_url = db.Column(db.String(500), nullable=True) # New column for QR code
    
    # New columns for advanced details
    lat = db.Column(db.Float, nullable=True)
    lng = db.Column(db.Float, nullable=True)
    views = db.Column(db.Integer, default=0)
    identification = db.Column(db.String(255), nullable=True)
    additional_info = db.Column(db.Text, nullable=True)
    phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(120), nullable=True) # Assuming this is separate from 'contact'
    
    comments = db.relationship('Comment', backref='signalement', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    signalement_id = db.Column(db.Integer, db.ForeignKey('signalement.id'), nullable=False)

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    is_read = db.Column(db.Boolean, default=False)
    link = db.Column(db.String(255))
db = SQLAlchemy(app)

# ⬇⬇⬇⬇⬇⬇⬇⬇⬇ AJOUTEZ CE CODE ICI ⬇⬇⬇⬇⬇⬇⬇⬇⬇
# Initialisation automatique de la base de données au démarrage
with app.app_context():
    try:
        # Créer toutes les tables si elles n'existent pas
        db.create_all()
        print("✅ Tables de la base de données créées avec succès !")
        
        # Créer l'utilisateur admin par défaut si nécessaire
        if not User.query.filter_by(email='admin@signalalert.bj').first():
            admin = User(
                username='admin',
                email='admin@signalalert.bj',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Utilisateur admin créé avec succès")
    except Exception as e:
        print(f"⚠️  Note lors de l'initialisation de la base de données: {e}")
        # Ne pas lever l'exception pour ne pas bloquer le démarrage
# ⬆⬆⬆⬆⬆⬆⬆⬆⬆ FIN DU CODE À AJOUTER ⬆⬆⬆⬆⬆⬆⬆⬆⬆

login_manager = LoginManager(app)
login_manager.login_view = 'login'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Fonctions utilitaires
def send_reset_email(user, token):
    """Envoie un email de réinitialisation"""
    if not app.config['MAIL_ENABLED']:
        print(f"[DEV] Email de réinitialisation pour {user.email}")
        print(f"[DEV] Lien: http://localhost:5000/reset-password/{token}")
        return True
    
    try:
        reset_url = f"http://localhost:5000/reset-password/{token}"
        
        msg = MIMEMultipart('alternative')
        msg['Subject'] = 'Réinitialisation de votre mot de passe - SignalAlert'
        msg['From'] = app.config['MAIL_DEFAULT_SENDER']
        msg['To'] = user.email
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <body>
            <h1>Réinitialisation de mot de passe</h1>
            <p>Bonjour {user.username},</p>
            <p>Cliquez sur ce lien pour réinitialiser votre mot de passe :</p>
            <a href="{reset_url}">{reset_url}</a>
            <p>Ce lien expirera dans 1 heure.</p>
        </body>
        </html>
        """
        
        text = f"""
        Réinitialisation de mot de passe
        
        Bonjour {user.username},
        
        Cliquez sur ce lien pour réinitialiser votre mot de passe :
        {reset_url}
        
        Ce lien expirera dans 1 heure.
        """
        
        msg.attach(MIMEText(text, 'plain'))
        msg.attach(MIMEText(html, 'html'))
        
        with smtplib.SMTP(app.config['MAIL_SERVER'], app.config['MAIL_PORT']) as server:
            server.starttls()
            server.login(app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
            server.send_message(msg)
        
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

def create_reset_token(user):
    """Crée un token de réinitialisation"""
    PasswordResetToken.query.filter_by(user_id=user.id).delete()
    
    token = secrets.token_urlsafe(32)
    expires_at = datetime.utcnow() + timedelta(seconds=app.config['RESET_TOKEN_EXPIRATION'])
    
    reset_token = PasswordResetToken(
        token=token,
        user_id=user.id,
        expires_at=expires_at
    )
    
    db.session.add(reset_token)
    db.session.commit()
    
    return token

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_now():
    return {'now': datetime.utcnow()}

@app.context_processor
def inject_csrf_token():
    return dict(csrf_token=generate_csrf)

@app.context_processor
def inject_notifications():
    if current_user.is_authenticated:
        unread_count = Notification.query.filter_by(user_id=current_user.id, is_read=False).count()
        return dict(unread_notifications_count=unread_count)
    return dict(unread_notifications_count=0)

import io
import base64
from weasyprint import HTML

def generate_qrcode_for_signalement(signalement_id, url_for_qrcode):
    """
    Génère un QR code pour le signalement et le sauvegarde.
    :param signalement_id: L'ID du signalement.
    :param url_for_qrcode: L'URL que le QR code doit encoder.
    :return: Le chemin relatif de l'image QR code sauvegardée, ou None en cas d'échec.
    """
    try:
        # Créer le répertoire si inexistant
        qr_codes_dir = os.path.join(app.root_path, 'static', 'uploads', 'qr_codes')
        os.makedirs(qr_codes_dir, exist_ok=True)

        # Générer le QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(url_for_qrcode)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Chemin de sauvegarde
        filename = f"qrcode_signalement_{signalement_id}.png"
        filepath = os.path.join(qr_codes_dir, filename)
        img.save(filepath)

        # Retourner le chemin relatif
        return os.path.join('uploads', 'qr_codes', filename).replace('\\', '/')
    except Exception as e:
        print(f"Erreur lors de la génération du QR code pour le signalement {signalement_id}: {e}")
        return None

@app.route('/signalement/<int:id>/generer_pdf')
@login_required
def generer_signalement_pdf(id):
    """
    Génère une affiche PDF stylisée pour un signalement en utilisant WeasyPrint.
    """
    signalement = Signalement.query.get_or_404(id)
    
    # 1. Générer le QR Code en mémoire
    signalement_url = url_for('signalement_detail', id=signalement.id, _external=True)
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(signalement_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Encoder en Base64 pour l'intégrer dans le HTML
    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    qr_code_base64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
    
    # 2. Rendre le template HTML avec les données
    # Assurez-vous que les chemins vers les CSS sont absolus ou accessibles par WeasyPrint
    rendered_html = render_template('rapport_pdf.html', 
                                    signalement=signalement, 
                                    qr_code_base64=qr_code_base64)
    
    # 3. Générer le PDF avec WeasyPrint
    pdf = HTML(string=rendered_html, base_url=request.url_root).write_pdf()
    
    # 4. Retourner le PDF en tant que réponse
    return send_file(
        io.BytesIO(pdf),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f'signalement_{signalement.id}.pdf'
    )

# ROUTES PRINCIPALES

@app.route('/')
def index():
    signalements = Signalement.query.filter_by(status='active').order_by(Signalement.created_at.desc()).limit(6).all()
    
    stats = {
        'total_signalements': Signalement.query.count(),
        'found_items': Signalement.query.filter_by(status='found').count(),
        'total_users': User.query.count(),
    }
    
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
    category_filter = request.args.get('category', '')
    status_filter = request.args.get('status', '')
    start_date_filter = request.args.get('start_date', '')
    end_date_filter = request.args.get('end_date', '')
    
    query = Signalement.query
    
    if type_filter:
        query = query.filter_by(type=type_filter)
    
    if search:
        query = query.filter(Signalement.title.contains(search) | Signalement.description.contains(search))

    if category_filter:
        query = query.filter_by(category=category_filter)

    if status_filter:
        query = query.filter_by(status=status_filter)
    
    if start_date_filter:
        try:
            start_date = datetime.strptime(start_date_filter, '%Y-%m-%d')
            query = query.filter(Signalement.date >= start_date)
        except ValueError:
            flash('Format de date de début invalide.', 'error')

    if end_date_filter:
        try:
            end_date = datetime.strptime(end_date_filter, '%Y-%m-%d')
            query = query.filter(Signalement.date <= end_date)
        except ValueError:
            flash('Format de date de fin invalide.', 'error')
    
    signalements = query.order_by(Signalement.created_at.desc())\
                       .paginate(page=page, per_page=12, error_out=False)
    
    return render_template('signalements.html',
                          signalements=signalements,
                          current_filter=type_filter,
                          search_query=search,
                          category_query=category_filter,
                          status_query=status_filter,
                          start_date_query=start_date_filter,
                          end_date_query=end_date_filter,
                          current_user=current_user)

@app.route('/map')
def map_view():
    return render_template('map.html', current_user=current_user)

@app.route('/signalement/<int:id>')
def signalement_detail(id):
    signalement = Signalement.query.get_or_404(id)
    comments = Comment.query.filter_by(signalement_id=id).order_by(Comment.timestamp.desc()).all()
    return render_template('signalement_detail.html',
                          signalement=signalement,
                          comments=comments,
                          current_user=current_user)

@app.route('/signalement/<int:id>/comment', methods=['POST'])
@login_required
def add_comment(id):
    signalement = Signalement.query.get_or_404(id)
    comment_content = request.form.get('comment_content')

    if not comment_content:
        flash('Le commentaire ne peut pas être vide.', 'error')
        return redirect(url_for('signalement_detail', id=id))

    comment = Comment(
        content=comment_content,
        user_id=current_user.id,
        signalement_id=id
    )
    db.session.add(comment)

    # Notifier le propriétaire du signalement, sauf s'il commente son propre post
    if signalement.author.id != current_user.id:
        notification = Notification(
            name=f"{current_user.username} a commenté votre signalement : \"{signalement.title}\"",
            user_id=signalement.author.id,
            link=url_for('signalement_detail', id=id)
        )
        db.session.add(notification)

    db.session.commit()

    flash('Votre commentaire a été ajouté.', 'success')
    return redirect(url_for('signalement_detail', id=id))

@app.route('/notifications')
@login_required
def notifications():
    notifications = Notification.query.filter_by(user_id=current_user.id).order_by(Notification.timestamp.desc()).all()
    # Marquer les notifications comme lues
    for notification in notifications:
        notification.is_read = True
    db.session.commit()
    return render_template('notifications.html', notifications=notifications)

@app.route('/politique-de-confidentialite')
def politique_de_confidentialite():
    return render_template('politique_de_confidentialite.html')

@app.route('/mentions-legales')
def mentions_legales():
    return render_template('mentions_legales.html')

@app.route('/conditions-d-utilisation')
def conditions_d_utilisation():
    return render_template('conditions_d_utilisation.html')



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
        image_url = None
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                
                # Redimensionner et sauvegarder l'image
                if resize_and_save_image(file, 800, file_path): # Max 800px on longest side
                    image_url = unique_filename # Store only the filename
                else:
                    flash('Erreur lors du traitement de l\'image.', 'error')
                    return redirect(request.url)
            elif file.filename != '': # If a file was submitted but not allowed
                flash('Type de fichier image non autorisé.', 'error')
                return redirect(request.url) # Redirect back to the form
        
        # Safely get lat and lng
        lat = request.form.get('lat')
        lng = request.form.get('lng')
        try:
            lat = float(lat) if lat else None
            lng = float(lng) if lng else None
        except (ValueError, TypeError):
            lat = None
            lng = None

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
            image_url=image_url, # Use the generated image_url
            lat=lat,
            lng=lng
        )
        db.session.add(signalement)
        db.session.commit() # Commit to get the signalement.id

        # Generate shareable URL for the signalement
        # We need to build the full URL, _external=True is necessary for sharing
        # In production, app.config['SERVER_NAME'] should be set to your domain
        signalement_url = url_for('signalement_detail', id=signalement.id, _external=True)
        print(f"DEBUG: Generated Signalement URL: {signalement_url}")

        # Generate and save the QR code
        qr_code_path = generate_qrcode_for_signalement(signalement.id, signalement_url)
        print(f"DEBUG: Generated QR Code Path: {qr_code_path}")

        if qr_code_path:
            signalement.qr_code_url = qr_code_path
            db.session.commit() # Commit the QR code path update

        flash('Signalement créé avec succès !', 'success')
        return redirect(url_for('signalement_detail', id=signalement.id))
    
    return render_template('nouveau_signalement.html', current_user=current_user)

@app.route('/signalement/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_signalement(id):
    signalement = Signalement.query.get_or_404(id)
    
    # Ensure only the author can edit
    if signalement.user_id != current_user.id:
        flash('Vous n\'êtes pas autorisé à modifier ce signalement.', 'error')
        return redirect(url_for('signalement_detail', id=signalement.id))

    if request.method == 'POST':
        # Handle image upload if a new one is provided
        image_url = signalement.image_url # Keep existing image if no new one uploaded
        if 'image' in request.files:
            file = request.files['image']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
                file.save(file_path)
                image_url = unique_filename
            elif file.filename != '':
                flash('Type de fichier image non autorisé.', 'error')
                return redirect(request.url)
        
        # Update signalement fields
        signalement.type = request.form['type']
        signalement.title = request.form['title']
        signalement.description = request.form['description']
        signalement.location = request.form['location']
        signalement.date = datetime.strptime(request.form['date'], '%Y-%m-%d')
        signalement.category = request.form.get('category')
        signalement.contact = request.form.get('contact', current_user.email)
        signalement.reward = request.form.get('reward')
        signalement.image_url = image_url # Update image_url
        
        # Update new fields (if present in form)
        signalement.lat = request.form.get('lat', type=float)
        signalement.lng = request.form.get('lng', type=float)
        signalement.identification = request.form.get('identification')
        signalement.additional_info = request.form.get('additional_info')
        signalement.phone = request.form.get('phone')
        signalement.email = request.form.get('email')

        # Re-generate QR code if data that affects the URL has changed (optional, but good practice)
        # For now, just re-generate it to ensure consistency if any detail changes.
        signalement_url = url_for('signalement_detail', id=signalement.id, _external=True)
        qr_code_path = generate_qrcode_for_signalement(signalement.id, signalement_url)
        if qr_code_path:
            signalement.qr_code_url = qr_code_path
        
        db.session.commit()
        flash('Signalement mis à jour avec succès !', 'success')
        return redirect(url_for('signalement_detail', id=signalement.id))
    
    # GET request: Render form with existing data
    return render_template('nouveau_signalement.html', 
                           signalement=signalement, # Pass signalement object for pre-filling
                           current_user=current_user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            if not user.is_active:
                flash('Votre compte est désactivé. Contactez l\'administrateur.', 'error')
            else:
                login_user(user)
                flash('Connexion réussie !', 'success')
                
                next_page = request.args.get('next')
                return redirect(next_page or url_for('dashboard'))
        else:
            flash('Email ou mot de passe incorrect', 'error')
    
    return render_template('login.html', current_user=current_user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        errors = []
        
        if not username or len(username) < 3:
            errors.append('Le nom d\'utilisateur doit contenir au moins 3 caractères')
        
        if not email or '@' not in email:
            errors.append('Adresse email invalide')
        
        if not password or len(password) < 8:
            errors.append('Le mot de passe doit contenir au moins 8 caractères')
        
        if User.query.filter_by(email=email).first():
            errors.append('Cet email est déjà utilisé')
        
        if User.query.filter_by(username=username).first():
            errors.append('Ce nom d\'utilisateur est déjà pris')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        else:
            user = User(
                username=username,
                email=email,
                is_active=True
            )
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            login_user(user)
            flash('Compte créé avec succès !', 'success')
            return redirect(url_for('dashboard'))
    
    return render_template('register.html', current_user=current_user)

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    # Ensure AVATAR_UPLOAD_FOLDER exists
    AVATAR_UPLOAD_FOLDER = os.path.join(app.root_path, 'static', 'uploads', 'avatars')
    os.makedirs(AVATAR_UPLOAD_FOLDER, exist_ok=True)
    app.config['AVATAR_UPLOAD_FOLDER'] = AVATAR_UPLOAD_FOLDER

    if request.method == 'POST':
        if 'avatar' in request.files:
            file = request.files['avatar']
            if file.filename == '':
                flash('Aucun fichier sélectionné pour l\'avatar.', 'warning')
            elif file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                unique_filename = str(uuid.uuid4()) + '_' + filename
                file_path = os.path.join(app.config['AVATAR_UPLOAD_FOLDER'], unique_filename)
                
                # Redimensionner et sauvegarder l'avatar
                if resize_and_save_image(file, 200, file_path): # Max 200px for avatar
                    current_user.avatar_url = unique_filename
                    db.session.commit()
                    flash('Votre photo de profil a été mise à jour !', 'success')
                else:
                    flash('Erreur lors du traitement de l\'image de profil.', 'error')
            else:
                flash('Type de fichier image non autorisé pour l\'avatar.', 'error')
        
        return redirect(url_for('profile'))

    user_signalements = Signalement.query.filter_by(user_id=current_user.id)\
                                        .order_by(Signalement.created_at.desc())\
                                        .all()
    user_comments = Comment.query.filter_by(user_id=current_user.id)\
                                 .order_by(Comment.timestamp.desc())\
                                 .all()
    
    return render_template('profile.html', 
                          current_user=current_user,
                          user_signalements=user_signalements,
                          user_comments=user_comments,
                          now=datetime.utcnow())

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Vous avez été déconnecté', 'info')
    return redirect(url_for('index'))

# ROUTES DE RÉINITIALISATION DE MOT DE PASSE

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        
        if not email:
            flash('Veuillez entrer votre adresse email', 'error')
            return render_template('forgot_password.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user:
            token = create_reset_token(user)
            
            if send_reset_email(user, token):
                flash('Un email de réinitialisation a été envoyé. Vérifiez votre boîte de réception.', 'success')
            else:
                flash('Erreur lors de l\'envoi de l\'email. Contactez l\'administrateur.', 'error')
        else:
            flash('Si votre email existe dans notre système, vous recevrez un lien de réinitialisation.', 'info')
        
        return redirect(url_for('login'))
    
    return render_template('forgot_password.html')

@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    # Retrieve the reset token from the database
    reset_token = PasswordResetToken.query.filter_by(token=token).first()
    
    if not reset_token or not reset_token.is_valid():
        flash('Le lien de réinitialisation est invalide ou a expiré.', 'error')
        return redirect(url_for('forgot_password'))
    
    user = reset_token.user
    
    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not password or not confirm_password:
            flash('Veuillez remplir tous les champs', 'error')
        elif len(password) < 8:
            flash('Le mot de passe doit contenir au moins 8 caractères', 'error')
        elif password != confirm_password:
            flash('Les mots de passe ne correspondent pas', 'error')
        else:
            user.set_password(password)
            reset_token.used = True
            PasswordResetToken.query.filter_by(user_id=user.id).delete()
            
            db.session.commit()
            
            flash('Votre mot de passe a été réinitialisé avec succès. Vous pouvez maintenant vous connecter.', 'success')
            return redirect(url_for('login'))
    
    return render_template('reset_password.html', token=token, user=user)

@app.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        if not current_user.check_password(current_password):
            flash('Mot de passe actuel incorrect', 'error')
        elif len(new_password) < 8:
            flash('Le nouveau mot de passe doit contenir au moins 8 caractères', 'error')
        elif new_password != confirm_password:
            flash('Les nouveaux mots de passe ne correspondent pas', 'error')
        elif current_password == new_password:
            flash('Le nouveau mot de passe doit être différent de l\'ancien', 'error')
        else:
            current_user.set_password(new_password)
            db.session.commit()
            
            flash('Votre mot de passe a été modifié avec succès', 'success')
            return redirect(url_for('profile'))
    
    return render_template('change_password.html')

# API ROUTES

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

@app.route('/api/signalements/locations')
def api_get_signalement_locations():
    signalements_with_location = Signalement.query.filter(
        Signalement.lat.isnot(None),
        Signalement.lng.isnot(None)
    ).all()
    
    locations = [{
        'id': s.id,
        'title': s.title,
        'type': s.type,
        'lat': s.lat,
        'lng': s.lng
    } for s in signalements_with_location]
    
    return jsonify(locations)

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
    
    if signalement.user_id != current_user.id:
        return jsonify({'error': 'Non autorisé'}), 403
    
    signalement.status = 'found'
    db.session.commit()
    return jsonify({'message': 'Signalement marqué comme retrouvé'})

# ROUTES ADMIN

@app.route('/admin/donnees')
@login_required
def admin_donnees():
    if current_user.email != 'admin@signalalert.bj':
        return "Accès non autorisé", 403
    
    users = User.query.all()
    signalements = Signalement.query.all()
    all_comments = Comment.query.order_by(Comment.timestamp.desc()).all()
    
    return render_template('admin_donnees.html',
                          users=users,
                          signalements=signalements,
                          all_comments=all_comments,
                          current_user=current_user)

@app.route('/admin/user/<int:user_id>/toggle_active', methods=['POST'])
@login_required
def admin_toggle_user_active(user_id):
    if current_user.email != 'admin@signalalert.bj':
        flash("Accès non autorisé.", "error")
        return redirect(url_for('index'))
    
    user = User.query.get_or_404(user_id)
    if user.email == 'admin@signalalert.bj': # Prevent deactivating the main admin
        flash("Vous ne pouvez pas désactiver le compte administrateur principal.", "error")
        return redirect(url_for('admin_donnees'))

    user.is_active = not user.is_active
    db.session.commit()
    flash(f"L'utilisateur {user.username} a été {'activé' if user.is_active else 'désactivé'}.", "success")
    return redirect(url_for('admin_donnees'))

@app.route('/admin/signalement/<int:signalement_id>/delete', methods=['POST'])
@login_required
def admin_delete_signalement(signalement_id):
    if current_user.email != 'admin@signalalert.bj':
        flash("Accès non autorisé.", "error")
        return redirect(url_for('index'))
    
    signalement = Signalement.query.get_or_404(signalement_id)
    db.session.delete(signalement)
    db.session.commit()
    flash(f"Le signalement '{signalement.title}' a été supprimé.", "success")
    return redirect(url_for('admin_donnees'))

@app.route('/admin/comment/<int:comment_id>/delete', methods=['POST'])
@login_required
def admin_delete_comment(comment_id):
    if current_user.email != 'admin@signalalert.bj':
        flash("Accès non autorisé.", "error")
        return redirect(url_for('index'))
    
    comment = Comment.query.get_or_404(comment_id)
    db.session.delete(comment)
    db.session.commit()
    flash(f"Le commentaire (ID: {comment.id}) a été supprimé.", "success")
    return redirect(url_for('admin_donnees'))

# ROUTES UTILITAIRES

@app.route('/cleanup-tokens')
def cleanup_tokens():
    expired_tokens = PasswordResetToken.query.filter(
        PasswordResetToken.expires_at < datetime.utcnow()
    ).all()
    
    for token in expired_tokens:
        db.session.delete(token)
    
    db.session.commit()
    
    return f"{len(expired_tokens)} tokens expirés nettoyés"

# ROUTES D'ERREUR

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# ROUTE STATIQUE POUR FAVICON

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'images'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')

# INITIALISATION

def init_db():
    with app.app_context():
        db.create_all()
        
        if not User.query.filter_by(email='admin@signalalert.bj').first():
            admin = User(
                username='admin',
                email='admin@signalalert.bj',
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Base de données initialisée avec l'utilisateur admin")

if __name__ == '__main__':
    init_db()
    
    # # Commented out for production deployment with Gunicorn
    # print("🚀 SignalAlert démarré sur http://localhost:5000")
    # print("👤 Admin: admin@signalalert.bj / admin123")
    # print("📁 Static folder:", app.static_folder)
    # print("📁 Template folder:", app.template_folder)
    # app.run(debug=True, host='0.0.0.0', port=5000)