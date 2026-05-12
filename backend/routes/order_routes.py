from flask import Blueprint, request, jsonify
from models.order_model import Order
from models.restaurant_model import Restaurant
from models.user_model import User
from middleware.auth_middleware import token_required
from utils.validators import Helpers
from datetime import datetime
import logging

logger = logging.getLogger(__name__)
order_bp = Blueprint('order', __name__, url_prefix='/api/order')

@order_bp.route('/create', methods=['POST'])
@token_required
def create_order():
    """Create new order"""
    try:
        user = request.current_user
        data = request.get_json()
        
        required_fields = ['restaurant_id', 'items', 'total_amount']
        if not all(field in data for field in required_fields):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate items
        if not isinstance(data['items'], list) or len(data['items']) == 0:
            return jsonify({'error': 'Items must be a non-empty array'}), 400
        
        # Create order
        order_data = {
            'user_id': user['_id'],
            'restaurant_id': data['restaurant_id'],
            'items': data['items'],
            'subtotal': data.get('subtotal', 0),
            'total_amount': data['total_amount'],
            'delivery_charge': data.get('delivery_charge', 50),
            'tax': data.get('tax', 0),
            'discount': data.get('discount', 0),
            'delivery_address': data.get('delivery_address'),
            'delivery_instructions': data.get('delivery_instructions', ''),
            'payment_method': data.get('payment_method', 'razorpay'),
            'coupon_code': data.get('coupon_code')
        }
        
        result = Order.create(order_data)
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Order created successfully',
                'order_id': result['order_id'],
                'order_number': result['order_number']
            }), 201
        
        return jsonify({'error': 'Failed to create order'}), 400
        
    except Exception as e:
        logger.error(f"Create order error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/<order_id>', methods=['GET'])
@token_required
def get_order(order_id):
    """Get order details"""
    try:
        order = Order.find_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check authorization
        if str(order['user_id']) != str(request.current_user['_id']):
            return jsonify({'error': 'Unauthorized'}), 403
        
        return jsonify({
            'success': True,
            'order': order
        }), 200
        
    except Exception as e:
        logger.error(f"Get order error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/user/history', methods=['GET'])
@token_required
def get_order_history():
    """Get user's order history"""
    try:
        user = request.current_user
        status = request.args.get('status')
        
        orders = Order.get_user_orders(user['_id'], status)
        
        return jsonify({
            'success': True,
            'orders': orders,
            'count': len(orders)
        }), 200
        
    except Exception as e:
        logger.error(f"Get order history error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/<order_id>/status', methods=['GET'])
@token_required
def get_order_status(order_id):
    """Get order status"""
    try:
        order = Order.find_by_id(order_id)
        
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        return jsonify({
            'success': True,
            'order_id': order_id,
            'order_number': order.get('order_number'),
            'status': order['status'],
            'status_label': Order.ORDER_STATUS.get(order['status']),
            'estimated_delivery': order.get('estimated_delivery_time'),
            'delivery_partner_location': order.get('delivery_partner_location')
        }), 200
        
    except Exception as e:
        logger.error(f"Get order status error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/<order_id>/cancel', methods=['POST'])
@token_required
def cancel_order(order_id):
    """Cancel order"""
    try:
        user = request.current_user
        data = request.get_json()
        
        order = Order.find_by_id(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check authorization
        if str(order['user_id']) != str(user['_id']):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Check if order can be cancelled
        if order['status'] in ['picked_up', 'delivered', 'cancelled']:
            return jsonify({'error': 'Order cannot be cancelled'}), 400
        
        reason = data.get('reason', 'User requested cancellation')
        
        if Order.cancel_order(order_id, reason):
            return jsonify({
                'success': True,
                'message': 'Order cancelled successfully'
            }), 200
        
        return jsonify({'error': 'Failed to cancel order'}), 400
        
    except Exception as e:
        logger.error(f"Cancel order error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/<order_id>/rate', methods=['POST'])
@token_required
def rate_order(order_id):
    """Add rating and review to order"""
    try:
        user = request.current_user
        data = request.get_json()
        
        order = Order.find_by_id(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        # Check authorization
        if str(order['user_id']) != str(user['_id']):
            return jsonify({'error': 'Unauthorized'}), 403
        
        rating = data.get('rating')
        review = data.get('review', '')
        
        if not rating or rating < 1 or rating > 5:
            return jsonify({'error': 'Rating must be between 1 and 5'}), 400
        
        if Order.add_rating(order_id, rating, review):
            return jsonify({
                'success': True,
                'message': 'Rating added successfully'
            }), 200
        
        return jsonify({'error': 'Failed to add rating'}), 400
        
    except Exception as e:
        logger.error(f"Rate order error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@order_bp.route('/active', methods=['GET'])
def get_active_orders():
    """Get all active orders (for admin dashboard)"""
    try:
        orders = Order.get_active_orders()
        
        return jsonify({
            'success': True,
            'orders': orders,
            'count': len(orders)
        }), 200
        
    except Exception as e:
        logger.error(f"Get active orders error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500