import jwt
from datetime import datetime, timedelta
from functools import wraps
from flask import request, jsonify
from config import Config
from models.user_model import User

class JWTHandler:
    """JWT Token Management"""
    
    @staticmethod
    def generate_token(user_id):
        """Generate JWT token"""
        payload = {
            'user_id': str(user_id),
            'iat': datetime.utcnow(),
            'exp': datetime.utcnow() + Config.JWT_EXPIRATION
        }
        
        token = jwt.encode(
            payload,
            Config.JWT_SECRET,
            algorithm=Config.JWT_ALGORITHM
        )
        
        return token
    
    @staticmethod
    def verify_token(token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(
                token,
                Config.JWT_SECRET,
                algorithms=[Config.JWT_ALGORITHM]
            )
            return {'valid': True, 'user_id': payload['user_id']}
        except jwt.ExpiredSignatureError:
            return {'valid': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'valid': False, 'error': 'Invalid token'}

def token_required(f):
    """Decorator to protect routes with JWT"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        # Check for token in headers
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        # Verify token
        result = JWTHandler.verify_token(token)
        if not result['valid']:
            return jsonify({'error': result['error']}), 401
        
        # Get user
        user = User.find_by_id(result['user_id'])
        if not user:
            return jsonify({'error': 'User not found'}), 401
        
        if not user.get('is_active'):
            return jsonify({'error': 'User account is inactive'}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated

def admin_required(f):
    """Decorator to protect admin routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        result = JWTHandler.verify_token(token)
        if not result['valid']:
            return jsonify({'error': result['error']}), 401
        
        user = User.find_by_id(result['user_id'])
        if not user or user.get('role') != 'admin':
            return jsonify({'error': 'Admin access required'}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated

def restaurant_required(f):
    """Decorator to protect restaurant owner routes"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({'error': 'Invalid token format'}), 401
        
        if not token:
            return jsonify({'error': 'Token missing'}), 401
        
        result = JWTHandler.verify_token(token)
        if not result['valid']:
            return jsonify({'error': result['error']}), 401
        
        user = User.find_by_id(result['user_id'])
        if not user or user.get('role') not in ['restaurant', 'admin']:
            return jsonify({'error': 'Restaurant owner access required'}), 403
        
        request.current_user = user
        return f(*args, **kwargs)
    
    return decorated