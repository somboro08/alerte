import os
from app import app, db, Signalement, FaceEncoding, User, PasswordResetToken, FaceMatch
from facial_recognition import face_service

def batch_index_existing_images():
    """Indexe toutes les images existantes dans la base"""
    with app.app_context():
        # db.create_all() # Ensure tables are created - This should be handled by init_db in app.py

        # Récupérer tous les signalements de personnes disparues avec image
        signalements = Signalement.query.filter_by(type='missing').all()
        
        print(f"Indexage de {len(signalements)} signalements...")
        
        indexed = 0
        skipped = 0
        errors = 0
        
        for signalement in signalements:
            if signalement.image_url:
                # Assuming app.config['UPLOAD_FOLDER'] is the correct base for images
                image_path = os.path.join(app.config['UPLOAD_FOLDER'], signalement.image_url)
                
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
