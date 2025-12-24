from app import app, db, Signalement
from sqlalchemy import text, inspect

def update_database_schema():
    with app.app_context():
        inspector = inspect(db.engine)
        table_exists = inspector.has_table("signalement")

        if not table_exists:
            print("Table 'signalement' does not exist. Please run init_db() first.")
            return

        columns_to_add = {
            'lat': "FLOAT NULL",
            'lng': "FLOAT NULL",
            'views': "INTEGER DEFAULT 0",
            'identification': "VARCHAR(255) NULL",
            'additional_info': "TEXT NULL",
            'phone': "VARCHAR(50) NULL",
            'email': "VARCHAR(120) NULL"
        }

        existing_columns = [col['name'] for col in inspector.get_columns('signalement')]

        with db.engine.connect() as connection:
            for col_name, col_type in columns_to_add.items():
                if col_name not in existing_columns:
                    print(f"Adding '{col_name}' column to 'signalement' table...")
                    connection.execute(text(f"ALTER TABLE signalement ADD COLUMN {col_name} {col_type}"))
                else:
                    print(f"Column '{col_name}' already exists.")
            connection.commit()
        print("Database schema update process finished.")

if __name__ == '__main__':
    update_database_schema()
    print("Update script update_2.py executed.")
