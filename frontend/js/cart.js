// Cart Management
let cart = JSON.parse(localStorage.getItem('cart')) || {};

function addToCart(restaurantId, item) {
    if (!cart[restaurantId]) {
        cart[restaurantId] = [];
    }
    
    const existingItem = cart[restaurantId].find(i => i.id === item.id);
    if (existingItem) {
        existingItem.quantity += item.quantity || 1;
    } else {
        cart[restaurantId].push({ ...item, quantity: item.quantity || 1 });
    }
    
    saveCart();
    updateCartCount();
    showToast(`${item.name} added to cart`, 'success');
    renderCart();
}

function removeFromCart(restaurantId, itemId) {
    if (cart[restaurantId]) {
        cart[restaurantId] = cart[restaurantId].filter(item => item.id !== itemId);
        if (cart[restaurantId].length === 0) {
            delete cart[restaurantId];
        }
        saveCart();
        updateCartCount();
        renderCart();
    }
}

function updateCartItemQuantity(restaurantId, itemId, quantity) {
    if (cart[restaurantId]) {
        const item = cart[restaurantId].find(i => i.id === itemId);
        if (item) {
            if (quantity <= 0) {
                removeFromCart(restaurantId, itemId);
            } else {
                item.quantity = quantity;
                saveCart();
                updateCartCount();
                renderCart();
            }
        }
    }
}

function clearCart() {
    cart = {};
    saveCart();
    updateCartCount();
    renderCart();
}

function saveCart() {
    localStorage.setItem('cart', JSON.stringify(cart));
}

function updateCartCount() {
    const count = Object.values(cart).reduce((sum, items) => {
        return sum + items.reduce((itemSum, item) => itemSum + item.quantity, 0);
    }, 0);
    
    const cartCount = document.getElementById('cart-count');
    if (cartCount) {
        cartCount.textContent = count;
    }
}

function getCartTotal() {
    let subtotal = 0;
    for (const restaurantId in cart) {
        const items = cart[restaurantId];
        subtotal += items.reduce((sum, item) => sum + (item.price * item.quantity), 0);
    }
    
    const tax = subtotal * 0.05; // 5% GST
    const delivery = 50; // Flat delivery charge
    const total = subtotal + tax + delivery;
    
    return { subtotal, tax, delivery, total };
}

function renderCart() {
    const container = document.getElementById('cart-items-container');
    if (!container) return;
    
    container.innerHTML = '';
    
    let hasItems = false;
    for (const restaurantId in cart) {
        const items = cart[restaurantId];
        hasItems = true;
        
        items.forEach(item => {
            const cartItem = document.createElement('div');
            cartItem.className = 'cart-item';
            cartItem.innerHTML = `
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name}</div>
                    <div class="cart-item-price">${formatPrice(item.price)}</div>
                </div>
                <div class="cart-item-controls">
                    <button onclick="updateCartItemQuantity('${restaurantId}', '${item.id}', ${item.quantity - 1})">−</button>
                    <span>${item.quantity}</span>
                    <button onclick="updateCartItemQuantity('${restaurantId}', '${item.id}', ${item.quantity + 1})">+</button>
                    <button onclick="removeFromCart('${restaurantId}', '${item.id}')"><i class="fas fa-trash"></i></button>
                </div>
            `;
            container.appendChild(cartItem);
        });
    }
    
    if (!hasItems) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-light); padding: 20px;">Your cart is empty</p>';
    }
    
    updateCartSummary();
}

function updateCartSummary() {
    const { subtotal, tax, delivery, total } = getCartTotal();
    
    const subtotalEl = document.getElementById('cart-subtotal');
    const deliveryEl = document.getElementById('cart-delivery');
    const taxEl = document.getElementById('cart-tax');
    const totalEl = document.getElementById('cart-total');
    
    if (subtotalEl) subtotalEl.textContent = formatPrice(subtotal);
    if (deliveryEl) deliveryEl.textContent = formatPrice(delivery);
    if (taxEl) taxEl.textContent = formatPrice(tax);
    if (totalEl) totalEl.textContent = formatPrice(total);
}

function proceedToCheckout() {
    if (Object.keys(cart).length === 0) {
        showToast('Your cart is empty', 'warning');
        return;
    }
    
    if (!isAuthenticated()) {
        showToast('Please login to proceed', 'warning');
        setTimeout(() => {
            window.location.href = 'login.html';
        }, 1000);
        return;
    }
    
    // Get first restaurant from cart (assuming single restaurant order)
    const restaurantId = Object.keys(cart)[0];
    const items = cart[restaurantId];
    const { subtotal, tax, delivery, total } = getCartTotal();
    
    // Store order data for checkout
    const orderData = {
        restaurant_id: restaurantId,
        items: items,
        subtotal: subtotal,
        tax: tax,
        delivery_charge: delivery,
        total_amount: total
    };
    
    localStorage.setItem('pendingOrder', JSON.stringify(orderData));
    window.location.href = 'checkout.html';
}

// Event listeners
document.addEventListener('DOMContentLoaded', () => {
    updateCartCount();
    renderCart();
    
    const checkoutBtn = document.getElementById('checkout-btn');
    if (checkoutBtn) {
        checkoutBtn.addEventListener('click', proceedToCheckout);
    }
    
    const closeCartBtn = document.getElementById('cart-close');
    if (closeCartBtn) {
        closeCartBtn.addEventListener('click', toggleCartSidebar);
    }
});

// Close cart when clicking outside
document.addEventListener('click', (e) => {
    const cart = document.getElementById('cart-sidebar');
    const cartBtn = document.getElementById('cart-btn');
    
    if (cart && cartBtn && !cart.contains(e.target) && !cartBtn.contains(e.target)) {
        cart.classList.remove('active');
    }
});