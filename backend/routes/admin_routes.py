from flask import Blueprint, request, jsonify
from middleware.auth_middleware import admin_required
from models.order_model import Order
from models.payment_model import Payment
from models.restaurant_model import Restaurant
from models.user_model import User
from datetime import datetime, timedelta
from database.db import Database
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/dashboard', methods=['GET'])
@admin_required
def admin_dashboard():
    """Get admin dashboard statistics"""
    try:
        # Get total counts
        total_users = len(User.get_all_users())
        active_orders = Order.get_active_orders()
        total_orders = len(active_orders)
        
        # Calculate revenue
        today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        tomorrow = today + timedelta(days=1)
        
        revenue_data = Payment.get_revenue_analytics(today, tomorrow)
        today_revenue = revenue_data.get('total_revenue', 0)
        
        # Get fraud alerts
        fraud_collection = Database.get_collection('fraud_alerts')
        fraud_alerts = list(fraud_collection.find({'reviewed': False}).limit(10))
        
        return jsonify({
            'success': True,
            'dashboard': {
                'total_users': total_users,
                'active_orders': total_orders,
                'today_revenue': today_revenue,
                'fraud_alerts': len(fraud_alerts),
                'pending_fraud_reviews': len(fraud_alerts)
            },
            'active_orders': active_orders[:5],
            'recent_fraud_alerts': fraud_alerts[:5]
        }), 200
        
    except Exception as e:
        logger.error(f"Admin dashboard error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/orders', methods=['GET'])
@admin_required
def get_all_orders():
    """Get all orders with filtering"""
    try:
        status = request.args.get('status')
        page = request.args.get('page', default=1, type=int)
        
        collection = Database.get_collection('orders')
        query = {} if not status else {'status': status}
        
        skip = (page - 1) * 10
        orders = list(collection.find(query).skip(skip).limit(10))
        total = collection.count_documents(query)
        
        for order in orders:
            order['_id'] = str(order['_id'])
        
        return jsonify({
            'success': True,
            'orders': orders,
            'total': total,
            'page': page
        }), 200
        
    except Exception as e:
        logger.error(f"Get all orders error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_all_users():
    """Get all users"""
    try:
        users = User.get_all_users()
        
        # Remove passwords
        for user in users:
            user.pop('password', None)
        
        return jsonify({
            'success': True,
            'users': users,
            'total': len(users)
        }), 200
        
    except Exception as e:
        logger.error(f"Get all users error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/fraud-alerts', methods=['GET'])
@admin_required
def get_fraud_alerts():
    """Get fraud alerts"""
    try:
        collection = Database.get_collection('fraud_alerts')
        alerts = list(collection.find().sort('timestamp', -1).limit(50))
        
        for alert in alerts:
            alert['_id'] = str(alert['_id'])
            alert['payment_id'] = str(alert['payment_id'])
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        }), 200
        
    except Exception as e:
        logger.error(f"Get fraud alerts error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/fraud-alerts/<alert_id>/review', methods=['POST'])
@admin_required
def review_fraud_alert(alert_id):
    """Review fraud alert"""
    try:
        data = request.get_json()
        action = data.get('action')  # approve, block, refund
        reason = data.get('reason', '')
        
        collection = Database.get_collection('fraud_alerts')
        from bson.objectid import ObjectId
        
        result = collection.update_one(
            {'_id': ObjectId(alert_id)},
            {'$set': {
                'reviewed': True,
                'action_taken': action,
                'admin_notes': reason,
                'reviewed_at': datetime.utcnow()
            }}
        )
        
        if result.modified_count > 0:
            return jsonify({
                'success': True,
                'message': f'Alert reviewed and {action}'
            }), 200
        
        return jsonify({'error': 'Failed to review alert'}), 400
        
    except Exception as e:
        logger.error(f"Review fraud alert error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/analytics/revenue', methods=['GET'])
@admin_required
def get_revenue_analytics():
    """Get revenue analytics"""
    try:
        days = request.args.get('days', default=30, type=int)
        
        start_date = datetime.utcnow() - timedelta(days=days)
        end_date = datetime.utcnow()
        
        analytics = Payment.get_revenue_analytics(start_date, end_date)
        
        return jsonify({
            'success': True,
            'analytics': analytics,
            'period_days': days
        }), 200
        
    except Exception as e:
        logger.error(f"Get revenue analytics error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@admin_bp.route('/restaurants', methods=['GET'])
@admin_required
def get_all_restaurants():
    """Get all restaurants"""
    try:
        collection = Database.get_collection('restaurants')
        restaurants = list(collection.find())
        
        for restaurant in restaurants:
            restaurant['_id'] = str(restaurant['_id'])
        
        return jsonify({
            'success': True,
            'restaurants': restaurants,
            'count': len(restaurants)
        }), 200
        
    except Exception as e:
        logger.error(f"Get all restaurants error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500