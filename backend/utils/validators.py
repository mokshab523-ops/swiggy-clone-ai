import re
from functools import wraps
from flask import jsonify

class Validators:
    """Input validation utilities"""
    
    @staticmethod
    def is_valid_email(email):
        """Validate email format"""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_phone(phone):
        """Validate 10-digit Indian phone"""
        pattern = r'^[6-9]\d{9}$'
        return re.match(pattern, phone) is not None
    
    @staticmethod
    def is_valid_password(password):
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters"
        
        has_upper = any(c.isupper() for c in password)
        has_lower = any(c.islower() for c in password)
        has_digit = any(c.isdigit() for c in password)
        has_special = any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in password)
        
        if not (has_upper and has_lower and has_digit and has_special):
            return False, "Password must have uppercase, lowercase, number, and special char"
        
        return True, "Valid"
    
    @staticmethod
    def is_valid_name(name):
        """Validate name (alphabets only)"""
        return re.match(r'^[a-zA-Z\s]{2,50}$', name) is not None
    
    @staticmethod
    def is_valid_url(url):
        """Validate URL format"""
        pattern = r'^https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)$'
        return re.match(pattern, url) is not None

class Helpers:
    """Helper functions"""
    
    @staticmethod
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance between two coordinates using Haversine formula"""
        from math import radians, cos, sin, asin, sqrt
        
        lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
        dlon = lon2 - lon1
        dlat = lat2 - lat1
        a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a))
        r = 6371  # Radius of earth in kilometers
        return c * r
    
    @staticmethod
    def calculate_delivery_eta(distance, avg_speed=15):
        """Calculate estimated delivery time in minutes"""
        time_hours = distance / avg_speed
        time_minutes = time_hours * 60
        return int(time_minutes) + 5  # Add 5 minute buffer
    
    @staticmethod
    def apply_discount(original_price, discount_percent):
        """Calculate discounted price"""
        return original_price * (1 - discount_percent / 100)
    
    @staticmethod
    def calculate_tax(amount, tax_rate=5):
        """Calculate GST (5% by default)"""
        return amount * (tax_rate / 100)
    
    @staticmethod
    def format_response(success, data=None, error=None, message=None):
        """Format API response"""
        response = {
            'success': success,
        }
        
        if data:
            response['data'] = data
        if error:
            response['error'] = error
        if message:
            response['message'] = message
        
        return response
    
    @staticmethod
    def paginate_results(items, page, per_page):
        """Paginate results"""
        total = len(items)
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            'items': items[start:end],
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }