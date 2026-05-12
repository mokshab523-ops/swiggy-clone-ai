from flask import Blueprint, request, jsonify
from models.restaurant_model import Restaurant
from models.order_model import Order
from middleware.auth_middleware import token_required, restaurant_required
from utils.validators import Validators, Helpers
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
restaurant_bp = Blueprint('restaurant', __name__, url_prefix='/api/restaurant')

@restaurant_bp.route('/nearby', methods=['GET'])
def get_nearby_restaurants():
    """Get nearby restaurants based on user location"""
    try:
        latitude = request.args.get('latitude', type=float)
        longitude = request.args.get('longitude', type=float)
        radius = request.args.get('radius', default=5, type=float)
        
        if latitude is None or longitude is None:
            return jsonify({'error': 'Latitude and longitude required'}), 400
        
        restaurants = Restaurant.get_nearby_restaurants(latitude, longitude, radius)
        
        return jsonify({
            'success': True,
            'restaurants': restaurants,
            'count': len(restaurants)
        }), 200
        
    except Exception as e:
        logger.error(f"Get nearby restaurants error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@restaurant_bp.route('/all', methods=['GET'])
def get_all_restaurants():
    """Get all restaurants with pagination"""
    try:
        page = request.args.get('page', default=1, type=int)
        per_page = request.args.get('per_page', default=10, type=int)
        
        restaurants = Restaurant.get_all_restaurants(page, per_page)
        
        return jsonify({
            'success': True,
            'restaurants': restaurants,
            'page': page,
            'per_page': per_page
        }), 200
        
    except Exception as e:
        logger.error(f"Get all restaurants error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@restaurant_bp.route('/<restaurant_id>', methods=['GET'])
def get_restaurant_details(restaurant_id):
    """Get detailed restaurant information"""
    try:
        restaurant = Restaurant.find_by_id(restaurant_id)
        
        if not restaurant:
            return jsonify({'error': 'Restaurant not found'}), 404
        
        return jsonify({
            'success': True,
            'restaurant': restaurant
        }), 200
        
    except Exception as e:
        logger.error(f"Get restaurant details error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@restaurant_bp.route('/search', methods=['GET'])
def search_restaurants():
    """Search restaurants by name or cuisine"""
    try:
        query = request.args.get('q', '')
        
        if not query or len(query) < 2:
            return jsonify({'error': 'Query must be at least 2 characters'}), 400
        
        restaurants = Restaurant.search_restaurants(query)
        
        return jsonify({
            'success': True,
            'restaurants': restaurants,
            'count': len(restaurants)
        }), 200
        
    except Exception as e:
        logger.error(f"Search restaurants error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@restaurant_bp.route('/category/<category>', methods=['GET'])
def get_by_category(category):
    """Get restaurants by food category"""
    try:
        restaurants = Restaurant.get_by_category(category)
        
        return jsonify({
            'success': True,
            'restaurants': restaurants,
            'category': category,
            'count': len(restaurants)
        }), 200
        
    except Exception as e:
        logger.error(f"Get by category error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@restaurant_bp.route('/wishlist/add', methods=['POST'])
@token_required
def add_to_wishlist():
    """Add restaurant to wishlist"""
    try:
        user = request.current_user
        data = request.get_json()
        restaurant_id = data.get('restaurant_id')
        
        if not restaurant_id:
            return jsonify({'error': 'Restaurant ID required'}), 400
        
        User.add_to_wishlist(user['_id'], restaurant_id)
        
        return jsonify({
            'success': True,
            'message': 'Added to wishlist'
        }), 200
        
    except Exception as e:
        logger.error(f"Add to wishlist error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@restaurant_bp.route('/dashboard', methods=['GET'])
@restaurant_required
def restaurant_dashboard():
    """Get restaurant dashboard data"""
    try:
        user = request.current_user
        restaurants = Restaurant.find_by_owner(user['_id'])
        
        if not restaurants:
            return jsonify({'error': 'No restaurants found'}), 404
        
        restaurant = restaurants[0]
        
        # Get recent orders
        recent_orders = Order.get_restaurant_orders(restaurant['_id'])
        
        # Calculate analytics
        completed_orders = [o for o in recent_orders if o['status'] == 'delivered']
        revenue = sum(o['total_amount'] for o in completed_orders)
        
        return jsonify({
            'success': True,
            'restaurant': restaurant,
            'total_orders': len(recent_orders),
            'completed_orders': len(completed_orders),
            'revenue': revenue,
            'rating': restaurant.get('rating', 4.5),
            'recent_orders': recent_orders[:5]
        }), 200
        
    except Exception as e:
        logger.error(f"Restaurant dashboard error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@restaurant_bp.route('/orders', methods=['GET'])
@restaurant_required
def get_restaurant_orders():
    """Get all orders for restaurant"""
    try:
        user = request.current_user
        status = request.args.get('status')
        
        restaurants = Restaurant.find_by_owner(user['_id'])
        if not restaurants:
            return jsonify({'error': 'No restaurants found'}), 404
        
        restaurant = restaurants[0]
        orders = Order.get_restaurant_orders(restaurant['_id'], status)
        
        return jsonify({
            'success': True,
            'orders': orders,
            'count': len(orders)
        }), 200
        
    except Exception as e:
        logger.error(f"Get restaurant orders error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500