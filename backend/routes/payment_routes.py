from flask import Blueprint, request, jsonify
from models.payment_model import Payment
from models.order_model import Order
from middleware.auth_middleware import token_required
from utils.fraud_detection import FraudDetection
import logging
import razorpay

logger = logging.getLogger(__name__)
payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# Initialize Razorpay
client = razorpay.Client(auth=("your_key_id", "your_key_secret"))

@payment_bp.route('/initiate', methods=['POST'])
@token_required
def initiate_payment():
    """Initiate payment for order"""
    try:
        user = request.current_user
        data = request.get_json()
        
        order_id = data.get('order_id')
        payment_method = data.get('payment_method', 'razorpay')
        
        if not order_id:
            return jsonify({'error': 'Order ID required'}), 400
        
        # Get order
        order = Order.find_by_id(order_id)
        if not order:
            return jsonify({'error': 'Order not found'}), 404
        
        if str(order['user_id']) != str(user['_id']):
            return jsonify({'error': 'Unauthorized'}), 403
        
        # Create payment record
        payment_data = {
            'order_id': order_id,
            'user_id': user['_id'],
            'amount': order['total_amount'],
            'payment_method': payment_method,
            'ip_address': request.remote_addr,
            'user_agent': request.headers.get('User-Agent')
        }
        
        payment_result = Payment.create(payment_data)
        payment_id = payment_result['payment_id']
        
        # Fraud Detection
        fraud_analysis = FraudDetection.analyze_transaction(payment_data, user)
        Payment.update_fraud_score(payment_id, fraud_analysis['fraud_score'], fraud_analysis['is_suspicious'])
        
        if fraud_analysis['is_suspicious']:
            FraudDetection.log_fraud_alert(payment_id, fraud_analysis)
            if fraud_analysis['recommendation'] == 'block_transaction':
                return jsonify({
                    'error': 'Transaction blocked due to suspicious activity',
                    'fraud_score': fraud_analysis['fraud_score']
                }), 403
        
        # Create Razorpay order
        if payment_method == 'razorpay':
            razorpay_order = client.order.create(dict(
                amount=int(order['total_amount'] * 100),  # Amount in paise
                currency='INR',
                receipt=f"order_{order_id}",
                payment_capture='1'
            ))
            
            return jsonify({
                'success': True,
                'payment_id': payment_id,
                'razorpay_order_id': razorpay_order['id'],
                'amount': order['total_amount'],
                'fraud_score': fraud_analysis['fraud_score']
            }), 200
        
        return jsonify({
            'success': True,
            'payment_id': payment_id,
            'amount': order['total_amount']
        }), 200
        
    except Exception as e:
        logger.error(f"Initiate payment error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/verify', methods=['POST'])
@token_required
def verify_payment():
    """Verify payment"""
    try:
        data = request.get_json()
        
        payment_id = data.get('payment_id')
        razorpay_order_id = data.get('razorpay_order_id')
        razorpay_payment_id = data.get('razorpay_payment_id')
        razorpay_signature = data.get('razorpay_signature')
        
        if not all([payment_id, razorpay_payment_id]):
            return jsonify({'error': 'Missing payment details'}), 400
        
        # In production, verify Razorpay signature
        # For now, mark as completed
        
        if Payment.update_status(payment_id, 'completed', razorpay_payment_id):
            # Update order status
            payment = Payment.find_by_id(payment_id)
            order_id = str(payment['order_id'])
            Order.update_payment_status(order_id, 'completed', razorpay_payment_id)
            Order.update_status(order_id, 'confirmed')
            
            return jsonify({
                'success': True,
                'message': 'Payment verified successfully',
                'payment_id': payment_id
            }), 200
        
        return jsonify({'error': 'Payment verification failed'}), 400
        
    except Exception as e:
        logger.error(f"Verify payment error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/<payment_id>/status', methods=['GET'])
@token_required
def get_payment_status(payment_id):
    """Get payment status"""
    try:
        payment = Payment.find_by_id(payment_id)
        
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        return jsonify({
            'success': True,
            'payment': payment
        }), 200
        
    except Exception as e:
        logger.error(f"Get payment status error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@payment_bp.route('/<payment_id>/refund', methods=['POST'])
@token_required
def request_refund(payment_id):
    """Request refund"""
    try:
        user = request.current_user
        data = request.get_json()
        
        payment = Payment.find_by_id(payment_id)
        if not payment:
            return jsonify({'error': 'Payment not found'}), 404
        
        if str(payment['user_id']) != str(user['_id']):
            return jsonify({'error': 'Unauthorized'}), 403
        
        if payment['status'] != 'completed':
            return jsonify({'error': 'Cannot refund incomplete payment'}), 400
        
        reason = data.get('reason', 'User requested refund')
        refund_amount = data.get('refund_amount', payment['amount'])
        
        if Payment.initiate_refund(payment_id, refund_amount, reason):
            return jsonify({
                'success': True,
                'message': 'Refund request initiated',
                'refund_amount': refund_amount
            }), 200
        
        return jsonify({'error': 'Failed to initiate refund'}), 400
        
    except Exception as e:
        logger.error(f"Request refund error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500