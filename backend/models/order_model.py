from database.db import Database
from bson.objectid import ObjectId
from datetime import datetime, timedelta
import uuid

class Order:
    """Order Model"""
    
    collection = Database.get_collection('orders')
    
    ORDER_STATUS = {
        'pending': 'Order Placed',
        'confirmed': 'Restaurant Accepted',
        'preparing': 'Preparing Food',
        'ready': 'Ready for Pickup',
        'picked_up': 'Out for Delivery',
        'delivered': 'Delivered',
        'cancelled': 'Cancelled',
        'failed': 'Payment Failed'
    }
    
    @staticmethod
    def create(order_data):
        """Create new order"""
        order = {
            'order_number': f"ORD-{uuid.uuid4().hex[:8].upper()}",
            'user_id': ObjectId(order_data['user_id']),
            'restaurant_id': ObjectId(order_data['restaurant_id']),
            'items': order_data['items'],
            'subtotal': order_data['subtotal'],
            'delivery_charge': order_data.get('delivery_charge', 50),
            'tax': order_data.get('tax', 0),
            'discount': order_data.get('discount', 0),
            'total_amount': order_data['total_amount'],
            'status': 'pending',
            'delivery_address': order_data.get('delivery_address'),
            'delivery_instructions': order_data.get('delivery_instructions', ''),
            'estimated_delivery_time': datetime.utcnow() + timedelta(minutes=30),
            'delivery_partner_id': None,
            'delivery_partner_location': None,
            'payment_method': order_data.get('payment_method'),
            'payment_status': 'pending',
            'transaction_id': None,
            'is_group_order': order_data.get('is_group_order', False),
            'group_order_id': order_data.get('group_order_id'),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'delivered_at': None,
            'cancelled_at': None,
            'cancellation_reason': None,
            'user_rating': None,
            'user_review': None,
            'coupon_code': order_data.get('coupon_code'),
            'special_instructions': order_data.get('special_instructions', '')
        }
        
        result = Order.collection.insert_one(order)
        return {
            'success': True,
            'order_id': str(result.inserted_id),
            'order_number': order['order_number']
        }
    
    @staticmethod
    def find_by_id(order_id):
        """Find order by ID"""
        try:
            order = Order.collection.find_one({'_id': ObjectId(order_id)})
            if order:
                Order._format_order(order)
            return order
        except:
            return None
    
    @staticmethod
    def find_by_order_number(order_number):
        """Find order by order number"""
        order = Order.collection.find_one({'order_number': order_number})
        if order:
            Order._format_order(order)
        return order
    
    @staticmethod
    def get_user_orders(user_id, status=None):
        """Get orders for a specific user"""
        query = {'user_id': ObjectId(user_id)}
        if status:
            query['status'] = status
        
        orders = list(Order.collection.find(query).sort('created_at', -1))
        for order in orders:
            Order._format_order(order)
        return orders
    
    @staticmethod
    def get_restaurant_orders(restaurant_id, status=None):
        """Get orders for a specific restaurant"""
        query = {'restaurant_id': ObjectId(restaurant_id)}
        if status:
            query['status'] = status
        
        orders = list(Order.collection.find(query).sort('created_at', -1))
        for order in orders:
            Order._format_order(order)
        return orders
    
    @staticmethod
    def update_status(order_id, new_status):
        """Update order status"""
        if new_status not in Order.ORDER_STATUS:
            return False
        
        update_data = {
            'status': new_status,
            'updated_at': datetime.utcnow()
        }
        
        if new_status == 'delivered':
            update_data['delivered_at'] = datetime.utcnow()
        elif new_status == 'cancelled':
            update_data['cancelled_at'] = datetime.utcnow()
        
        result = Order.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def assign_delivery_partner(order_id, delivery_partner_id):
        """Assign delivery partner to order"""
        result = Order.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {
                'delivery_partner_id': ObjectId(delivery_partner_id),
                'updated_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    @staticmethod
    def update_delivery_location(order_id, latitude, longitude):
        """Update delivery partner's live location"""
        result = Order.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {
                'delivery_partner_location': {
                    'latitude': latitude,
                    'longitude': longitude,
                    'updated_at': datetime.utcnow()
                }
            }}
        )
        return result.modified_count > 0
    
    @staticmethod
    def update_payment_status(order_id, payment_status, transaction_id=None):
        """Update payment status"""
        update_data = {
            'payment_status': payment_status,
            'updated_at': datetime.utcnow()
        }
        
        if transaction_id:
            update_data['transaction_id'] = transaction_id
        
        result = Order.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def add_rating(order_id, rating, review):
        """Add user rating and review"""
        result = Order.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {
                'user_rating': rating,
                'user_review': review,
                'updated_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    @staticmethod
    def cancel_order(order_id, reason):
        """Cancel order"""
        result = Order.collection.update_one(
            {'_id': ObjectId(order_id)},
            {'$set': {
                'status': 'cancelled',
                'cancelled_at': datetime.utcnow(),
                'cancellation_reason': reason,
                'updated_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0
    
    @staticmethod
    def get_active_orders():
        """Get all active orders across the platform"""
        active_statuses = ['pending', 'confirmed', 'preparing', 'ready', 'picked_up']
        orders = list(Order.collection.find({'status': {'$in': active_statuses}}))
        for order in orders:
            Order._format_order(order)
        return orders
    
    @staticmethod
    def get_orders_by_date_range(start_date, end_date):
        """Get orders within date range (for analytics)"""
        orders = list(Order.collection.find({
            'created_at': {'$gte': start_date, '$lte': end_date}
        }))
        for order in orders:
            Order._format_order(order)
        return orders
    
    @staticmethod
    def _format_order(order):
        """Format order for response"""
        order['_id'] = str(order['_id'])
        order['user_id'] = str(order['user_id'])
        order['restaurant_id'] = str(order['restaurant_id'])
        
        if order.get('delivery_partner_id'):
            order['delivery_partner_id'] = str(order['delivery_partner_id'])
        
        if order.get('group_order_id'):
            order['group_order_id'] = str(order['group_order_id'])
        
        return order