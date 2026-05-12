from database.db import Database
from bson.objectid import ObjectId
from datetime import datetime
import uuid

class Payment:
    """Payment Model"""
    
    collection = Database.get_collection('payments')
    
    PAYMENT_STATUS = {
        'pending': 'Awaiting Payment',
        'processing': 'Processing',
        'completed': 'Payment Successful',
        'failed': 'Payment Failed',
        'refunded': 'Refunded',
        'partially_refunded': 'Partially Refunded'
    }
    
    PAYMENT_METHODS = ['card', 'upi', 'wallet', 'net_banking', 'cash']
    
    @staticmethod
    def create(payment_data):
        """Create payment record"""
        payment = {
            'transaction_id': f"TXN-{uuid.uuid4().hex[:12].upper()}",
            'order_id': ObjectId(payment_data['order_id']),
            'user_id': ObjectId(payment_data['user_id']),
            'amount': payment_data['amount'],
            'currency': payment_data.get('currency', 'INR'),
            'payment_method': payment_data['payment_method'],
            'payment_gateway': payment_data.get('payment_gateway'),  # razorpay, stripe
            'gateway_transaction_id': None,
            'status': 'pending',
            'card_last_four': payment_data.get('card_last_four'),
            'card_brand': payment_data.get('card_brand'),
            'upi_id': payment_data.get('upi_id'),
            'error_message': None,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow(),
            'completed_at': None,
            'refund_requested_at': None,
            'refund_amount': 0,
            'refund_reason': None,
            'refund_status': None,
            'ip_address': payment_data.get('ip_address'),
            'user_agent': payment_data.get('user_agent'),
            'is_suspicious': False,
            'fraud_score': 0
        }
        
        result = Payment.collection.insert_one(payment)
        return {
            'success': True,
            'payment_id': str(result.inserted_id),
            'transaction_id': payment['transaction_id']
        }
    
    @staticmethod
    def find_by_id(payment_id):
        """Find payment by ID"""
        try:
            payment = Payment.collection.find_one({'_id': ObjectId(payment_id)})
            if payment:
                Payment._format_payment(payment)
            return payment
        except:
            return None
    
    @staticmethod
    def find_by_transaction_id(transaction_id):
        """Find payment by transaction ID"""
        payment = Payment.collection.find_one({'transaction_id': transaction_id})
        if payment:
            Payment._format_payment(payment)
        return payment
    
    @staticmethod
    def find_by_order_id(order_id):
        """Find payment by order ID"""
        payment = Payment.collection.find_one({'order_id': ObjectId(order_id)})
        if payment:
            Payment._format_payment(payment)
        return payment
    
    @staticmethod
    def update_status(payment_id, status, gateway_transaction_id=None, error=None):
        """Update payment status"""
        update_data = {
            'status': status,
            'updated_at': datetime.utcnow()
        }
        
        if status == 'completed':
            update_data['completed_at'] = datetime.utcnow()
        
        if gateway_transaction_id:
            update_data['gateway_transaction_id'] = gateway_transaction_id
        
        if error:
            update_data['error_message'] = error
        
        result = Payment.collection.update_one(
            {'_id': ObjectId(payment_id)},
            {'$set': update_data}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def initiate_refund(payment_id, refund_amount, reason):
        """Initiate refund process"""
        result = Payment.collection.update_one(
            {'_id': ObjectId(payment_id)},
            {'$set': {
                'refund_requested_at': datetime.utcnow(),
                'refund_amount': refund_amount,
                'refund_reason': reason,
                'refund_status': 'pending'
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def complete_refund(payment_id):
        """Complete refund process"""
        result = Payment.collection.update_one(
            {'_id': ObjectId(payment_id)},
            {'$set': {
                'status': 'refunded',
                'refund_status': 'completed',
                'updated_at': datetime.utcnow()
            }}
        )
        
        return result.modified_count > 0
    
    @staticmethod
    def update_fraud_score(payment_id, fraud_score, is_suspicious):
        """Update fraud detection score"""
        Payment.collection.update_one(
            {'_id': ObjectId(payment_id)},
            {'$set': {
                'fraud_score': fraud_score,
                'is_suspicious': is_suspicious
            }}
        )
    
    @staticmethod
    def get_user_payments(user_id, limit=10):
        """Get payment history for user"""
        payments = list(Payment.collection.find(
            {'user_id': ObjectId(user_id)}
        ).sort('created_at', -1).limit(limit))
        
        for payment in payments:
            Payment._format_payment(payment)
        
        return payments
    
    @staticmethod
    def get_payments_by_status(status, limit=50):
        """Get payments by status (for admin/analytics)"""
        payments = list(Payment.collection.find(
            {'status': status}
        ).sort('created_at', -1).limit(limit))
        
        for payment in payments:
            Payment._format_payment(payment)
        
        return payments
    
    @staticmethod
    def get_suspicious_payments():
        """Get suspicious payments for fraud detection"""
        payments = list(Payment.collection.find(
            {'is_suspicious': True}
        ).sort('fraud_score', -1))
        
        for payment in payments:
            Payment._format_payment(payment)
        
        return payments
    
    @staticmethod
    def get_revenue_analytics(start_date, end_date):
        """Get revenue analytics for date range"""
        pipeline = [
            {'$match': {
                'status': 'completed',
                'created_at': {'$gte': start_date, '$lte': end_date}
            }},
            {'$group': {
                '_id': None,
                'total_revenue': {'$sum': '$amount'},
                'total_transactions': {'$sum': 1},
                'average_transaction': {'$avg': '$amount'}
            }}
        ]
        
        result = list(Payment.collection.aggregate(pipeline))
        return result[0] if result else {}
    
    @staticmethod
    def _format_payment(payment):
        """Format payment for response"""
        payment['_id'] = str(payment['_id'])
        payment['order_id'] = str(payment['order_id'])
        payment['user_id'] = str(payment['user_id'])
        return payment