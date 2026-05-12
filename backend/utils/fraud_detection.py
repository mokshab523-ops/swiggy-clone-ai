from datetime import datetime, timedelta
from models.payment_model import Payment
from models.order_model import Order
from database.db import Database
from bson.objectid import ObjectId
import logging

logger = logging.getLogger(__name__)

class FraudDetection:
    """AI-Powered Fraud Detection System"""
    
    SUSPICIOUS_SCORE_THRESHOLD = 70  # Flag if score > 70
    
    @staticmethod
    def analyze_transaction(payment_data, user_history=None):
        """Analyze transaction for fraud indicators"""
        fraud_score = 0
        flags = []
        
        # Check 1: Multiple failed attempts in short time
        if FraudDetection._check_failed_attempts(payment_data.get('user_id')):
            fraud_score += 20
            flags.append('multiple_failed_attempts')
        
        # Check 2: Unusual amount
        if FraudDetection._check_unusual_amount(payment_data.get('user_id'), payment_data.get('amount')):
            fraud_score += 15
            flags.append('unusual_amount')
        
        # Check 3: Rapid transactions
        if FraudDetection._check_rapid_transactions(payment_data.get('user_id')):
            fraud_score += 25
            flags.append('rapid_transactions')
        
        # Check 4: New payment method
        if FraudDetection._check_new_payment_method(payment_data.get('user_id'), payment_data.get('payment_method')):
            fraud_score += 10
            flags.append('new_payment_method')
        
        # Check 5: International transaction (if applicable)
        if payment_data.get('country') and payment_data['country'] != 'IN':
            fraud_score += 20
            flags.append('international_transaction')
        
        # Check 6: Refund pattern
        if FraudDetection._check_refund_pattern(payment_data.get('user_id')):
            fraud_score += 30
            flags.append('suspicious_refund_pattern')
        
        is_suspicious = fraud_score > FraudDetection.SUSPICIOUS_SCORE_THRESHOLD
        
        return {
            'fraud_score': fraud_score,
            'is_suspicious': is_suspicious,
            'flags': flags,
            'recommendation': FraudDetection._get_recommendation(fraud_score)
        }
    
    @staticmethod
    def _check_failed_attempts(user_id):
        """Check for multiple failed payment attempts"""
        collection = Database.get_collection('payments')
        
        # Count failed payments in last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        failed_count = collection.count_documents({
            'user_id': ObjectId(user_id),
            'status': 'failed',
            'created_at': {'$gte': one_hour_ago}
        })
        
        return failed_count >= 3
    
    @staticmethod
    def _check_unusual_amount(user_id, amount):
        """Check if transaction amount is unusual for user"""
        collection = Database.get_collection('payments')
        
        # Get average transaction amount for user
        result = list(collection.aggregate([
            {'$match': {'user_id': ObjectId(user_id), 'status': 'completed'}},
            {'$group': {'_id': None, 'avg_amount': {'$avg': '$amount'}}}
        ]))
        
        if not result:
            return False
        
        avg_amount = result[0]['avg_amount']
        # Flag if transaction is 3x higher than average
        return amount > avg_amount * 3
    
    @staticmethod
    def _check_rapid_transactions(user_id):
        """Check for too many transactions in short time"""
        collection = Database.get_collection('payments')
        
        # Count transactions in last 5 minutes
        five_minutes_ago = datetime.utcnow() - timedelta(minutes=5)
        count = collection.count_documents({
            'user_id': ObjectId(user_id),
            'created_at': {'$gte': five_minutes_ago}
        })
        
        return count >= 5
    
    @staticmethod
    def _check_new_payment_method(user_id, payment_method):
        """Check if payment method is new to user"""
        collection = Database.get_collection('payments')
        
        # Check if user has used this payment method before
        existing = collection.find_one({
            'user_id': ObjectId(user_id),
            'payment_method': payment_method,
            'status': 'completed'
        })
        
        return existing is None
    
    @staticmethod
    def _check_refund_pattern(user_id):
        """Check for suspicious refund patterns"""
        collection = Database.get_collection('payments')
        
        # Get total refund percentage
        result = list(collection.aggregate([
            {'$match': {'user_id': ObjectId(user_id)}},
            {'$group': {
                '_id': None,
                'total_refunds': {'$sum': {'$cond': [{'$eq': ['$status', 'refunded']}, 1, 0]}},
                'total_transactions': {'$sum': 1}
            }}
        ]))
        
        if not result or result[0]['total_transactions'] == 0:
            return False
        
        refund_percent = (result[0]['total_refunds'] / result[0]['total_transactions']) * 100
        return refund_percent > 30  # Flag if >30% refund rate
    
    @staticmethod
    def _get_recommendation(fraud_score):
        """Get action recommendation based on fraud score"""
        if fraud_score >= 80:
            return 'block_transaction'
        elif fraud_score >= 70:
            return 'require_verification'
        elif fraud_score >= 50:
            return 'monitor'
        else:
            return 'allow'
    
    @staticmethod
    def log_fraud_alert(payment_id, fraud_analysis):
        """Log fraud alert for admin dashboard"""
        collection = Database.get_collection('fraud_alerts')
        
        alert = {
            'payment_id': ObjectId(payment_id),
            'fraud_score': fraud_analysis['fraud_score'],
            'flags': fraud_analysis['flags'],
            'recommendation': fraud_analysis['recommendation'],
            'timestamp': datetime.utcnow(),
            'reviewed': False,
            'action_taken': None
        }
        
        collection.insert_one(alert)
        logger.warning(f"Fraud Alert: Payment {payment_id} - Score: {fraud_analysis['fraud_score']}")