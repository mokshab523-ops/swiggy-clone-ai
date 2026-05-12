// Order Tracking Page
let orderData = null;
let map = null;
let deliveryMarker = null;
let userMarker = null;

function getOrderIdFromURL() {
    const params = new URLSearchParams(window.location.search);
    return params.get('order_id');
}

function loadOrderTracking() {
    const orderId = getOrderIdFromURL();
    
    if (!orderId) {
        showToast('No order ID provided', 'error');
        return;
    }
    
    showLoader(true);
    
    getOrder(orderId)
        .then(response => {
            showLoader(false);
            if (response.success) {
                orderData = response.order;
                renderOrderTracking(orderData);
                joinOrderRoom(orderId);
                initializeMap();
            } else {
                showToast('Order not found', 'error');
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading order:', error);
            showToast('Error loading order', 'error');
        });
}

function renderOrderTracking(order) {
    // Update status timeline
    const statusMap = {
        'pending': 'pending',
        'confirmed': 'confirmed',
        'preparing': 'preparing',
        'picked_up': 'picked_up',
        'delivered': 'delivered'
    };
    
    const currentStatus = order.status;
    document.querySelectorAll('.timeline-item').forEach(item => {
        if (item.dataset.status === currentStatus) {
            item.classList.add('active');
        }
    });
    
    // Update order info
    const orderInfoHtml = `
        <div style="margin-bottom: 15px;">
            <h4>Order #${order.order_number}</h4>
            <p>Total Amount: <strong>${formatPrice(order.total_amount)}</strong></p>
            <p>Estimated Delivery: <strong id="eta">30 minutes</strong></p>
        </div>
        <div>
            <h4>Items</h4>
            <ul>
                ${order.items.map(item => `<li>${item.name} x${item.quantity}</li>`).join('')}
            </ul>
        </div>
    `;
    
    const orderInfo = document.getElementById('order-info');
    if (orderInfo) {
        orderInfo.innerHTML = orderInfoHtml;
    }
    
    // Show delivery partner details if assigned
    if (order.delivery_partner_id) {
        const partnerSection = document.getElementById('delivery-partner-section');
        if (partnerSection) {
            partnerSection.style.display = 'block';
        }
    }
}

function initializeMap() {
    const mapElement = document.getElementById('tracking-map');
    if (!mapElement) return;
    
    // Initialize map with user location and restaurant location
    // This is a placeholder - in production, use actual Google Maps API
    if (typeof google !== 'undefined' && google.maps) {
        map = new google.maps.Map(mapElement, {
            zoom: 15,
            center: {
                lat: orderData.delivery_address?.latitude || 40.7128,
                lng: orderData.delivery_address?.longitude || -74.0060
            }
        });
        
        // Add user location marker
        userMarker = new google.maps.Marker({
            map: map,
            title: 'Your Location',
            position: {
                lat: orderData.delivery_address?.latitude || 40.7128,
                lng: orderData.delivery_address?.longitude || -74.0060
            }
        });
    } else {
        // Fallback if Google Maps not available
        mapElement.innerHTML = '<p style="padding: 20px; text-align: center; color: var(--text-light);">Map loading...</p>';
    }
}

function updateMap(latitude, longitude) {
    if (map && deliveryMarker) {
        deliveryMarker.setPosition({ lat: latitude, lng: longitude });
        map.panTo({ lat: latitude, lng: longitude });
    }
}

// Socket event handlers for real-time updates
if (typeof socket !== 'undefined' && socket) {
    socket.on('order_status_changed', (data) => {
        if (data.order_id === getOrderIdFromURL()) {
            updateStatusTimeline(data.status);
            showToast(`Order status: ${data.status}`, 'info');
        }
    });
    
    socket.on('delivery_location', (data) => {
        if (data.order_id === getOrderIdFromURL()) {
            updateMap(data.latitude, data.longitude);
        }
    });
}

function updateStatusTimeline(status) {
    document.querySelectorAll('.timeline-item').forEach(item => {
        const itemStatus = item.dataset.status;
        if (itemStatus === status) {
            item.classList.add('active');
        }
    });
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    loadOrderTracking();
    
    const contactBtn = document.getElementById('contact-delivery-btn');
    if (contactBtn) {
        contactBtn.addEventListener('click', () => {
            showToast('Calling delivery partner...', 'info');
        });
    }
});
