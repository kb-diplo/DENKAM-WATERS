from django.core.management.base import BaseCommand
from django.db import connection

class Command(BaseCommand):
    help = 'Fixes the account_account_id_seq sequence issue'

    def handle(self, *args, **options):
        with connection.cursor() as cursor:
            try:
                # First, check if the sequence exists
                cursor.execute("""
                    SELECT 1 
                    FROM information_schema.sequences 
                    WHERE sequence_name = 'account_account_id_seq';
                """)
                
                if cursor.fetchone():
                    self.stdout.write(self.style.SUCCESS('Sequence exists, attempting to fix...'))
                    
                    # Get the current max id
                    cursor.execute("SELECT MAX(id) FROM account_account;")
                    max_id = cursor.fetchone()[0] or 0
                    
                    # Set the sequence to the max id + 1
                    cursor.execute(f"""
                        ALTER SEQUENCE account_account_id_seq 
                        RESTART WITH {max_id + 1};
                    """)
                    
                    self.stdout.write(self.style.SUCCESS(f'Successfully reset sequence to {max_id + 1}'))
                else:
                    self.stdout.write(self.style.WARNING('Sequence does not exist. Creating it...'))
                    
                    # Create the sequence
                    cursor.execute("""
                        CREATE SEQUENCE account_account_id_seq;
                        SELECT setval('account_account_id_seq', (SELECT COALESCE(MAX(id), 0) + 1 FROM account_account));
                        ALTER TABLE account_account 
                        ALTER COLUMN id 
                        SET DEFAULT nextval('account_account_id_seq');
                        ALTER SEQUENCE account_account_id_seq OWNED BY account_account.id;
                    """)
                    
                    self.stdout.write(self.style.SUCCESS('Successfully created sequence and set default'))
                    
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Error: {str(e)}'))
                self.stdout.write(self.style.ERROR('You may need to run this with a database superuser account'))
