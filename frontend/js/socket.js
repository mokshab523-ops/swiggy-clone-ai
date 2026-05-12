// Socket.IO Real-time Communication
let socket = null;

function initializeSocket() {
    socket = io(SOCKET_URL, {
        auth: {
            token: getToken()
        },
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5
    });

    // Connection events
    socket.on('connect', () => {
        console.log('✓ Connected to server');
        showToast('Connected to server', 'success');
    });

    socket.on('disconnect', () => {
        console.log('✗ Disconnected from server');
        showToast('Disconnected from server', 'warning');
    });

    socket.on('error', (error) => {
        console.error('Socket error:', error);
    });

    // Order events
    socket.on('order_status_changed', (data) => {
        console.log('Order status updated:', data);
        updateOrderStatus(data);
    });

    socket.on('delivery_location', (data) => {
        console.log('Delivery location updated:', data);
        updateDeliveryLocation(data);
    });

    socket.on('cart_changed', (data) => {
        console.log('Cart updated:', data);
        updateCart(data.items);
    });

    socket.on('notification_received', (data) => {
        console.log('Notification received:', data);
        showToast(data.message, 'info');
    });

    socket.on('payment_success', (data) => {
        console.log('Payment successful:', data);
        showToast('Payment successful!', 'success');
        setTimeout(() => {
            window.location.href = 'order-tracking.html?order_id=' + data.order_id;
        }, 1500);
    });

    socket.on('fraud_detected', (data) => {
        console.log('Fraud detected:', data);
        showToast('Suspicious activity detected. Please verify your transaction.', 'warning');
    });
}

function joinOrderRoom(orderId) {
    if (socket) {
        socket.emit('join_order', {
            order_id: orderId,
            user_id: getUser()?._id
        });
    }
}

function updateOrderStatus(data) {
    const orderElements = document.querySelectorAll(`[data-order-id="${data.order_id}"]`);
    orderElements.forEach(el => {
        const statusEl = el.querySelector('.order-status');
        if (statusEl) {
            statusEl.textContent = data.status;
            statusEl.className = `order-status ${data.status}`;
        }
    });

    // Update timeline if on order tracking page
    const timelineItems = document.querySelectorAll('[data-status]');
    timelineItems.forEach(item => {
        if (item.dataset.status === data.status) {
            item.classList.add('active');
        }
    });
}

function updateDeliveryLocation(data) {
    console.log('Delivery location:', data.latitude, data.longitude);
    // Update map if Google Maps is available
    if (window.map && typeof window.updateMap === 'function') {
        window.updateMap(data.latitude, data.longitude);
    }
}

function updateCart(items) {
    renderCart(items);
    updateCartCount();
}

// Initialize socket when authenticated
if (isAuthenticated()) {
    initializeSocket();
}

// Reinitialize socket on page load
document.addEventListener('DOMContentLoaded', () => {
    if (isAuthenticated() && !socket) {
        initializeSocket();
    }
});

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
    if (socket) {
        socket.disconnect();
    }
});

// Reconnect on visibility change
document.addEventListener('visibilitychange', () => {
    if (document.hidden && socket) {
        socket.disconnect();
    } else if (!document.hidden && isAuthenticated()) {
        if (!socket || !socket.connected) {
            initializeSocket();
        }
    }
});