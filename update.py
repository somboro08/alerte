from app import app, db, Signalement
from sqlalchemy import text

def update_database_schema():
    with app.app_context():
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('signalement')
        column_names = [col['name'] for col in columns]

        if 'qr_code_url' not in column_names:
            print("Adding 'qr_code_url' column to 'signalement' table...")
            with db.engine.connect() as connection:
                connection.execute(text("ALTER TABLE signalement ADD COLUMN qr_code_url VARCHAR(500) NULL"))
                connection.commit()
            print("'qr_code_url' column added successfully.")
        else:
            print("'qr_code_url' column already exists.")
        
        # If there are any existing signalements, generate QR codes for them
        # (This is optional, but good for data consistency)
        existing_signalements = Signalement.query.filter(Signalement.qr_code_url == None).all()
        if existing_signalements:
            print(f"Found {len(existing_signalements)} existing signalements without QR codes. Skipping for now as QR code generation logic is not fully integrated yet.")
            print("You will need to manually generate QR codes for these or re-run a script after the QR generation is integrated.")


if __name__ == '__main__':
    update_database_schema()
    print("Database schema update process finished.")
