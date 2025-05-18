import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Admin configuration
ADMIN_USERNAME = os.getenv('ADMIN_USERNAME', 'Suraj_Believer')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', 'MS1415@gmail.com')
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'your_secure_password')

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'your_production_db_host'),
    'user': os.getenv('DB_USER', 'your_production_db_user'),
    'password': os.getenv('DB_PASSWORD', 'your_production_db_password'),
    'database': os.getenv('DB_NAME', 'lost_and_found')
} 