import argparse
from sqlalchemy import create_engine, text, inspect, JSON
from sqlalchemy.exc import SQLAlchemyError
from models import Base, BMSData, CellVoltage, SCCData, LoadData, Tenant, EnvironmentData, SiteData, DeviceInfo
from migration import init_db, create_initial_data
from config import DB_CONFIG


def get_engine():
    db_url = f"postgresql://{DB_CONFIG['user']}:{DB_CONFIG['password']}@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    return create_engine(db_url)

def rollback():
    """Rollback database by dropping all tables"""
    print("Rolling back database...")
    engine = get_engine()
    
    # Drop all tables with CASCADE
    with engine.connect() as connection:
        # Disable foreign key checks temporarily
        connection.execute(text("DROP SCHEMA public CASCADE;"))
        connection.execute(text("CREATE SCHEMA public;"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO postgres;"))
        connection.execute(text("GRANT ALL ON SCHEMA public TO public;"))
    
    print("Rollback completed successfully")

def migrate():
    """Run database migrations"""
    print("Running migrations...")
    engine = init_db()
    create_initial_data(engine)
    print("Migration completed successfully")

def refresh():
    """Rollback and run migrations"""
    rollback()
    migrate()

def status():
    """Check database status"""
    try:
        engine = get_engine()
        
        # Tambahkan debug print
        print("Engine created successfully")
        
        inspector = inspect(engine)
        
        print("\nDatabase Status:")
        print("-" * 50)
        
        #Gunakan metode berbeda untuk mendapatkan nama tabel
        with engine.connect() as connection:
            table_query = text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """)
            tables = connection.execute(table_query).fetchall()
        
        print(f"Tables found ({len(tables)}):")
        for (table,) in tables:
            print(f"  - {table}")
            
            # Hitung jumlah baris
            try:
                with engine.connect() as conn:
                    count_query = text(f"SELECT COUNT(*) FROM {table}")
                    result = conn.execute(count_query)
                    count = result.scalar()
                    print(f"    Rows: {count}")
            except SQLAlchemyError as count_error:
                print(f"    Could not count rows: {count_error}")
        
    except Exception as e:
        print(f"Error connecting to database: {e}")
        import traceback
        traceback.print_exc()
        
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Database management commands')
    parser.add_argument('command', choices=['rollback', 'migrate', 'refresh', 'status'],
                       help='Command to execute')
    
    args = parser.parse_args()
    
    if args.command == 'rollback':
        answer = input("This will delete all tables and data. Are you sure? (y/n): ")
        if answer.lower() == 'y':
            rollback()
    elif args.command == 'migrate':
        migrate()
    elif args.command == 'refresh':
        answer = input("This will delete all data and recreate tables. Are you sure? (y/n): ")
        if answer.lower() == 'y':
            refresh()
    elif args.command == 'status':
        status()