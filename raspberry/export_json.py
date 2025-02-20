import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from models import Base  # Import Base dari models
from config import DB_CONFIG
import json
from datetime import datetime

def json_serial(obj):
    """JSON serializer untuk objek yang tidak bisa di-serialize otomatis"""
    if isinstance(obj, datetime):
        return obj.isoformat()
    raise TypeError(f"Tipe {type(obj)} tidak bisa di-serialize")

def export_database_to_json(export_dir='db_export'):
    # Buat direktori export jika belum ada
    os.makedirs(export_dir, exist_ok=True)

    # Buat koneksi database
    db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Gunakan inspector untuk mendapatkan daftar tabel
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        
        print(f"Ditemukan {len(table_names)} tabel dalam database:")
        for table_name in table_names:
            print(f"- {table_name}")

        # Cari model yang sesuai dengan nama tabel
        for table_name in table_names:
            # Cari model yang memiliki __tablename__ sesuai
            table_model = None
            for model in Base.__subclasses__():
                if hasattr(model, '__tablename__') and model.__tablename__ == table_name:
                    table_model = model
                    break

            if table_model:
                # Query semua data dari tabel
                results = session.query(table_model).all()
                
                # Konversi ke list of dictionaries
                data = []
                for row in results:
                    # Konversi objek SQLAlchemy ke dictionary
                    row_dict = {column.name: getattr(row, column.name) for column in row.__table__.columns}
                    data.append(row_dict)
                
                # Buat nama file
                filename = os.path.join(export_dir, f"{table_name}_export.json")
                
                # Tulis ke file JSON
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, default=json_serial, ensure_ascii=False)
                
                print(f"Exported {len(data)} records from {table_name} to {filename}")
            else:
                print(f"Tidak ditemukan model untuk tabel {table_name}")
    
    except Exception as e:
        print(f"Error during export: {e}")
    
    finally:
        session.close()

# Jalankan export
if __name__ == "__main__":
    export_database_to_json()