import cv2
import numpy as np
# import face_recognition # Removed
from deepface import DeepFace # NEW
from PIL import Image
import io
import os
import pickle # Added explicitly for pickle.loads/dumps
from typing import List, Tuple, Optional

class FacialRecognitionService:
    def __init__(self, model_name='Facenet', detector_backend='opencv', distance_metric='euclidean_l2'): # Changed to DeepFace compatible params
        """
        Initialise le service de reconnaissance faciale avec DeepFace
        model_name: Modèle à utiliser pour l'encodage (e.g., 'VGG-Face', 'Facenet', 'OpenFace', 'DeepFace', 'DeepID', 'ArcFace', 'Dlib', 'SFace')
        detector_backend: Backend de détection de visage (e.g., 'opencv', 'ssd', 'dlib', 'mtcnn', 'retinaface', 'mediapipe', 'yolov8')
        distance_metric: Métrique de distance pour la comparaison (e.g., 'cosine', 'euclidean', 'euclidean_l2')
        """
        self.model_name = model_name
        self.detector_backend = detector_backend
        self.distance_metric = distance_metric
        self.known_encodings = {} # Stores deepface embeddings
        self.known_metadata = {}
        self.initialized_deepface = False # Flag to avoid re-initializing DeepFace models

    def _initialize_deepface_models(self):
        """Initialise les modèles DeepFace si nécessaire."""
        if not self.initialized_deepface:
            try:
                print(f"DeepFace: Initializing models ({self.model_name}, {self.detector_backend})...")
                # DeepFace.build_model() loads models. Represent also loads them.
                # We just need to ensure the backend is ready.
                # This is more of an internal DeepFace mechanism.
                # We can force a dummy call to ensure models are loaded.
                self.initialized_deepface = True
                print("DeepFace: Models initialized.")
            except Exception as e:
                print(f"Error initializing DeepFace models: {e}")
                self.initialized_deepface = False


    def load_known_faces(self):
        """Charge tous les visages connus depuis la base de données"""
        from app import db, FaceEncoding
        
        face_encodings_db = FaceEncoding.query.filter_by(is_active=True).all()
        
        self.known_encodings = {} # Clear existing
        self.known_metadata = {}  # Clear existing
        
        for fe in face_encodings_db:
            try:
                # Convertir le binaire en numpy array (DeepFace embeddings are numpy arrays)
                embedding = pickle.loads(fe.encoding)
                if isinstance(embedding, np.ndarray):
                    self.known_encodings[fe.id] = embedding
                    self.known_metadata[fe.id] = {
                        'user_id': fe.user_id,
                        'signalement_id': fe.signalement_id
                    }
                else:
                    print(f"Warning: Stored encoding for face_id {fe.id} is not a numpy array. Skipping.")
            except Exception as e:
                print(f"Error loading face_id {fe.id}: {e}. Skipping.")
        
        print(f"Loaded {len(self.known_encodings)} known face embeddings.")
        return len(self.known_encodings)
    
    def encode_face(self, image_data) -> Optional[List[np.ndarray]]:
        """
        Encode un visage à partir d'une image en utilisant DeepFace.represent.
        Retourne une liste d'embeddings pour chaque visage détecté.
        """
        try:
            # DeepFace.represent expects either a path or a numpy array (image loaded by opencv)
            # We need to convert image_data (bytes) to a numpy array readable by DeepFace
            if isinstance(image_data, bytes):
                nparr = np.frombuffer(image_data, np.uint8)
                image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                if image is None:
                    raise ValueError("Could not decode image bytes to OpenCV image.")
            elif isinstance(image_data, str): # Assume it's a file path
                image = image_data
            elif isinstance(image_data, np.ndarray):
                image = image_data
            else:
                raise ValueError("Format d'image non supporté")

            # Extract embeddings. DeepFace.represent can handle multiple faces in an image
            # It returns a list of dictionaries, each containing 'embedding' key
            embeddings = DeepFace.represent(
                img_path=image,
                model_name=self.model_name,
                detector_backend=self.detector_backend,
                enforce_detection=False # Allow processing even if no face is detected initially (might still fail)
            )

            if embeddings:
                return [np.array(e["embedding"]) for e in embeddings]
            else:
                return None
            
        except Exception as e:
            print(f"Erreur lors de l'encodage DeepFace: {e}")
            return None
    
    def compare_faces(self, unknown_embedding: np.ndarray, 
                     tolerance: float = 0.6) -> List[Tuple[int, float]]:
        """
        Compare un embedding facial inconnu avec la base de données.
        """
        matches = []
        
        if not self.known_encodings:
            self.load_known_faces()
        
        for face_id, known_embedding in self.known_encodings.items():
            try:
                # DeepFace.verify returns a dictionary with 'distance', 'verified', etc.
                verification = DeepFace.verify(
                    img1_path=unknown_embedding, # Pass embeddings directly
                    img2_path=known_embedding,   # Pass embeddings directly
                    model_name=self.model_name,
                    distance_metric=self.distance_metric,
                    enforce_detection=False # We already have embeddings, no need to detect again
                )
                
                # DeepFace's distance is usually 0 for same faces, higher for different.
                # Tolerance needs to be adapted. DeepFace uses specific thresholds.
                # Let's calculate a confidence based on distance, assuming lower distance is better.
                # Max expected distance can vary greatly, so we need a dynamic approach or fixed max_dist.
                # For now, let's assume a "good" match is distance < 0.7 for euclidean_l2 or cosine
                
                # Use DeepFace's internal threshold if available. DeepFace.verify already has a 'verified' flag.
                # Let's re-think the 'confidence' value given DeepFace's output.
                # For `distance_metric='cosine'`, threshold is often 0.4. For 'euclidean_l2', 1.0 or 1.2.
                
                # The 'tolerance' parameter here comes from the old face_recognition setup.
                # DeepFace verify directly returns a boolean 'verified' based on its internal thresholds.
                # To maintain consistency with `confidence` from 0-1 and `match_level`, we need to adjust.
                
                # For demonstration, let's use 1 - (distance / typical_max_distance_for_model)
                # This is a heuristic. DeepFace.verify's 'verified' is more robust.
                
                # Let's simply use the inverse of normalized distance as confidence.
                # Max distance for euclidean_l2 for Facenet is approx 1.5, for cosine it's 2.
                # If distance_metric is euclidean_l2:
                if self.distance_metric == 'euclidean_l2' and self.model_name == 'Facenet':
                    threshold = 0.85 # DeepFace's default for Facenet/euclidean_l2
                elif self.distance_metric == 'cosine' and self.model_name == 'Facenet':
                    threshold = 0.4 # DeepFace's default for Facenet/cosine
                else:
                    threshold = 1.0 # Fallback, might need adjustment

                confidence = max(0, (threshold - distance) / threshold) * 100
                if confidence < 0: confidence = 0 # Ensure no negative confidence

                # If DeepFace says it's verified, set confidence high
                if verification['verified']:
                    confidence = 100
                elif confidence > 0.7: # If our heuristic is still good
                    matches.append((face_id, confidence))
            
            except Exception as e:
                print(f"Erreur lors de la comparaison DeepFace (face_id {face_id}): {e}")
                
        # Filter and sort by confidence
        # For DeepFace, a lower distance means higher similarity.
        # So we need to ensure confidence mapping reflects this.
        # The 'confidence' here is now 0-100% from above heuristic.
        matches.sort(key=lambda x: x[1], reverse=True)
        
        return matches
    
    def search_similar_faces(self, image_data, max_results: int = 10):
        """
        Recherche des visages similaires dans la base en utilisant DeepFace.
        """
        # Ensure DeepFace models are loaded
        # self._initialize_deepface_models() # DeepFace.represent will load models as needed

        # Encoder l'image d'entrée
        source_embeddings = self.encode_face(image_data)
        
        if not source_embeddings:
            return {"error": "Aucun visage détecté ou encodable", "matches": []}
        
        all_matches = []
        
        # We need to load all known faces if not already loaded
        if not self.known_encodings:
            self.load_known_faces()

        # Iterate through each detected face in the input image
        for source_embedding in source_embeddings:
            for face_id, known_embedding in self.known_encodings.items():
                try:
                    # Use DeepFace.verify to compare embeddings
                    # DeepFace.verify can take embeddings as img1_path and img2_path
                    verification = DeepFace.verify(
                        img1_path=source_embedding,
                        img2_path=known_embedding,
                        model_name=self.model_name,
                        detector_backend='skip', # Skip detection as we have embeddings
                        distance_metric=self.distance_metric,
                        enforce_detection=False # Important for embedding comparison
                    )
                    
                    # DeepFace's `verified` is based on its internal threshold.
                    # We can use this directly or derive a confidence.
                    # Let's derive a confidence from distance for consistency with the template.
                    distance = verification['distance']
                    
                    # Define a threshold based on model and metric
                    if self.distance_metric == 'euclidean_l2':
                        if self.model_name == 'Facenet': threshold = 0.85
                        elif self.model_name == 'VGG-Face': threshold = 0.68
                        else: threshold = 1.0 # Generic fallback
                    elif self.distance_metric == 'cosine':
                        if self.model_name == 'Facenet': threshold = 0.4
                        elif self.model_name == 'VGG-Face': threshold = 0.23
                        else: threshold = 0.5 # Generic fallback
                    else: # Assuming euclidean distance
                        threshold = 1.0 # Generic fallback

                    # Confidence calculation, aiming for 0-100%
                    # If verified is true, it's a very high confidence match
                    if verification['verified']:
                        confidence = 95 + (1 - (distance / threshold)) * 5 # Scale high confidence for verified
                        confidence = min(100, confidence) # Cap at 100
                    else:
                        confidence = max(0, (threshold - distance) / threshold) * 100
                        confidence = min(94, confidence) # Cap below verified range if not verified

                    if confidence >= 70: # Only consider matches above a certain confidence
                        all_matches.append((face_id, confidence))
                        
                except Exception as e:
                    # print(f"DeepFace comparison error: {e}")
                    pass # Ignore comparison errors for individual faces
        
        # Sort by confidence (descending)
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
                'confidence': round(confidence, 2),  # Pourcentage
                'match_level': self._get_match_level(confidence / 100) # Convert back to 0-1 for match level function
            })
        
        return {
            "total_faces_detected": len(source_embeddings),
            "matches_found": len(results),
            "matches": results
        }
    
    def _get_match_level(self, confidence: float) -> str:
        """Convertit le score en niveau textuel (confidence expected 0-1)"""
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
        Sauvegarde un encodage facial pour un signalement en utilisant DeepFace.represent.
        """
        from app import db, FaceEncoding, Signalement # Re-import inside function
        
        try:
            signalement = Signalement.query.get(signalement_id)
            if not signalement:
                return False
            
            embeddings = self.encode_face(image_data)
            if not embeddings:
                print("No face detected for encoding.")
                return False
            
            # Prendre le premier visage détecté
            main_embedding = embeddings[0]
            
            face_encoding_obj = FaceEncoding(
                signalement_id=signalement_id,
                user_id=signalement.user_id,
                encoding=pickle.dumps(main_embedding)
            )
            
            db.session.add(face_encoding_obj)
            db.session.commit()
            
            # Mettre à jour le cache
            self.known_encodings[face_encoding_obj.id] = main_embedding
            self.known_metadata[face_encoding_obj.id] = {
                'user_id': signalement.user_id,
                'signalement_id': signalement_id
            }
            
            print(f"Face encoding saved for signalement {signalement_id}")
            return True
            
        except Exception as e:
            db.session.rollback()
            print(f"Erreur lors de la sauvegarde DeepFace: {e}")
            return False

# Instance globale
# Using 'Facenet' as a default model as it's often a good balance between speed and accuracy.
# 'opencv' detector is generally fast.
# 'euclidean_l2' distance is standard for Facenet.
face_service = FacialRecognitionService(model_name='Facenet', detector_backend='opencv', distance_metric='euclidean_l2')