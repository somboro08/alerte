from app import app, db, User, Signalement, Comment, Notification, PasswordResetToken
from sqlalchemy import text
import os

# Set up a dummy SQLALCHEMY_DATABASE_URI if not set, for app_context
# This is mainly for local execution of this script outside of gunicorn,
# but Render will have DATABASE_URL set.
if 'DATABASE_URL' not in os.environ:
    os.environ['DATABASE_URL'] = 'sqlite:///signalalert.db'

with app.app_context():
    print("Running database initialization script for Render...")
    db.create_all()
    print("Tables checked/created.")

    # Create admin user only if it doesn't exist
    if not User.query.filter_by(email='admin@signalalert.bj').first():
        admin = User(
            username='admin',
            email='admin@signalalert.bj',
            is_active=True
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✅ Base de données initialisée avec l'utilisateur admin.")
    else:
        print("Admin user already exists, skipping creation.")
    print("Database initialization script finished.")
