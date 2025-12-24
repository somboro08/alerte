Pour ajouter une fonctionnalité de recherche de visage par photo, voici comment procéder :

## Architecture recommandée

### 1. **Stack technologique suggérée**

```
Python + Flask
↓
OpenCV / face_recognition (pour la reconnaissance faciale)
↓
SQLite/PostgreSQL (stockage des encodages faciaux)
↓
HTML/CSS/JavaScript (interface utilisateur)
```

### 2. **Installation des dépendances**

```bash
# Installation des packages nécessaires
pip install opencv-python
pip install face_recognition  # Facile à utiliser mais lourde
pip install numpy
pip install pillow

# Ou pour une solution plus légère :
pip install deepface  # Alternative avec plusieurs modèles
pip install mtcnn     # Détection de visages
```

## Implémentation étape par étape

### **Étape 1 : Modèles de base de données**

```python
# Dans vos modèles (app.py ou models.py)

from flask_sqlalchemy import SQLAlchemy
import numpy as np
import pickle
import base64

db = SQLAlchemy()

class FaceEncoding(db.Model):
    __tablename__ = 'face_encodings'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    signalement_id = db.Column(db.Integer, db.ForeignKey('signalement.id'))
    
    # Stocker l'encodage facial sous forme binaire
    encoding = db.Column(db.LargeBinary)
    
    # Métadonnées
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relations
    user = db.relationship('User', backref='face_encodings')
    signalement = db.relationship('Signalement', backref='face_encoding')

class FaceMatch(db.Model):
    __tablename__ = 'face_matches'
    
    id = db.Column(db.Integer, primary_key=True)
    search_id = db.Column(db.String(100))  # ID unique pour chaque recherche
    original_signalement_id = db.Column(db.Integer)
    matched_signalement_id = db.Column(db.Integer)
    confidence = db.Column(db.Float)  # Score de similarité (0-1)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Index pour performances
    __table_args__ = (
        db.Index('idx_search_id', 'search_id'),
        db.Index('idx_confidence', 'confidence'),
    )
```

### **Étape 2 : Service de reconnaissance faciale**

```python
# Créez un fichier facial_recognition.py

import cv2
import numpy as np
import face_recognition
from PIL import Image
import io
import os
from typing import List, Tuple, Optional

class FacialRecognitionService:
    def __init__(self, model='hog'):
        """
        Initialise le service de reconnaissance faciale
        model: 'hog' (plus rapide) ou 'cnn' (plus précis)
        """
        self.model = model
        self.known_encodings = {}
        self.known_metadata = {}
        
    def load_known_faces(self):
        """Charge tous les visages connus depuis la base de données"""
        from app import db, FaceEncoding
        
        face_encodings = FaceEncoding.query.filter_by(is_active=True).all()
        
        for fe in face_encodings:
            # Convertir le binaire en numpy array
            encoding = pickle.loads(fe.encoding)
            self.known_encodings[fe.id] = encoding
            self.known_metadata[fe.id] = {
                'user_id': fe.user_id,
                'signalement_id': fe.signalement_id
            }
        
        return len(self.known_encodings)
    
    def encode_face(self, image_data) -> Optional[List[np.ndarray]]:
        """
        Encode un visage à partir d'une image
        
        Args:
            image_data: bytes, file path, ou numpy array
            
        Returns:
            List d'encodages faciaux ou None
        """
        try:
            # Charger l'image
            if isinstance(image_data, bytes):
                image = face_recognition.load_image_file(io.BytesIO(image_data))
            elif isinstance(image_data, str):
                image = face_recognition.load_image_file(image_data)
            elif isinstance(image_data, np.ndarray):
                image = image_data
            else:
                raise ValueError("Format d'image non supporté")
            
            # Détecter les visages
            face_locations = face_recognition.face_locations(image, model=self.model)
            
            if not face_locations:
                return None
            
            # Encoder chaque visage détecté
            face_encodings = face_recognition.face_encodings(image, face_locations)
            
            return face_encodings
            
        except Exception as e:
            print(f"Erreur lors de l'encodage: {e}")
            return None
    
    def compare_faces(self, unknown_encoding: np.ndarray, 
                     tolerance: float = 0.6) -> List[Tuple[int, float]]:
        """
        Compare un encodage facial avec la base de données
        
        Returns:
            List de tuples (face_id, confidence)
        """
        matches = []
        
        if not self.known_encodings:
            self.load_known_faces()
        
        for face_id, known_encoding in self.known_encodings.items():
            # Calculer la distance entre les encodages
            distance = face_recognition.face_distance([known_encoding], unknown_encoding)[0]
            
            # Convertir distance en score de confiance
            confidence = max(0, 1 - distance / tolerance)
            
            if confidence > 0.7:  # Seuil minimum
                matches.append((face_id, confidence))
        
        # Trier par confiance décroissante
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def search_similar_faces(self, image_data, max_results: int = 10):
        """
        Recherche des visages similaires dans la base
        """
        # Encoder l'image d'entrée
        encodings = self.encode_face(image_data)
        
        if not encodings:
            return {"error": "Aucun visage détecté", "matches": []}
        
        all_matches = []
        
        # Comparer chaque visage détecté
        for encoding in encodings:
            matches = self.compare_faces(encoding)
            all_matches.extend(matches)
        
        # Trier et limiter les résultats
        all_matches.sort(key=lambda x: x[1], reverse=True)
        top_matches = all_matches[:max_results]
        
        # Formater les résultats
        results = []
        for face_id, confidence in top_matches:
            metadata = self.known_metadata.get(face_id, {})
            results.append({
                'face_id': face_id,
                'signalement_id': metadata.get('signalement_id'),
                'user_id': metadata.get('user_id'),
                'confidence': round(confidence * 100, 2),  # Pourcentage
                'match_level': self._get_match_level(confidence)
            })
        
        return {
            "total_faces_detected": len(encodings),
            "matches_found": len(results),
            "matches": results
        }
    
    def _get_match_level(self, confidence: float) -> str:
        """Convertit le score en niveau textuel"""
        if confidence >= 0.9:
            return "Correspondance forte"
        elif confidence >= 0.8:
            return "Correspondance probable"
        elif confidence >= 0.7:
            return "Ressemblance possible"
        else:
            return "Faible ressemblance"
    
    def save_face_encoding(self, signalement_id: int, image_data) -> bool:
        """
        Sauvegarde un encodage facial pour un signalement
        """
        from app import db, FaceEncoding, Signalement
        
        try:
            # Vérifier si le signalement existe
            signalement = Signalement.query.get(signalement_id)
            if not signalement:
                return False
            
            # Encoder le visage
            encodings = self.encode_face(image_data)
            if not encodings:
                return False
            
            # Prendre le premier visage détecté (le plus grand/central)
            main_encoding = encodings[0]
            
            # Sauvegarder dans la base
            face_encoding = FaceEncoding(
                signalement_id=signalement_id,
                user_id=signalement.user_id,
                encoding=pickle.dumps(main_encoding)
            )
            
            db.session.add(face_encoding)
            db.session.commit()
            
            # Mettre à jour le cache
            self.known_encodings[face_encoding.id] = main_encoding
            self.known_metadata[face_encoding.id] = {
                'user_id': signalement.user_id,
                'signalement_id': signalement_id
            }
            
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la sauvegarde: {e}")
            return False

# Instance globale
face_service = FacialRecognitionService()
```

### **Étape 3 : Routes Flask**

```python
# Ajoutez ces routes à votre app.py

import uuid
from werkzeug.utils import secure_filename
from PIL import Image

# Configuration
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
UPLOAD_FOLDER = 'static/uploads/face_search'
MAX_FILE_SIZE = 16 * 1024 * 1024  # 16MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_image(image_file):
    """Valide l'image avant traitement"""
    try:
        img = Image.open(image_file)
        img.verify()
        image_file.seek(0)
        
        # Vérifier la taille
        if img.size[0] * img.size[1] > 4000 * 4000:
            return False, "Image trop grande"
            
        return True, "OK"
    except Exception as e:
        return False, f"Image invalide: {str(e)}"

@app.route('/recherche-visage', methods=['GET', 'POST'])
def recherche_visage():
    """Page de recherche par visage"""
    if request.method == 'POST':
        # Vérifier si un fichier a été envoyé
        if 'face_image' not in request.files:
            flash('Aucune image sélectionnée', 'error')
            return redirect(request.url)
        
        file = request.files['face_image']
        
        # Vérifier si un fichier a été sélectionné
        if file.filename == '':
            flash('Aucune image sélectionnée', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            try:
                # Valider l'image
                is_valid, message = validate_image(file)
                if not is_valid:
                    flash(message, 'error')
                    return redirect(request.url)
                
                # Lire l'image
                file.seek(0)
                image_data = file.read()
                
                # Générer un ID de recherche
                search_id = str(uuid.uuid4())
                
                # Sauvegarder l'image temporairement
                filename = f"{search_id}_{secure_filename(file.filename)}"
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                file.seek(0)
                file.save(file_path)
                
                # Rechercher des correspondances
                results = face_service.search_similar_faces(image_data, max_results=20)
                
                if results.get('error'):
                    flash(results['error'], 'warning')
                    return redirect(request.url)
                
                # Récupérer les détails des signalements correspondants
                matches_with_details = []
                for match in results['matches']:
                    signalement = Signalement.query.get(match['signalement_id'])
                    if signalement:
                        match_details = {
                            'signalement': signalement,
                            'confidence': match['confidence'],
                            'match_level': match['match_level']
                        }
                        matches_with_details.append(match_details)
                
                return render_template('recherche_visage.html',
                                     results=matches_with_details,
                                     search_id=search_id,
                                     image_url=f"/{file_path}",
                                     total_found=len(matches_with_details))
                
            except Exception as e:
                flash(f"Erreur lors du traitement: {str(e)}", 'error')
                return redirect(request.url)
        
        else:
            flash('Format de fichier non supporté', 'error')
            return redirect(request.url)
    
    return render_template('recherche_visage.html')

@app.route('/api/search-face', methods=['POST'])
def api_search_face():
    """API pour la recherche de visage"""
    if 'image' not in request.files:
        return jsonify({'error': 'No image provided'}), 400
    
    file = request.files['image']
    
    if file.filename == '':
        return jsonify({'error': 'No image selected'}), 400
    
    if file and allowed_file(file.filename):
        try:
            image_data = file.read()
            results = face_service.search_similar_faces(image_data)
            
            # Ajouter les URLs des signalements
            for match in results['matches']:
                signalement = Signalement.query.get(match['signalement_id'])
                if signalement:
                    match['signalement_url'] = url_for('signalement_detail', 
                                                      id=signalement.id, 
                                                      _external=True)
                    match['title'] = signalement.title
                    match['type'] = signalement.type
                    match['location'] = signalement.location
            
            return jsonify(results)
            
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    return jsonify({'error': 'Invalid file format'}), 400

@app.route('/admin/face-encodings/update')
@login_required
def update_face_encodings():
    """Met à jour tous les encodages faciaux"""
    if not current_user.is_admin:
        abort(403)
    
    signalements = Signalement.query.filter_by(type='missing').all()
    updated = 0
    failed = 0
    
    for signalement in signalements:
        if signalement.image_url:
            image_path = f"static/uploads/images/{signalement.image_url}"
            if os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                
                if face_service.save_face_encoding(signalement.id, image_data):
                    updated += 1
                else:
                    failed += 1
    
    flash(f"{updated} encodages mis à jour, {failed} échecs", 'info')
    return redirect(url_for('admin_dashboard'))
```

### **Étape 4 : Template HTML**

```html
<!-- templates/recherche_visage.html -->
{% extends "base.html" %}

{% block title %}Recherche par visage - SignalAlert{% endblock %}

{% block head_extra %}
<style>
    .search-container {
        max-width: 1000px;
        margin: 2rem auto;
        padding: 2rem;
    }
    
    .upload-area {
        border: 3px dashed var(--primary-color);
        border-radius: 20px;
        padding: 3rem;
        text-align: center;
        background: rgba(255, 140, 60, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
        margin-bottom: 2rem;
    }
    
    .upload-area:hover {
        background: rgba(255, 140, 60, 0.1);
        border-color: var(--secondary-color);
        transform: translateY(-5px);
    }
    
    .upload-area.drag-over {
        background: rgba(255, 140, 60, 0.2);
        border-color: var(--secondary-color);
    }
    
    .upload-icon {
        font-size: 4rem;
        color: var(--primary-color);
        margin-bottom: 1rem;
    }
    
    .preview-container {
        max-width: 400px;
        margin: 0 auto 2rem;
        position: relative;
    }
    
    .preview-image {
        width: 100%;
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
    }
    
    .results-container {
        margin-top: 3rem;
    }
    
    .match-card {
        display: flex;
        gap: 2rem;
        padding: 1.5rem;
        background: white;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        box-shadow: 0 5px 20px rgba(0,0,0,0.08);
        border: 2px solid transparent;
        transition: all 0.3s ease;
    }
    
    .match-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 30px rgba(0,0,0,0.15);
    }
    
    .match-card.high-match {
        border-color: #2ecc71;
        border-left-width: 5px;
    }
    
    .match-card.medium-match {
        border-color: #f39c12;
        border-left-width: 5px;
    }
    
    .match-card.low-match {
        border-color: #e74c3c;
        border-left-width: 5px;
    }
    
    .confidence-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 50px;
        font-weight: bold;
        font-size: 0.9rem;
        margin-bottom: 0.5rem;
    }
    
    .confidence-high {
        background: #2ecc71;
        color: white;
    }
    
    .confidence-medium {
        background: #f39c12;
        color: white;
    }
    
    .confidence-low {
        background: #e74c3c;
        color: white;
    }
    
    .match-thumbnail {
        width: 150px;
        height: 150px;
        object-fit: cover;
        border-radius: 10px;
        flex-shrink: 0;
    }
    
    .match-details {
        flex: 1;
    }
    
    .match-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 1rem;
    }
    
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(255, 255, 255, 0.9);
        display: none;
        justify-content: center;
        align-items: center;
        z-index: 1000;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 5px solid #f3f3f3;
        border-top: 5px solid var(--primary-color);
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    .requirements {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 1.5rem;
        margin-top: 2rem;
    }
    
    .requirements ul {
        margin: 0;
        padding-left: 1.5rem;
    }
    
    .requirements li {
        margin-bottom: 0.5rem;
    }
    
    .webcam-container {
        margin: 2rem 0;
        text-align: center;
    }
    
    #video {
        width: 100%;
        max-width: 500px;
        border-radius: 10px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.1);
    }
    
    .webcam-controls {
        margin-top: 1rem;
    }
    
    @media (max-width: 768px) {
        .match-card {
            flex-direction: column;
            gap: 1rem;
        }
        
        .match-thumbnail {
            width: 100%;
            height: 200px;
        }
        
        .upload-area {
            padding: 2rem 1rem;
        }
    }
</style>
{% endblock %}

{% block content %}
<div class="container search-container">
    <h1 class="text-center mb-4">
        <i class="fas fa-search"></i> Recherche par visage
    </h1>
    
    <p class="text-center text-muted mb-5">
        Recherchez une personne disparue en comparant une photo avec notre base de données
    </p>
    
    <!-- Zone de dépôt d'image -->
    <div class="upload-area" id="dropZone">
        <div class="upload-icon">
            <i class="fas fa-cloud-upload-alt"></i>
        </div>
        <h3>Déposez votre image ici</h3>
        <p class="text-muted">ou cliquez pour parcourir vos fichiers</p>
        <p class="small text-muted">
            Formats supportés : JPG, PNG, GIF | Max. 16MB
        </p>
        <input type="file" id="fileInput" accept="image/*" class="d-none">
        <button class="btn btn-primary mt-3" onclick="document.getElementById('fileInput').click()">
            <i class="fas fa-folder-open"></i> Choisir une image
        </button>
        
        <!-- Webcam option -->
        <div class="mt-4">
            <button class="btn btn-outline-primary" onclick="openWebcam()">
                <i class="fas fa-camera"></i> Prendre une photo
            </button>
        </div>
    </div>
    
    <!-- Webcam container (caché par défaut) -->
    <div class="webcam-container" id="webcamContainer" style="display: none;">
        <video id="video" autoplay></video>
        <div class="webcam-controls">
            <button class="btn btn-success" onclick="capturePhoto()">
                <i class="fas fa-camera"></i> Capturer
            </button>
            <button class="btn btn-outline-secondary" onclick="closeWebcam()">
                <i class="fas fa-times"></i> Annuler
            </button>
        </div>
    </div>
    
    <!-- Aperçu de l'image -->
    <div class="preview-container" id="previewContainer" style="display: none;">
        <img id="previewImage" class="preview-image" src="" alt="Aperçu">
        <button class="btn btn-sm btn-outline-danger mt-2" onclick="clearImage()">
            <i class="fas fa-times"></i> Supprimer
        </button>
    </div>
    
    <!-- Bouton de recherche -->
    <div class="text-center">
        <button class="btn btn-primary btn-lg" id="searchBtn" style="display: none;">
            <i class="fas fa-search"></i> Lancer la recherche
        </button>
    </div>
    
    <!-- Résultats -->
    <div class="results-container" id="resultsContainer" style="display: none;">
        <h2 class="mb-4">
            <i class="fas fa-chart-line"></i> Résultats de la recherche
            <small class="text-muted" id="resultsCount"></small>
        </h2>
        
        <div id="matchesList"></div>
        
        <div class="text-center mt-4">
            <button class="btn btn-outline-primary" onclick="newSearch()">
                <i class="fas fa-redo"></i> Nouvelle recherche
            </button>
        </div>
    </div>
    
    <!-- Exigences pour une bonne recherche -->
    <div class="requirements">
        <h5><i class="fas fa-lightbulb"></i> Pour de meilleurs résultats :</h5>
        <ul>
            <li>Utilisez une photo claire et nette du visage</li>
            <li>Le visage doit être bien éclairé et visible</li>
            <li>Évitez les photos de groupe ou les visages masqués</li>
            <li>Les photos de face donnent les meilleurs résultats</li>
            <li>Assurez-vous que le visage occupe au moins 30% de l'image</li>
        </ul>
    </div>
</div>

<!-- Overlay de chargement -->
<div class="loading-overlay" id="loadingOverlay">
    <div class="text-center">
        <div class="loading-spinner"></div>
        <h3 class="mt-3">Analyse en cours...</h3>
        <p class="text-muted">Veuillez patienter pendant la recherche</p>
    </div>
</div>

<!-- Template pour les résultats -->
<template id="matchTemplate">
    <div class="match-card {match_class}">
        <img src="{image_url}" alt="{title}" class="match-thumbnail">
        <div class="match-details">
            <div class="match-header">
                <div>
                    <span class="confidence-badge {confidence_class}">{confidence}%</span>
                    <h4 class="mb-1">{title}</h4>
                    <p class="text-muted mb-1">
                        <i class="fas fa-map-marker-alt"></i> {location}
                    </p>
                </div>
                <div>
                    <span class="badge badge-{type}">
                        {type_text}
                    </span>
                </div>
            </div>
            <p class="mb-2">{description}</p>
            <div class="d-flex justify-content-between align-items-center">
                <small class="text-muted">
                    <i class="fas fa-user"></i> Publié par {author}
                </small>
                <a href="{detail_url}" class="btn btn-primary btn-sm">
                    <i class="fas fa-eye"></i> Voir détails
                </a>
            </div>
        </div>
    </div>
</template>
{% endblock %}

{% block scripts %}
<script>
let selectedFile = null;
let stream = null;

// Initialisation
document.addEventListener('DOMContentLoaded', function() {
    const fileInput = document.getElementById('fileInput');
    const dropZone = document.getElementById('dropZone');
    const previewContainer = document.getElementById('previewContainer');
    const previewImage = document.getElementById('previewImage');
    const searchBtn = document.getElementById('searchBtn');
    
    // Gestion du drag & drop
    dropZone.addEventListener('dragover', function(e) {
        e.preventDefault();
        dropZone.classList.add('drag-over');
    });
    
    dropZone.addEventListener('dragleave', function() {
        dropZone.classList.remove('drag-over');
    });
    
    dropZone.addEventListener('drop', function(e) {
        e.preventDefault();
        dropZone.classList.remove('drag-over');
        
        const files = e.dataTransfer.files;
        if (files.length > 0) {
            handleFile(files[0]);
        }
    });
    
    // Gestion de la sélection de fichier
    fileInput.addEventListener('change', function(e) {
        if (this.files.length > 0) {
            handleFile(this.files[0]);
        }
    });
    
    // Bouton de recherche
    searchBtn.addEventListener('click', function() {
        performSearch();
    });
});

function handleFile(file) {
    // Vérifier la taille
    if (file.size > 16 * 1024 * 1024) {
        alert('Fichier trop volumineux (max 16MB)');
        return;
    }
    
    // Vérifier le type
    if (!file.type.match('image.*')) {
        alert('Veuillez sélectionner une image');
        return;
    }
    
    selectedFile = file;
    
    // Afficher l'aperçu
    const reader = new FileReader();
    reader.onload = function(e) {
        document.getElementById('previewImage').src = e.target.result;
        document.getElementById('previewContainer').style.display = 'block';
        document.getElementById('searchBtn').style.display = 'block';
        document.getElementById('dropZone').style.display = 'none';
    };
    reader.readAsDataURL(file);
}

// Webcam functions
async function openWebcam() {
    try {
        const constraints = {
            video: {
                width: { ideal: 1280 },
                height: { ideal: 720 },
                facingMode: 'user'
            }
        };
        
        stream = await navigator.mediaDevices.getUserMedia(constraints);
        const video = document.getElementById('video');
        video.srcObject = stream;
        
        document.getElementById('webcamContainer').style.display = 'block';
        document.getElementById('dropZone').style.display = 'none';
        
    } catch (err) {
        console.error('Erreur webcam:', err);
        alert('Impossible d\'accéder à la webcam');
    }
}

function capturePhoto() {
    const video = document.getElementById('video');
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    canvas.getContext('2d').drawImage(video, 0, 0);
    
    // Convertir en blob
    canvas.toBlob(function(blob) {
        selectedFile = new File([blob], 'webcam-photo.jpg', { type: 'image/jpeg' });
        
        // Afficher l'aperçu
        const previewUrl = URL.createObjectURL(blob);
        document.getElementById('previewImage').src = previewUrl;
        document.getElementById('previewContainer').style.display = 'block';
        document.getElementById('searchBtn').style.display = 'block';
        document.getElementById('webcamContainer').style.display = 'none';
        
        // Arrêter la webcam
        closeWebcam();
    }, 'image/jpeg', 0.95);
}

function closeWebcam() {
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    document.getElementById('webcamContainer').style.display = 'none';
    document.getElementById('dropZone').style.display = 'block';
}

function clearImage() {
    selectedFile = null;
    document.getElementById('previewContainer').style.display = 'none';
    document.getElementById('searchBtn').style.display = 'none';
    document.getElementById('dropZone').style.display = 'block';
    document.getElementById('fileInput').value = '';
}

async function performSearch() {
    if (!selectedFile) {
        alert('Veuillez sélectionner une image');
        return;
    }
    
    // Afficher le loading
    document.getElementById('loadingOverlay').style.display = 'flex';
    
    const formData = new FormData();
    formData.append('face_image', selectedFile);
    
    try {
        const response = await fetch('/recherche-visage', {
            method: 'POST',
            body: formData
        });
        
        if (response.ok) {
            // Recharger la page pour afficher les résultats
            window.location.reload();
        } else {
            const error = await response.text();
            throw new Error(error);
        }
    } catch (error) {
        console.error('Erreur:', error);
        alert('Erreur lors de la recherche: ' + error.message);
    } finally {
        document.getElementById('loadingOverlay').style.display = 'none';
    }
}

// Pour l'API (alternative AJAX)
async function performApiSearch() {
    if (!selectedFile) return;
    
    const formData = new FormData();
    formData.append('image', selectedFile);
    
    try {
        const response = await fetch('/api/search-face', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.error) {
            throw new Error(data.error);
        }
        
        displayResults(data);
        
    } catch (error) {
        console.error('Erreur API:', error);
        alert('Erreur: ' + error.message);
    }
}

function displayResults(data) {
    const container = document.getElementById('resultsContainer');
    const list = document.getElementById('matchesList');
    const count = document.getElementById('resultsCount');
    
    // Afficher le container
    container.style.display = 'block';
    
    // Mettre à jour le compteur
    count.textContent = ` (${data.matches_found} correspondances)`;
    
    // Effacer les anciens résultats
    list.innerHTML = '';
    
    if (data.matches.length === 0) {
        list.innerHTML = `
            <div class="text-center py-5">
                <i class="fas fa-search fa-3x text-muted mb-3"></i>
                <h4>Aucune correspondance trouvée</h4>
                <p class="text-muted">Essayez avec une autre photo</p>
            </div>
        `;
        return;
    }
    
    // Afficher les résultats
    data.matches.forEach(match => {
        const template = document.getElementById('matchTemplate').innerHTML;
        
        // Déterminer la classe CSS en fonction de la confiance
        let matchClass = '';
        let confidenceClass = '';
        
        if (match.confidence >= 80) {
            matchClass = 'high-match';
            confidenceClass = 'confidence-high';
        } else if (match.confidence >= 60) {
            matchClass = 'medium-match';
            confidenceClass = 'confidence-medium';
        } else {
            matchClass = 'low-match';
            confidenceClass = 'confidence-low';
        }
        
        // Remplir le template
        const html = template
            .replace('{match_class}', matchClass)
            .replace('{confidence_class}', confidenceClass)
            .replace('{confidence}', match.confidence)
            .replace('{title}', match.title || 'Signalement')
            .replace('{location}', match.location || 'Localisation inconnue')
            .replace('{type}', match.type || 'missing')
            .replace('{type_text}', getTypeText(match.type))
            .replace('{description}', match.description || '')
            .replace('{author}', 'Utilisateur')
            .replace('{detail_url}', match.signalement_url || '#')
            .replace('{image_url}', match.image_url || '/static/default-avatar.jpg');
        
        list.innerHTML += html;
    });
}

function getTypeText(type) {
    switch(type) {
        case 'missing': return 'Personne disparue';
        case 'lost': return 'Objet perdu';
        case 'theft': return 'Objet volé';
        default: return 'Signalement';
    }
}

function newSearch() {
    selectedFile = null;
    document.getElementById('resultsContainer').style.display = 'none';
    document.getElementById('previewContainer').style.display = 'none';
    document.getElementById('searchBtn').style.display = 'none';
    document.getElementById('dropZone').style.display = 'block';
    document.getElementById('fileInput').value = '';
}
</script>
{% endblock %}
```

### **Étape 5 : Script de batch pour indexer les images existantes**

```python
# create_batch_index.py

import os
from app import app, db, Signalement, FaceEncoding
from facial_recognition import face_service

def batch_index_existing_images():
    """Indexe toutes les images existantes dans la base"""
    with app.app_context():
        # Récupérer tous les signalements de personnes disparues avec image
        signalements = Signalement.query.filter_by(type='missing').all()
        
        print(f"Indexage de {len(signalements)} signalements...")
        
        indexed = 0
        skipped = 0
        errors = 0
        
        for signalement in signalements:
            if signalement.image_url:
                image_path = os.path.join('static/uploads/images', signalement.image_url)
                
                if os.path.exists(image_path):
                    try:
                        with open(image_path, 'rb') as f:
                            image_data = f.read()
                        
                        # Vérifier si déjà indexé
                        existing = FaceEncoding.query.filter_by(
                            signalement_id=signalement.id
                        ).first()
                        
                        if not existing:
                            success = face_service.save_face_encoding(
                                signalement.id, 
                                image_data
                            )
                            
                            if success:
                                indexed += 1
                                print(f"✓ Indexé: {signalement.title}")
                            else:
                                errors += 1
                                print(f"✗ Erreur d'encodage: {signalement.title}")
                        else:
                            skipped += 1
                            print(f"- Déjà indexé: {signalement.title}")
                            
                    except Exception as e:
                        errors += 1
                        print(f"✗ Erreur: {signalement.title} - {str(e)}")
                else:
                    skipped += 1
                    print(f"- Fichier manquant: {image_path}")
        
        print(f"\nRésumé:")
        print(f"  Indexés: {indexed}")
        print(f"  Sautés: {skipped}")
        print(f"  Erreurs: {errors}")
        print(f"  Total: {indexed + skipped + errors}")

if __name__ == '__main__':
    batch_index_existing_images()
```

### **Étape 6 : Ajouter à la navigation**

```html
<!-- Dans votre navigation -->
<li class="nav-item">
    <a class="nav-link" href="{{ url_for('recherche_visage') }}">
        <i class="fas fa-search"></i> Recherche par visage
    </a>
</li>
```

## Points importants à considérer :

### **1. Aspects légaux et éthiques**
- Informez les utilisateurs que leurs photos sont analysées
- Obtenez le consentement explicite
- Stockez les données de façon sécurisée
- Supprimez les photos après traitement si demandé

### **2. Optimisations**
- Utilisez des threads pour les recherches
- Cachez les résultats fréquents
- Limitez le taux de requêtes par utilisateur
- Compressez les images avant traitement

### **3. Sécurité**
- Validez toutes les images uploadées
- Limitez la taille des fichiers
- Utilisez un sandbox pour le traitement
- Journalisez toutes les recherches

### **4. Performance**
- Indexez périodiquement (cron job)
- Utilisez Redis pour le cache
- Optimisez les requêtes SQL
- Chargez les encodages en mémoire au démarrage

## Pour tester rapidement :

1. Installez les dépendances :
```bash
pip install face_recognition opencv-python numpy pillow
```

2. Lancez le script d'indexation :
```bash
python create_batch_index.py
```

3. Testez avec une photo de visage

Cette implémentation vous donne une base solide pour la recherche faciale. Vous pouvez l'améliorer avec :
- L'utilisation de DeepFace pour plus de précision
- L'ajout de l'analyse d'âge/sexe
- La détection d'émotions
- L'historique des recherches
- Les notifications en temps réel