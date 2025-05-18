from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# Database configuration for both local and Render.com
if os.environ.get('RENDER'):
    app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
else:
    # Local database URL
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:687819990505@localhost/lost_and_found'

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Database Models
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    mobile = db.Column(db.String(15), nullable=False)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)
    lost_items = db.relationship('LostItem', backref='user', lazy=True)
    found_items = db.relationship('FoundItem', backref='user', lazy=True)

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    rating = db.Column(db.Integer, nullable=False)  # 1-5 stars
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    item_found = db.Column(db.Boolean, default=False)  # Whether the user found their item

class LostItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    date_lost = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class FoundItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50))
    date_found = db.Column(db.DateTime, nullable=False)
    location = db.Column(db.String(200))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    status = db.Column(db.String(20), default='open')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Match(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    lost_item_id = db.Column(db.Integer, db.ForeignKey('lost_item.id'))
    found_item_id = db.Column(db.Integer, db.ForeignKey('found_item.id'))
    match_date = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Routes
@app.route('/')
def index():
    # Get statistics
    active_categories = db.session.query(db.func.count(db.distinct(LostItem.category))).scalar()
    pending_items = LostItem.query.filter_by(status='pending').count() + FoundItem.query.filter_by(status='pending').count()
    published_items = LostItem.query.filter_by(status='published').count() + FoundItem.query.filter_by(status='published').count()
    
    # Calculate success rate
    total_feedbacks = Feedback.query.count()
    successful_matches = Feedback.query.filter_by(item_found=True).count()
    success_rate = (successful_matches / total_feedbacks * 100) if total_feedbacks > 0 else 0
    
    # Calculate average rating
    avg_rating = db.session.query(db.func.avg(Feedback.rating)).scalar() or 0
    
    # Get recent items
    lost_items = LostItem.query.filter_by(status='open').order_by(LostItem.created_at.desc()).limit(5).all()
    found_items = FoundItem.query.filter_by(status='open').order_by(FoundItem.created_at.desc()).limit(5).all()
    
    # Get recent feedbacks
    recent_feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).limit(5).all()
    
    return render_template('index.html',
                         active_categories=active_categories,
                         pending_items=pending_items,
                         published_items=published_items,
                         lost_items=lost_items,
                         found_items=found_items,
                         success_rate=round(success_rate, 1),
                         avg_rating=round(avg_rating, 1),
                         recent_feedbacks=recent_feedbacks)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        mobile = request.form.get('mobile')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email, mobile=mobile)
        user.password_hash = generate_password_hash(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Registration successful')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        
        flash('Invalid username or password')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/report-lost', methods=['GET', 'POST'])
@login_required
def report_lost():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        date_lost = datetime.strptime(request.form.get('date_lost'), '%Y-%m-%d')
        location = request.form.get('location')
        
        lost_item = LostItem(
            title=title,
            description=description,
            category=category,
            date_lost=date_lost,
            location=location,
            user_id=current_user.id
        )
        
        db.session.add(lost_item)
        db.session.commit()
        flash('Lost item reported successfully')
        return redirect(url_for('index'))
    
    return render_template('report_lost.html')

@app.route('/report-found', methods=['GET', 'POST'])
@login_required
def report_found():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        date_found = datetime.strptime(request.form.get('date_found'), '%Y-%m-%d')
        location = request.form.get('location')
        
        found_item = FoundItem(
            title=title,
            description=description,
            category=category,
            date_found=date_found,
            location=location,
            user_id=current_user.id
        )
        
        db.session.add(found_item)
        db.session.commit()
        flash('Found item reported successfully')
        return redirect(url_for('index'))
    
    return render_template('report_found.html')

@app.route('/admin')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        return redirect(url_for('index'))
    
    # Get all users except admins
    users = User.query.filter_by(is_admin=False).all()
    
    # Get all items with their current status
    lost_items = LostItem.query.order_by(LostItem.created_at.desc()).all()
    found_items = FoundItem.query.order_by(FoundItem.created_at.desc()).all()
    
    # Get all feedback
    feedbacks = Feedback.query.order_by(Feedback.created_at.desc()).all()
    
    return render_template('admin_dashboard.html',
                         users=users,
                         lost_items=lost_items,
                         found_items=found_items,
                         feedbacks=feedbacks)

@app.route('/admin/item/<string:type>/<int:item_id>/edit', methods=['POST'])
@login_required
def edit_item(type, item_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    data = request.json
    
    try:
        if type == 'lost':
            item = LostItem.query.get_or_404(item_id)
        else:
            item = FoundItem.query.get_or_404(item_id)
        
        if 'title' in data:
            item.title = data['title']
        if 'description' in data:
            item.description = data['description']
        if 'category' in data:
            item.category = data['category']
        if 'location' in data:
            item.location = data['location']
        if 'status' in data:
            item.status = data['status']
        
        db.session.commit()
        return jsonify({'message': 'Item updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/item/<string:type>/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(type, item_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        if type == 'lost':
            item = LostItem.query.get_or_404(item_id)
        else:
            item = FoundItem.query.get_or_404(item_id)
        
        db.session.delete(item)
        db.session.commit()
        return jsonify({'message': 'Item deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/item/<int:item_id>/mark-found', methods=['POST'])
@login_required
def mark_item_found(item_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        item = LostItem.query.get_or_404(item_id)
        item.status = 'found'
        db.session.commit()
        return jsonify({'message': 'Item marked as found'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/feedback/<int:feedback_id>/delete', methods=['POST'])
@login_required
def delete_feedback(feedback_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        feedback = Feedback.query.get_or_404(feedback_id)
        db.session.delete(feedback)
        db.session.commit()
        return jsonify({'message': 'Feedback deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/user/<int:user_id>/edit', methods=['POST'])
@login_required
def edit_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        data = request.json
        
        if 'username' in data:
            user.username = data['username']
        if 'email' in data:
            user.email = data['email']
        if 'mobile' in data:
            user.mobile = data['mobile']
        
        db.session.commit()
        return jsonify({'message': 'User updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
def toggle_user_status(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        user.is_active = not user.is_active
        db.session.commit()
        return jsonify({'message': 'User status updated successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/admin/user/<int:user_id>/delete', methods=['POST'])
@login_required
def delete_user(user_id):
    if not current_user.is_admin:
        return jsonify({'error': 'Unauthorized'}), 403
    
    try:
        user = User.query.get_or_404(user_id)
        
        # Don't allow deleting admin users
        if user.is_admin:
            return jsonify({'error': 'Cannot delete admin user'}), 400
        
        # Delete all associated items and feedback
        LostItem.query.filter_by(user_id=user_id).delete()
        FoundItem.query.filter_by(user_id=user_id).delete()
        Feedback.query.filter_by(user_id=user_id).delete()
        
        db.session.delete(user)
        db.session.commit()
        return jsonify({'message': 'User and associated data deleted successfully'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@app.route('/feedback', methods=['GET', 'POST'])
@login_required
def submit_feedback():
    if request.method == 'POST':
        rating = int(request.form.get('rating'))
        comment = request.form.get('comment')
        item_found = request.form.get('item_found') == 'yes'
        
        feedback = Feedback(
            user_id=current_user.id,
            rating=rating,
            comment=comment,
            item_found=item_found
        )
        
        db.session.add(feedback)
        db.session.commit()
        
        flash('Thank you for your feedback!')
        return redirect(url_for('index'))
    
    return render_template('feedback.html')

@app.route('/fix_login', methods=['POST'])
def fix_login():
    username = request.form.get('username')
    password = request.form.get('password')
    
    if not username or not password:
        flash('Please provide both username and password', 'error')
        return redirect(url_for('index'))
    
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            hashed_password = generate_password_hash(password)
            sql = "UPDATE user SET password_hash = %s WHERE username = %s"
            cursor.execute(sql, (hashed_password, username))
            conn.commit()
            
            if cursor.rowcount > 0:
                flash(f"Success! User '{username}' can now log in with the new password.", 'success')
            else:
                flash(f"User '{username}' not found in database.", 'error')
            
    except Exception as e:
        flash(f"Error: {str(e)}", 'error')
    finally:
        conn.close()
    
    return redirect(url_for('index'))

def get_db_connection():
    return pymysql.connect(**DB_CONFIG)

def create_admin_user(username, email, password):
    with app.app_context():
        # Check if admin already exists
        admin = User.query.filter_by(username=username).first()
        if admin:
            print(f"Admin user '{username}' already exists")
            return
        
        # Create new admin user
        admin = User(
            username=username,
            email=email,
            mobile='admin',  # You can update this if needed
            is_admin=True
        )
        admin.password_hash = generate_password_hash(password)
        db.session.add(admin)
        try:
            db.session.commit()
            print(f"Admin user '{username}' created successfully")
        except Exception as e:
            db.session.rollback()
            print(f"Error creating admin user: {e}")

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        # Create admin user with credentials from config
        create_admin_user(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            password=ADMIN_PASSWORD
        )
    app.run(host='0.0.0.0', port=8080) 