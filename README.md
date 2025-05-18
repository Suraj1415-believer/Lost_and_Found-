# Lost and Found System

A web-based Lost and Found management system built with Python Flask and MySQL.

## Features

- User Registration and Authentication
- Report Lost Items
- Report Found Items
- Admin Dashboard
- Item Matching System
- Responsive Design

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- pip (Python package manager)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/lost-and-found.git
cd lost-and-found
```

2. Create a virtual environment and activate it:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install the required packages:
```bash
pip install -r requirements.txt
```

4. Create a MySQL database:
```sql
CREATE DATABASE lost_and_found;
```

5. Update the database configuration in `app.py`:
```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/lost_and_found'
```

6. Initialize the database:
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

7. Create an admin user:
```bash
python
>>> from app import app, db, User
>>> from werkzeug.security import generate_password_hash
>>> with app.app_context():
...     admin = User(username='admin', email='admin@example.com', password_hash=generate_password_hash('admin123'), is_admin=True)
...     db.session.add(admin)
...     db.session.commit()
>>> exit()
```

## Running the Application

1. Start the Flask development server:
```bash
python app.py
```

2. Open your web browser and navigate to:
```
http://localhost:5000
```

## Default Admin Credentials

- Username: admin
- Password: admin123

## Usage

1. Register a new user account or login with existing credentials
2. Report lost items through the "Report Lost" page
3. Report found items through the "Report Found" page
4. Administrators can access the admin dashboard to:
   - Manage users
   - Review lost and found items
   - Handle potential matches
   - Update item status

## Contributing

1. Fork the repository
2. Create a new branch
3. Make your changes
4. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 