// Admin Dashboard Functionality
let revenueChart = null;
let orderStatusChart = null;

function switchAdminSection(sectionName) {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    document.querySelectorAll('.sidebar-link').forEach(link => {
        link.classList.remove('active');
    });
    
    const section = document.getElementById(sectionName);
    if (section) {
        section.classList.add('active');
    }
    
    const link = document.querySelector(`.sidebar-link[data-section="${sectionName}"]`);
    if (link) {
        link.classList.add('active');
    }
    
    if (sectionName === 'dashboard') {
        loadAdminDashboard();
    } else if (sectionName === 'orders') {
        loadAllOrders();
    } else if (sectionName === 'users') {
        loadAllUsers();
    } else if (sectionName === 'fraud') {
        loadFraudAlerts();
    } else if (sectionName === 'analytics') {
        loadAnalytics();
    }
}

function loadAdminDashboard() {
    showLoader(true);
    getAdminDashboard()
        .then(response => {
            showLoader(false);
            if (response.success) {
                renderAdminDashboard(response.dashboard, response.active_orders, response.recent_fraud_alerts);
            } else {
                showToast('Failed to load dashboard', 'error');
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading admin dashboard:', error);
            showToast('Error loading dashboard', 'error');
        });
}

function renderAdminDashboard(dashboard, activeOrders, fraudAlerts) {
    // Update stat cards
    document.getElementById('stat-active-orders').textContent = dashboard.active_orders;
    document.getElementById('stat-today-revenue').textContent = formatPrice(dashboard.today_revenue);
    document.getElementById('stat-total-users').textContent = dashboard.total_users;
    document.getElementById('stat-fraud-alerts').textContent = dashboard.pending_fraud_reviews;
    
    // Initialize charts
    initializeCharts();
    
    // Render active orders
    const ordersContainer = document.querySelector('[data-section="orders"] .orders-list');
    if (ordersContainer && activeOrders.length > 0) {
        ordersContainer.innerHTML = activeOrders.slice(0, 5).map(order => `
            <div class="order-card">
                <div class="order-header">
                    <div class="order-number">Order #${order.order_number}</div>
                    <div class="order-status ${order.status}">${order.status.toUpperCase()}</div>
                </div>
                <div class="order-details">
                    <div class="order-detail">
                        <div class="order-detail-label">Amount</div>
                        <div class="order-detail-value">${formatPrice(order.total_amount)}</div>
                    </div>
                    <div class="order-detail">
                        <div class="order-detail-label">Date</div>
                        <div class="order-detail-value">${formatDate(order.created_at)}</div>
                    </div>
                </div>
            </div>
        `).join('');
    }
}

function initializeCharts() {
    // Revenue Chart
    const revenueCtx = document.getElementById('revenue-chart');
    if (revenueCtx && !revenueChart) {
        revenueChart = new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
                datasets: [{
                    label: 'Revenue (₹)',
                    data: [5000, 6200, 5800, 7100, 8200, 9100, 7800],
                    borderColor: '#FF7A3D',
                    backgroundColor: 'rgba(255, 122, 61, 0.1)',
                    tension: 0.3,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }
    
    // Order Status Chart
    const statusCtx = document.getElementById('order-status-chart');
    if (statusCtx && !orderStatusChart) {
        orderStatusChart = new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Pending', 'Confirmed', 'Preparing', 'Out for Delivery', 'Delivered'],
                datasets: [{
                    data: [12, 25, 18, 15, 50],
                    backgroundColor: [
                        '#f39c12',
                        '#3498db',
                        '#9b59b6',
                        '#e67e22',
                        '#27ae60'
                    ]
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

function loadAllOrders(status = null, page = 1) {
    showLoader(true);
    getAllOrders(status, page)
        .then(response => {
            showLoader(false);
            if (response.success) {
                renderOrdersTable(response.orders);
            } else {
                showToast('Failed to load orders', 'error');
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading orders:', error);
        });
}

function renderOrdersTable(orders) {
    const tbody = document.getElementById('orders-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = orders.map(order => `
        <tr>
            <td>#${order.order_number}</td>
            <td>${order.user_id}</td>
            <td>${formatPrice(order.total_amount)}</td>
            <td><span class="order-status ${order.status}">${order.status}</span></td>
            <td>${formatDate(order.created_at)}</td>
            <td><button class="btn btn-small" onclick="viewOrderDetail('${order._id}')">View</button></td>
        </tr>
    `).join('');
}

function loadAllUsers() {
    showLoader(true);
    getAllUsers()
        .then(response => {
            showLoader(false);
            if (response.success) {
                renderUsersTable(response.users);
            } else {
                showToast('Failed to load users', 'error');
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading users:', error);
        });
}

function renderUsersTable(users) {
    const tbody = document.getElementById('users-table-body');
    if (!tbody) return;
    
    tbody.innerHTML = users.map(user => `
        <tr>
            <td>${user._id}</td>
            <td>${user.first_name} ${user.last_name}</td>
            <td>${user.email}</td>
            <td>${user.phone}</td>
            <td>${formatDate(user.created_at)}</td>
            <td><span style="color: ${user.is_active ? '#27ae60' : '#e74c3c'};">${user.is_active ? 'Active' : 'Inactive'}</span></td>
            <td><button class="btn btn-small" onclick="manageUser('${user._id}')">Manage</button></td>
        </tr>
    `).join('');
}

function loadFraudAlerts() {
    showLoader(true);
    getFraudAlerts()
        .then(response => {
            showLoader(false);
            if (response.success) {
                renderFraudAlerts(response.alerts);
            } else {
                showToast('Failed to load fraud alerts', 'error');
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading fraud alerts:', error);
        });
}

function renderFraudAlerts(alerts) {
    const container = document.getElementById('fraud-alerts-container');
    if (!container) return;
    
    if (alerts.length === 0) {
        container.innerHTML = '<p style="text-align: center; padding: 20px; color: var(--text-light);">No fraud alerts</p>';
        return;
    }
    
    container.innerHTML = alerts.map(alert => `
        <div class="fraud-alert-card">
            <div class="fraud-alert-header">
                <span class="fraud-alert-id">Alert #${alert._id}</span>
                <span class="fraud-score">${alert.fraud_score}</span>
            </div>
            <div class="fraud-alert-content">
                <div class="fraud-detail">
                    <span class="fraud-detail-label">Payment ID:</span>
                    <span class="fraud-detail-value">${alert.payment_id}</span>
                </div>
                <div class="fraud-detail">
                    <span class="fraud-detail-label">Recommendation:</span>
                    <span class="fraud-detail-value">${alert.recommendation}</span>
                </div>
                <div class="fraud-flags">
                    ${alert.flags.map(flag => `<span class="fraud-flag">${flag}</span>`).join('')}
                </div>
            </div>
            <div class="fraud-alert-actions">
                <button class="btn-approve" onclick="reviewFraudAlert('${alert._id}', 'approve', '')">Approve</button>
                <button class="btn-block" onclick="reviewFraudAlert('${alert._id}', 'block', '')">Block</button>
            </div>
        </div>
    `).join('');
}

function loadAnalytics() {
    showLoader(true);
    getRevenueAnalytics(30)
        .then(response => {
            showLoader(false);
            if (response.success && response.analytics) {
                renderAnalytics(response.analytics);
            }
        })
        .catch(error => {
            showLoader(false);
            console.error('Error loading analytics:', error);
        });
}

function renderAnalytics(analytics) {
    document.getElementById('avg-order-value').textContent = analytics.average_transaction ? formatPrice(analytics.average_transaction) : '₹0';
    document.getElementById('total-transactions').textContent = analytics.total_transactions || 0;
    // Add more analytics rendering as needed
}

// Event listeners for admin
document.addEventListener('DOMContentLoaded', () => {
    if (window.location.pathname.includes('admin')) {
        document.querySelectorAll('.sidebar-link').forEach(link => {
            link.addEventListener('click', (e) => {
                e.preventDefault();
                switchAdminSection(link.dataset.section);
            });
        });
        
        loadAdminDashboard();
    }
});
