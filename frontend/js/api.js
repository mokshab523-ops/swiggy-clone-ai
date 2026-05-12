// API Functions for Restaurants and Orders

// Restaurant API
function getNearbyRestaurants(latitude, longitude, radius = 5) {
    return fetch(
        `${API_BASE_URL}/restaurant/nearby?latitude=${latitude}&longitude=${longitude}&radius=${radius}`
    ).then(res => res.json());
}

function getAllRestaurants(page = 1, perPage = 10) {
    return fetch(
        `${API_BASE_URL}/restaurant/all?page=${page}&per_page=${perPage}`
    ).then(res => res.json());
}

function getRestaurantDetails(restaurantId) {
    return fetch(`${API_BASE_URL}/restaurant/${restaurantId}`)
        .then(res => res.json());
}

function searchRestaurants(query) {
    return fetch(
        `${API_BASE_URL}/restaurant/search?q=${encodeURIComponent(query)}`
    ).then(res => res.json());
}

function getRestaurantsByCategory(category) {
    return fetch(`${API_BASE_URL}/restaurant/category/${category}`)
        .then(res => res.json());
}

// Order API
function createOrder(orderData) {
    return fetch(`${API_BASE_URL}/order/create`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify(orderData)
    })
    .then(res => res.json());
}

function getOrder(orderId) {
    return fetch(`${API_BASE_URL}/order/${orderId}`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function getOrderHistory(status = null) {
    let url = `${API_BASE_URL}/order/user/history`;
    if (status) {
        url += `?status=${status}`;
    }
    return fetch(url, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function getOrderStatus(orderId) {
    return fetch(`${API_BASE_URL}/order/${orderId}/status`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function cancelOrder(orderId, reason) {
    return fetch(`${API_BASE_URL}/order/${orderId}/cancel`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ reason })
    })
    .then(res => res.json());
}

function rateOrder(orderId, rating, review) {
    return fetch(`${API_BASE_URL}/order/${orderId}/rate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ rating, review })
    })
    .then(res => res.json());
}

// Payment API
function initiatePayment(orderId, paymentMethod = 'razorpay') {
    return fetch(`${API_BASE_URL}/payment/initiate`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            order_id: orderId,
            payment_method: paymentMethod
        })
    })
    .then(res => res.json());
}

function verifyPayment(paymentId, razorpayOrderId, razorpayPaymentId, razorpaySignature) {
    return fetch(`${API_BASE_URL}/payment/verify`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            payment_id: paymentId,
            razorpay_order_id: razorpayOrderId,
            razorpay_payment_id: razorpayPaymentId,
            razorpay_signature: razorpaySignature
        })
    })
    .then(res => res.json());
}

function getPaymentStatus(paymentId) {
    return fetch(`${API_BASE_URL}/payment/${paymentId}/status`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function requestRefund(paymentId, reason, refundAmount) {
    return fetch(`${API_BASE_URL}/payment/${paymentId}/refund`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            reason,
            refund_amount: refundAmount
        })
    })
    .then(res => res.json());
}

// Chatbot API
function sendChatMessage(message, messageType = 'text') {
    return fetch(`${API_BASE_URL}/chat/send-message`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            message,
            type: messageType
        })
    })
    .then(res => res.json());
}

function trackOrderViaChat(orderNumber) {
    return fetch(`${API_BASE_URL}/chat/track-order`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({ order_number: orderNumber })
    })
    .then(res => res.json());
}

function requestRefundViaChat(orderId, reason) {
    return fetch(`${API_BASE_URL}/chat/request-refund`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            order_id: orderId,
            reason
        })
    })
    .then(res => res.json());
}

// Admin API
function getAdminDashboard() {
    return fetch(`${API_BASE_URL}/admin/dashboard`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function getAllOrders(status = null, page = 1) {
    let url = `${API_BASE_URL}/admin/orders?page=${page}`;
    if (status) {
        url += `&status=${status}`;
    }
    return fetch(url, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function getAllUsers() {
    return fetch(`${API_BASE_URL}/admin/users`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function getFraudAlerts() {
    return fetch(`${API_BASE_URL}/admin/fraud-alerts`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}

function reviewFraudAlert(alertId, action, reason) {
    return fetch(`${API_BASE_URL}/admin/fraud-alerts/${alertId}/review`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getToken()}`
        },
        body: JSON.stringify({
            action,
            reason
        })
    })
    .then(res => res.json());
}

function getRevenueAnalytics(days = 30) {
    return fetch(`${API_BASE_URL}/admin/analytics/revenue?days=${days}`, {
        headers: {
            'Authorization': `Bearer ${getToken()}`
        }
    })
    .then(res => res.json());
}