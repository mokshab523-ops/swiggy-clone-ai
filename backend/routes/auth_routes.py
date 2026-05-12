from flask import Blueprint, request, jsonify
from models.user_model import User
from middleware.auth_middleware import JWTHandler, token_required
from utils.validators import Validators, Helpers
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['first_name', 'last_name', 'email', 'phone', 'password']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Create user
        result = User.create(data)
        
        if not result['success']:
            return jsonify({'error': result['error']}), 400
        
        # Generate token
        token = JWTHandler.generate_token(result['user_id'])
        
        return jsonify({
            'success': True,
            'message': 'User registered successfully',
            'user_id': result['user_id'],
            'token': token
        }), 201
        
    except Exception as e:
        logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email and password required'}), 400
        
        # Find user by email
        user = User.find_by_email(email)
        
        if not user:
            return jsonify({'error': 'Invalid email or password'}), 401
        
        # Verify password
        if not User.verify_password(password, user['password']):
            return jsonify({'error': 'Invalid email or password'}), 401
        
        if not user.get('is_active'):
            return jsonify({'error': 'Account is inactive'}), 403
        
        # Update last login
        User.update_last_login(user['_id'])
        
        # Generate token
        token = JWTHandler.generate_token(user['_id'])
        
        # Remove password from response
        user.pop('password', None)
        
        return jsonify({
            'success': True,
            'message': 'Login successful',
            'user': user,
            'token': token
        }), 200
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/verify-token', methods=['POST'])
def verify_token():
    """Verify JWT token"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token required'}), 400
        
        result = JWTHandler.verify_token(token)
        
        if result['valid']:
            user = User.find_by_id(result['user_id'])
            if user:
                user.pop('password', None)
                return jsonify({
                    'success': True,
                    'valid': True,
                    'user': user
                }), 200
        
        return jsonify({
            'success': False,
            'valid': False,
            'error': result.get('error', 'Invalid token')
        }), 401
        
    except Exception as e:
        logger.error(f"Token verification error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/profile', methods=['GET'])
@token_required
def get_profile():
    """Get user profile"""
    try:
        user = request.current_user
        user.pop('password', None)
        
        return jsonify({
            'success': True,
            'user': user
        }), 200
        
    except Exception as e:
        logger.error(f"Profile fetch error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/update-profile', methods=['PUT'])
@token_required
def update_profile():
    """Update user profile"""
    try:
        user = request.current_user
        data = request.get_json()
        
        # Update allowed fields
        allowed_fields = ['first_name', 'last_name', 'profile_image', 'latitude', 'longitude']
        update_data = {field: data[field] for field in allowed_fields if field in data}
        
        if not update_data:
            return jsonify({'error': 'No fields to update'}), 400
        
        if User.update(user['_id'], update_data):
            updated_user = User.find_by_id(user['_id'])
            updated_user.pop('password', None)
            
            return jsonify({
                'success': True,
                'message': 'Profile updated successfully',
                'user': updated_user
            }), 200
        
        return jsonify({'error': 'Update failed'}), 400
        
    except Exception as e:
        logger.error(f"Profile update error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/change-password', methods=['POST'])
@token_required
def change_password():
    """Change user password"""
    try:
        user = request.current_user
        data = request.get_json()
        
        old_password = data.get('old_password')
        new_password = data.get('new_password')
        
        if not old_password or not new_password:
            return jsonify({'error': 'Both passwords required'}), 400
        
        # Verify old password
        if not User.verify_password(old_password, user['password']):
            return jsonify({'error': 'Old password is incorrect'}), 401
        
        # Validate new password
        is_valid, msg = User.validate_password(new_password)
        if not is_valid:
            return jsonify({'error': msg}), 400
        
        # Update password
        hashed_password = User.hash_password(new_password)
        User.update(user['_id'], {'password': hashed_password})
        
        return jsonify({
            'success': True,
            'message': 'Password changed successfully'
        }), 200
        
    except Exception as e:
        logger.error(f"Password change error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/add-address', methods=['POST'])
@token_required
def add_address():
    """Add delivery address"""
    try:
        user = request.current_user
        data = request.get_json()
        
        required_fields = ['address', 'latitude', 'longitude', 'label']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        address = {
            'address': data['address'],
            'latitude': data['latitude'],
            'longitude': data['longitude'],
            'label': data['label'],  # Home, Work, etc.
            'is_default': data.get('is_default', False)
        }
        
        address_id = User.add_address(user['_id'], address)
        
        return jsonify({
            'success': True,
            'message': 'Address added successfully',
            'address_id': address_id
        }), 201
        
    except Exception as e:
        logger.error(f"Add address error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@auth_bp.route('/logout', methods=['POST'])
@token_required
def logout():
    """Logout user (frontend should clear token)"""
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    }), 200