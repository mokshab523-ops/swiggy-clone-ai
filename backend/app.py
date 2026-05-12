import os
from flask import Flask
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS
from config import Config
from database.db import Database
import logging
from datetime import datetime
from bson.objectid import ObjectId

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_app(config_name='development'):
    """Application factory"""
    
    app = Flask(__name__)
    
    # Load configuration
    if config_name == 'production':
        from config import ProductionConfig
        app.config.from_object(ProductionConfig)
    elif config_name == 'testing':
        from config import TestingConfig
        app.config.from_object(TestingConfig)
    else:
        from config import DevelopmentConfig
        app.config.from_object(DevelopmentConfig)
    
    # Initialize CORS
    CORS(app, resources={r"/api/*": {"origins": app.config['CORS_ORIGINS']}})
    
    # Initialize SocketIO
    socketio = SocketIO(
        app,
        cors_allowed_origins=app.config['CORS_ORIGINS'],
        async_mode='eventlet',
        ping_timeout=60,
        ping_interval=25
    )
    
    # Initialize Database
    Database.get_instance()
    
    # Create upload folder
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    
    # Register blueprints
    from routes.auth_routes import auth_bp
    from routes.restaurant_routes import restaurant_bp
    from routes.order_routes import order_bp
    from routes.payment_routes import payment_bp
    from routes.admin_routes import admin_bp
    from routes.chat_routes import chat_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(restaurant_bp)
    app.register_blueprint(order_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(chat_bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        db_status = Database.health_check()
        return {
            'status': 'healthy' if db_status else 'unhealthy',
            'database': 'connected' if db_status else 'disconnected',
            'timestamp': datetime.utcnow().isoformat()
        }, 200 if db_status else 503
    
    # Socket.IO events
    @socketio.on('connect')
    def handle_connect(auth):
        logger.info(f"Client connected: {auth}")
        emit('response', {'data': 'Connected to server'})
    
    @socketio.on('disconnect')
    def handle_disconnect():
        logger.info('Client disconnected')
    
    @socketio.on('join_order')
    def on_join_order(data):
        """Join order tracking room"""
        order_id = data.get('order_id')
        user_id = data.get('user_id')
        
        room = f"order_{order_id}"
        join_room(room)
        
        emit('order_joined', {
            'order_id': order_id,
            'user_id': user_id,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
    
    @socketio.on('order_update')
    def broadcast_order_update(data):
        """Broadcast order status update"""
        order_id = data.get('order_id')
        status = data.get('status')
        
        room = f"order_{order_id}"
        emit('order_status_changed', {
            'order_id': order_id,
            'status': status,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
    
    @socketio.on('delivery_location_update')
    def broadcast_location_update(data):
        """Broadcast delivery partner location"""
        order_id = data.get('order_id')
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        room = f"order_{order_id}"
        emit('delivery_location', {
            'order_id': order_id,
            'latitude': latitude,
            'longitude': longitude,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
    
    @socketio.on('cart_update')
    def broadcast_cart_update(data):
        """Broadcast real-time cart updates"""
        user_id = data.get('user_id')
        cart_items = data.get('items')
        
        room = f"cart_{user_id}"
        join_room(room)
        emit('cart_changed', {
            'items': cart_items,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
    
    @socketio.on('notification')
    def send_notification(data):
        """Send real-time notification"""
        user_id = data.get('user_id')
        message = data.get('message')
        
        room = f"user_{user_id}"
        emit('notification_received', {
            'message': message,
            'timestamp': datetime.utcnow().isoformat()
        }, room=room)
    
    return app, socketio

if __name__ == '__main__':
    app, socketio = create_app()
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)