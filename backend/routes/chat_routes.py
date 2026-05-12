from flask import Blueprint, request, jsonify
from models.user_model import User
from middleware.auth_middleware import token_required
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
chat_bp = Blueprint('chat', __name__, url_prefix='/api/chat')

@chat_bp.route('/send-message', methods=['POST'])
@token_required
def send_chat_message():
    """Send chat message to chatbot"""
    try:
        user = request.current_user
        data = request.get_json()
        
        message = data.get('message')
        message_type = data.get('type', 'text')  # text, order_tracking, refund_request
        
        if not message:
            return jsonify({'error': 'Message required'}), 400
        
        # Simple AI chatbot responses
        response = generate_chatbot_response(message, message_type, user)
        
        return jsonify({
            'success': True,
            'user_message': message,
            'bot_response': response,
            'timestamp': datetime.utcnow().isoformat()
        }), 200
        
    except Exception as e:
        logger.error(f"Send chat message error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@chat_bp.route('/track-order', methods=['POST'])
@token_required
def track_order_via_chat():
    """Track order through chatbot"""
    try:
        data = request.get_json()
        order_number = data.get('order_number')
        
        if not order_number:
            return jsonify({'error': 'Order number required'}), 400
        
        from models.order_model import Order
        order = Order.find_by_order_number(order_number)
        
        if not order:
            return jsonify({
                'success': True,
                'bot_response': f"I couldn't find order {order_number}. Could you please verify the order number?"
            }), 200
        
        response = f"Order {order_number} is currently {Order.ORDER_STATUS.get(order['status'])}."
        if order.get('delivery_partner_location'):
            response += " Your delivery partner is on the way!"
        
        return jsonify({
            'success': True,
            'bot_response': response,
            'order': order
        }), 200
        
    except Exception as e:
        logger.error(f"Track order via chat error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

@chat_bp.route('/request-refund', methods=['POST'])
@token_required
def request_refund_via_chat():
    """Request refund through chatbot"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        reason = data.get('reason')
        
        if not order_id or not reason:
            return jsonify({'error': 'Order ID and reason required'}), 400
        
        from models.order_model import Order
        from models.payment_model import Payment
        
        order = Order.find_by_id(order_id)
        if not order:
            return jsonify({
                'success': True,
                'bot_response': 'Order not found. Please check the order ID.'
            }), 200
        
        # Get payment
        payment = Payment.find_by_order_id(order_id)
        if payment:
            Payment.initiate_refund(payment['_id'], payment['amount'], reason)
        
        response = f"Your refund request for order {order.get('order_number')} has been submitted. We'll process it within 5-7 business days."
        
        return jsonify({
            'success': True,
            'bot_response': response
        }), 200
        
    except Exception as e:
        logger.error(f"Request refund via chat error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

def generate_chatbot_response(message, message_type, user):
    """Generate chatbot response using simple NLP"""
    message_lower = message.lower()
    
    # Order tracking
    if 'track' in message_lower or 'where' in message_lower or 'status' in message_lower:
        return "I can help you track your order! Please provide your order number or order ID."
    
    # Refund requests
    if 'refund' in message_lower or 'money back' in message_lower:
        return "I can help you with refunds. Please provide your order number and reason for refund request."
    
    # Restaurant recommendations
    if 'recommend' in message_lower or 'suggest' in message_lower:
        return "I can recommend restaurants based on your preferences. What type of cuisine do you prefer?"
    
    # FAQs
    if 'how' in message_lower or 'what' in message_lower:
        if 'delivery' in message_lower:
            return "Delivery usually takes 30-45 minutes depending on your location. You can track your order in real-time."
        elif 'payment' in message_lower:
            return "We accept multiple payment methods: UPI, Cards, Wallets, and Net Banking."
        elif 'cancel' in message_lower:
            return "You can cancel orders before the restaurant confirms. After confirmation, cancellation fees may apply."
    
    # Default response
    return f"Thanks for your message! I'm here to help with order tracking, refunds, and restaurant recommendations. How can I assist you?"
