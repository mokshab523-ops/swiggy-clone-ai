// Dashboard Functionality
let currentSection = 'orders';

function switchSection(sectionName) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active from sidebar links
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.classList.remove('active');
    });
    
    // Show selected section
    const section = document.getElementById(sectionName);
    if (section) {
        section.classList.add('active');
    }
    
    // Mark sidebar link as active
    const link = document.querySelector(`.sidebar-link[data-section="${sectionName}"]`);
    if (link) {
        link.classList.add('active');
    }
    
    currentSection = sectionName;
    
    // Load data for section
    if (sectionName === 'orders') {
        loadOrders();
    } else if (sectionName === 'profile') {
        loadProfile();
    } else if (sectionName === 'addresses') {
        loadAddresses();
    } else if (sectionName === 'favorites') {
        loadFavorites();
    }
}

function loadOrders(status = null) {
    showLoader(true);
    getOrderHistory(status)
        .then(response => {
            showLoader(false);
            if (response.success) {
                renderOrders(response.orders);
            } else {
                showToast('Failed to load orders', 'error');
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading orders:', error);
            showToast('Error loading orders', 'error');
        });
}

function renderOrders(orders) {
    const container = document.getElementById('orders-container');
    if (!container) return;
    
    if (orders.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 40px; color: var(--text-light);">No orders yet. <a href="index.html">Order now</a></p>';
        return;
    }
    
    container.innerHTML = orders.map(order => `
        <div class="order-card" onclick="showOrderDetails('${order._id}')">
            <div class="order-header">
                <div class="order-number">Order #${order.order_number}</div>
                <div class="order-status ${order.status}">${order.status.toUpperCase()}</div>
            </div>
            <div class="order-details">
                <div class="order-detail">
                    <div class="order-detail-label">Restaurant</div>
                    <div class="order-detail-value">${order.restaurant_id || 'Restaurant'}</div>
                </div>
                <div class="order-detail">
                    <div class="order-detail-label">Amount</div>
                    <div class="order-detail-value">${formatPrice(order.total_amount)}</div>
                </div>
                <div class="order-detail">
                    <div class="order-detail-label">Date</div>
                    <div class="order-detail-value">${formatDate(order.created_at)}</div>
                </div>
                <div class="order-detail">
                    <div class="order-detail-label">Items</div>
                    <div class="order-detail-value">${order.items.length} items</div>
                </div>
            </div>
        </div>
    `).join('');
}

function loadProfile() {
    showLoader(true);
    getProfile()
        .then(response => {
            showLoader(false);
            if (response.success) {
                renderProfile(response.user);
            } else {
                showToast('Failed to load profile', 'error');
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading profile:', error);
            showToast('Error loading profile', 'error');
        });
}

function renderProfile(user) {
    document.getElementById('profile-first-name').value = user.first_name || '';
    document.getElementById('profile-last-name').value = user.last_name || '';
    document.getElementById('profile-email').value = user.email || '';
    document.getElementById('profile-phone').value = user.phone || '';
}

function loadAddresses() {
    const user = getUser();
    const container = document.getElementById('addresses-container');
    
    if (!user || !user.addresses || user.addresses.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 20px; color: var(--text-light);">No addresses saved yet.</p>';
        return;
    }
    
    container.innerHTML = user.addresses.map((address, idx) => `
        <div class="address-card">
            <div class="address-label">${address.label}</div>
            <div class="address-text">${address.address}</div>
            <div class="address-actions">
                <button onclick="editAddress(${idx})">Edit</button>
                <button onclick="deleteAddress(${idx})">Delete</button>
            </div>
        </div>
    `).join('');
}

function loadFavorites() {
    const user = getUser();
    const container = document.getElementById('favorites-container');
    
    if (!user || !user.wishlist || user.wishlist.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 20px; color: var(--text-light);">No favorite restaurants yet.</p>';
        return;
    }
    
    // Render favorite restaurants
    showToast('Loading favorites...', 'info');
}

function showOrderDetails(orderId) {
    showLoader(true);
    getOrder(orderId)
        .then(response => {
            showLoader(false);
            if (response.success) {
                renderOrderDetail(response.order);
                openModal('order-detail-modal');
            } else {
                showToast('Failed to load order details', 'error');
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading order:', error);
            showToast('Error loading order', 'error');
        });
}

function renderOrderDetail(order) {
    const content = document.getElementById('order-detail-content');
    
    const itemsHtml = order.items.map(item => `
        <tr>
            <td>${item.name}</td>
            <td>x${item.quantity}</td>
            <td>${formatPrice(item.price * item.quantity)}</td>
        </tr>
    `).join('');
    
    content.innerHTML = `
        <div class="detail-section">
            <div class="detail-item">
                <span class="detail-label">Order Number:</span>
                <span class="detail-value">${order.order_number}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Status:</span>
                <span class="detail-value order-status ${order.status}">${order.status.toUpperCase()}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Date:</span>
                <span class="detail-value">${formatDate(order.created_at)} ${formatTime(order.created_at)}</span>
            </div>
        </div>
        
        <div class="detail-section">
            <h4>Items</h4>
            <table style="width: 100%; border-collapse: collapse;">
                <thead>
                    <tr style="border-bottom: 1px solid var(--border-color);">
                        <th style="text-align: left; padding: 8px;">Item</th>
                        <th style="text-align: center; padding: 8px;">Qty</th>
                        <th style="text-align: right; padding: 8px;">Price</th>
                    </tr>
                </thead>
                <tbody>
                    ${itemsHtml}
                </tbody>
            </table>
        </div>
        
        <div class="detail-section">
            <div class="detail-item">
                <span class="detail-label">Subtotal:</span>
                <span class="detail-value">${formatPrice(order.subtotal)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Tax:</span>
                <span class="detail-value">${formatPrice(order.tax)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label">Delivery Charge:</span>
                <span class="detail-value">${formatPrice(order.delivery_charge)}</span>
            </div>
            <div class="detail-item">
                <span class="detail-label"><strong>Total:</strong></span>
                <span class="detail-value"><strong>${formatPrice(order.total_amount)}</strong></span>
            </div>
        </div>
    `;
}

// Event listeners for dashboard
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('dashboard')) {
        // Sidebar navigation
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                const section = link.dataset.section;
                switchSection(section);
            });
        });
        
        // Order filters
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                const status = btn.dataset.status || null;
                loadOrders(status);
            });
        });
        
        // Profile form submission
        const profileForm = document.getElementById('profile-form');
        if (profileForm) {
            profileForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const firstName = document.getElementById('profile-first-name').value;
                const lastName = document.getElementById('profile-last-name').value;
                
                updateProfile({
                    first_name: firstName,
                    last_name: lastName
                })
                .then(response => {
                    if (response.success) {
                        setUser(response.user);
                        showToast('Profile updated successfully', 'success');
                    } else {
                        showToast(response.error || 'Failed to update profile', 'error');
                    }
                })
                .catch(error => {
                    showToast('Error updating profile', 'error');
                });
            });
        }
        
        // Load initial data
        loadOrders();
    }
});
