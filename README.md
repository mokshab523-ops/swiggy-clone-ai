# 🍕 Swiggy Clone - AI-Powered Food Delivery Platform

A production-level real-time food delivery web application inspired by Swiggy with AI-powered features, modern UI/UX, scalable backend architecture, and live order synchronization.

## 🚀 Features

### Core Features
- ✅ Real-time Order Management (WebSocket/Socket.IO)
- ✅ Live Order Tracking with GPS
- ✅ AI Voice Ordering System
- ✅ AI Chatbot Support
- ✅ Secure Payment Gateway (Razorpay + Stripe)
- ✅ AI Fraud Detection
- ✅ Real-time Dashboard & Analytics
- ✅ Admin Panel with Live Monitoring
- ✅ Group Ordering System
- ✅ Delivery Partner Module

### Tech Stack

**Frontend:**
- HTML5, CSS3, JavaScript
- Socket.IO Client
- Chart.js for Analytics
- Fetch API & AJAX

**Backend:**
- Python Flask
- Flask-SocketIO
- MongoDB with PyMongo
- JWT Authentication
- Razorpay & Stripe Integration

**Database:**
- MongoDB

## 📁 Project Structure

```
swiggy-clone-ai/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── requirements.txt
│   ├── routes/
│   │   ├── auth_routes.py
│   │   ├── order_routes.py
│   │   ├── restaurant_routes.py
│   │   ├── payment_routes.py
│   │   └── admin_routes.py
│   ├── controllers/
│   │   ├── auth_controller.py
│   │   ├── order_controller.py
│   │   ├── restaurant_controller.py
│   │   └── admin_controller.py
│   ├── models/
│   │   ├── user_model.py
│   │   ├── order_model.py
│   │   ├── restaurant_model.py
│   │   └── payment_model.py
│   ├── middleware/
│   │   └── auth_middleware.py
│   ├── utils/
│   │   ├── decorators.py
│   │   ├── validators.py
│   │   └── helpers.py
│   └── database/
│       └── db.py
├── frontend/
│   ├── index.html
│   ├── login.html
│   ├── signup.html
│   ├── dashboard.html
│   ├── order-tracking.html
│   ├── admin.html
│   ├── css/
│   │   ├── style.css
│   │   ├── dashboard.css
│   │   ├── admin.css
│   │   └── animations.css
│   ├── js/
│   │   ├── app.js
│   │   ├── socket.js
│   │   ├── auth.js
│   │   ├── cart.js
│   │   ├── api.js
│   │   ├── chatbot.js
│   │   └── voice-ordering.js
│   └── assets/
│       ├── images/
│       └── icons/
└── docs/
    └── API_DOCUMENTATION.md
```

## 🔧 Installation & Setup

### Backend Setup

```bash
# Clone repository
git clone https://github.com/mokshab523-ops/swiggy-clone-ai.git
cd swiggy-clone-ai/backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Update .env with your credentials:
MONGODB_URI=your_mongodb_connection_string
JWT_SECRET=your_secret_key
RAZORPAY_KEY_ID=your_razorpay_key
RAZORPAY_KEY_SECRET=your_razorpay_secret

# Run backend
python app.py
```

### Frontend Setup

```bash
# Navigate to frontend
cd ../frontend

# Start local server (Python)
python -m http.server 8000

# Or use Live Server extension in VS Code
# Open http://localhost:8000
```

## 🔐 Authentication

### Signup Validations
- ✅ First name: Alphabets only
- ✅ Last name: Alphabets only
- ✅ Email: Valid email format with @
- ✅ Phone: 10-digit Indian phone number
- ✅ Password: Uppercase + Lowercase + Number + Special Character

### Security Features
- ✅ Password hashing (bcrypt)
- ✅ JWT authentication
- ✅ Session persistence
- ✅ Protected routes
- ✅ Auto-login after refresh
- ✅ Duplicate account prevention

## 📡 Real-Time Socket Events

```javascript
// Client to Server Events
'place_order' - Place new order
'cancel_order' - Cancel existing order
'track_order' - Get order location updates
'update_cart' - Real-time cart updates

// Server to Client Events
'new_order' - New order placed
'order_accepted' - Restaurant accepted order
'preparing_order' - Food being prepared
'out_for_delivery' - Order picked up for delivery
'order_delivered' - Order delivered
'payment_success' - Payment confirmed
'fraud_detected' - Fraud alert
'delivery_partner_assigned' - Delivery person assigned
```

## 💳 Payment Integration

Supported Payment Methods:
- ✅ Razorpay (UPI, Card, Wallet)
- ✅ Stripe (International Cards)
- ✅ Cashback & Coupon System
- ✅ Secure Transaction Verification

## 🤖 AI Features

### 1. Voice Ordering
- Speech recognition for food search
- Voice-based order placement
- Multi-language support

### 2. AI Chatbot
- Order support & tracking
- Refund assistance
- Restaurant recommendations
- FAQ automation

### 3. Fraud Detection
- Suspicious transaction detection
- Fake refund prevention
- Order behavior analysis
- Real-time fraud alerts

## 📊 Dashboard Features

### User Dashboard
- Live order tracking
- Order history
- Saved addresses
- Payment methods
- Wishlist

### Restaurant Dashboard
- Real-time order notifications
- Revenue analytics
- Food item management
- Restaurant settings

### Admin Dashboard
- Revenue monitoring
- Live order tracking
- Fraud alerts
- User management
- Restaurant management
- Real-time analytics & charts

## 🚚 Delivery Tracking

- Real-time GPS tracking
- Live delivery partner location
- Dynamic ETA calculation
- Route optimization
- Multi-order batching

## 📱 Responsive Design

- Mobile-first approach
- Swiggy-inspired Orange + White theme
- Smooth animations and transitions
- Professional restaurant cards
- Floating cart sidebar
- Modern hero section

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
# Use browser developer tools console
```

## 📚 API Documentation

Full API documentation available in `docs/API_DOCUMENTATION.md`

## 🔒 Security Best Practices

- ✅ Environment variables for sensitive data
- ✅ Input validation and sanitization
- ✅ CORS configuration
- ✅ Rate limiting
- ✅ Secure headers
- ✅ SQL/NoSQL injection prevention
- ✅ XSS protection

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is open source and available under the MIT License.

## 📧 Support

For support, email: support@swiggyclone.com

## 🎯 Roadmap

- [ ] Mobile app (React Native)
- [ ] Advanced analytics
- [ ] Machine learning recommendations
- [ ] Subscription model
- [ ] Dark mode
- [ ] Multi-language support

---

**Built with ❤️ for food delivery lovers**
