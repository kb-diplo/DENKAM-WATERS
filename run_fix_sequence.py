import os
import sys
import psycopg2
from django.conf import settings

def main():
    # Read database settings from Django settings
    db_settings = settings.DATABASES['default']
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            dbname=db_settings['NAME'],
            user=db_settings['USER'],
            password=db_settings['PASSWORD'],
            host=db_settings['HOST'],
            port=db_settings['PORT']
        )
        
        # Read the SQL file
        with open('fix_sequence.sql', 'r') as f:
            sql_commands = f.read()
        
        # Execute the SQL commands
        with conn.cursor() as cursor:
            cursor.execute(sql_commands)
        
        # Commit the transaction
        conn.commit()
        print("Successfully fixed the sequence issue!")
        
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
    import django
    django.setup()
    
    main()
