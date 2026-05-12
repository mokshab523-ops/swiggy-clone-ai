from database.db import Database
from bson.objectid import ObjectId
import bcrypt
from datetime import datetime
import re

class User:
    """User Model"""
    
    collection = Database.get_collection('users')
    
    @staticmethod
    def validate_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def validate_phone(phone):
        """Validate 10-digit Indian phone number"""
        pattern = r'^[6-9]\d{9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def validate_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "Password must contain uppercase, lowercase, number, and special character"
        
        return True, "Valid"
    
    @staticmethod
    def validate_name(name):
        """Validate name (alphabets only)"""
        return re.match(r'^[a-zA-Z\s]{2,50}$', name) is not None
    
    @staticmethod
    def hash_password(password):
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed.decode('utf-8')
    
    @staticmethod
    def verify_password(password, hashed_password):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def create(user_data):
        """Create new user"""
        # Validate inputs
        if not User.validate_name(user_data.get('first_name', '')):
            return {'success': False, 'error': 'Invalid first name (alphabets only)'}
        
        if not User.validate_name(user_data.get('last_name', '')):
            return {'success': False, 'error': 'Invalid last name (alphabets only)'}
        
        if not User.validate_email(user_data.get('email', '')):
            return {'success': False, 'error': 'Invalid email format'}
        
        if not User.validate_phone(user_data.get('phone', '')):
            return {'success': False, 'error': 'Invalid phone number (10 digits)'}
        
        is_valid, msg = User.validate_password(user_data.get('password', ''))
        if not is_valid:
            return {'success': False, 'error': msg}
        
        # Check duplicate email and phone
        if User.collection.find_one({'email': user_data['email']}):
            return {'success': False, 'error': 'Email already registered'}
        
        if User.collection.find_one({'phone': user_data['phone']}):
            return {'success': False, 'error': 'Phone number already registered'}
        
        # Create user object
        user = {
            'first_name': user_data['first_name'].strip(),
            'last_name': user_data['last_name'].strip(),
            'email': user_data['email'].lower().strip(),
            'phone': user_data['phone'],
            'password': User.hash_password(user_data['password']),
            'role': 'customer',
            'is_active': True,
            'is_verified': False,
            'profile_image': None,
            'addresses': [],
            'payment_methods': [],
            'wishlist': [],
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'last_login': None,
            'latitude': user_data.get('latitude'),
            'longitude': user_data.get('longitude'),
            'preferences': {
                'notifications': True,
                'email_notifications': True,
                'sms_notifications': True,
                'dark_mode': False
            },
            'banned': False,
            'ban_reason': None
        }
        
        result = User.collection.insert_one(user)
        
        return {
            'success': True,
            'user_id': str(result.inserted_id),
            'message': 'User created successfully'
        }
    
    @staticmethod
    def find_by_id(user_id):
        """Find user by ID"""
        try:
            user = User.collection.find_one({'_id': ObjectId(user_id)})
            if user:
                user['_id'] = str(user['_id'])
            return user
        except:
            return None
    
    @staticmethod
    def find_by_email(email):
        """Find user by email"""
        user = User.collection.find_one({'email': email.lower().strip()})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def find_by_phone(phone):
        """Find user by phone"""
        user = User.collection.find_one({'phone': phone})
        if user:
            user['_id'] = str(user['_id'])
        return user
    
    @staticmethod
    def update(user_id, update_data):
        """Update user information"""
        update_data['updated_at'] = datetime.utcnow()
        
        result = User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def update_last_login(user_id):
        """Update last login time"""
        User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$set': {'last_login': datetime.utcnow()}}
        )
    
    @staticmethod
    def add_address(user_id, address):
        """Add new address to user"""
        address['_id'] = ObjectId()
        address['created_at'] = datetime.utcnow()
        
        User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$push': {'addresses': address}}
        )
        
        return str(address['_id'])
    
    @staticmethod
    def add_to_wishlist(user_id, restaurant_id):
        """Add restaurant to wishlist"""
        User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$addToSet': {'wishlist': ObjectId(restaurant_id)}}
        )
    
    @staticmethod
    def remove_from_wishlist(user_id, restaurant_id):
        """Remove restaurant from wishlist"""
        User.collection.update_one(
            {'_id': ObjectId(user_id)},
            {'$pull': {'wishlist': ObjectId(restaurant_id)}}
        )
    
    @staticmethod
    def get_all_users():
        """Get all users (for admin)"""
        users = list(User.collection.find({'role': 'customer'}))
        for user in users:
            user['_id'] = str(user['_id'])
        return users
    
    @staticmethod
    def delete(user_id):
        """Delete user"""
        result = User.collection.delete_one({'_id': ObjectId(user_id)})
        return result.deleted_count > 0