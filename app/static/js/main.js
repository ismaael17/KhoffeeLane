// Family Coffee Shop - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Family Coffee Shop initialized');
    
    // Initialize family member selection from localStorage
    initializeFamilyMember();
    
    // Initialize cart from localStorage
    updateCartCount();
    
    // Family member dropdown selection
    const familyMemberLinks = document.querySelectorAll('.family-member');
    familyMemberLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const member = this.getAttribute('data-member');
            setFamilyMember(member);
        });
    });
    
    // Add to cart functionality
    const addToCartButtons = document.querySelectorAll('.add-to-cart');
    addToCartButtons.forEach(button => {
        button.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Get coffee details
            const card = this.closest('.coffee-card');
            const id = card.getAttribute('data-id');
            const name = card.querySelector('.coffee-title').textContent;
            const price = parseFloat(card.getAttribute('data-price'));
            const image = card.querySelector('.coffee-img').src;
            
            // Get selected options
            const options = {};
            const milkOption = card.querySelector('input[name="milk-' + id + '"]:checked');
            if (milkOption) {
                options.milk = milkOption.value;
            }
            
            const sugarOption = card.querySelector('input[name="sugar-' + id + '"]:checked');
            if (sugarOption) {
                options.sugar = sugarOption.value;
            }
            
            // Check if size options are available
            const sizeOption = card.querySelector('input[name="size-' + id + '"]:checked');
            if (sizeOption) {
                options.size = sizeOption.value;
                
                // Adjust price based on size
                if (options.size === 'medium') {
                    options.priceAdjustment = 0.75;
                } else if (options.size === 'large') {
                    options.priceAdjustment = 1.5;
                } else {
                    options.priceAdjustment = 0;
                }
            }
            
            // Add extras if selected
            const extrasOptions = card.querySelectorAll('input[name="extras-' + id + '"]:checked');
            if (extrasOptions.length > 0) {
                options.extras = [];
                extrasOptions.forEach(extra => {
                    options.extras.push({
                        name: extra.value,
                        price: parseFloat(extra.getAttribute('data-price') || 0)
                    });
                });
            }
            
            // Get notes if available
            const notesInput = card.querySelector('.coffee-notes');
            if (notesInput && notesInput.value.trim() !== '') {
                options.notes = notesInput.value.trim();
            }
            
            // Calculate final price with adjustments
            let finalPrice = price;
            
            // Add size adjustment
            if (options.priceAdjustment) {
                finalPrice += options.priceAdjustment;
            }
            
            // Add extras
            if (options.extras && options.extras.length > 0) {
                options.extras.forEach(extra => {
                    finalPrice += extra.price;
                });
            }
            
            // Create cart item
            const cartItem = {
                id: id,
                name: name,
                price: finalPrice,
                basePrice: price,
                image: image,
                options: options,
                quantity: 1
            };
            
            // Add to cart
            addToCart(cartItem);
            
            // Show success message
            showToast('Added to cart: ' + name);
        });
    });
    
    // Quantity adjustment in cart
    const quantityInputs = document.querySelectorAll('.item-quantity');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const id = this.getAttribute('data-id');
            updateCartItemQuantity(id, parseInt(this.value));
        });
    });
    
    // Remove from cart
    const removeButtons = document.querySelectorAll('.remove-from-cart');
    removeButtons.forEach(button => {
        button.addEventListener('click', function() {
            const id = this.getAttribute('data-id');
            removeFromCart(id);
            
            // Remove item from DOM
            const cartItem = this.closest('.cart-item');
            if (cartItem) {
                cartItem.remove();
                
                // Update cart total
                updateCartTotal();
                
                // Show empty cart message if needed
                checkEmptyCart();
            }
        });
    });
    
    // Place order button
    const placeOrderBtn = document.getElementById('place-order-btn');
    if (placeOrderBtn) {
        placeOrderBtn.addEventListener('click', function() {
            const cart = getCart();
            
            // Check if cart is empty
            if (cart.length === 0) {
                showToast('Your cart is empty!', 'warning');
                return;
            }
            
            // Check if family member is selected
            const familyMember = getFamilyMember();
            if (!familyMember || familyMember === 'Select Family Member') {
                showToast('Please select a family member first!', 'warning');
                return;
            }
            
            // Get any order notes
            const orderNotes = document.getElementById('order-notes') ? document.getElementById('order-notes').value : '';
            
            // Create order object
            const order = {
                items: cart,
                familyMember: familyMember,
                notes: orderNotes,
                status: 'pending',
                timestamp: new Date().toISOString(),
                orderId: generateOrderId()
            };
            
            // Save order to localStorage
            saveOrder(order);
            
            // Clear cart
            clearCart();
            
            // Redirect to order confirmation
            window.location.href = '/order-confirmation/' + order.orderId;
        });
    }
    
    // Admin panel - change order status
    const statusButtons = document.querySelectorAll('.change-status-btn');
    statusButtons.forEach(button => {
        button.addEventListener('click', function() {
            const orderId = this.getAttribute('data-order-id');
            const newStatus = this.getAttribute('data-status');
            
            updateOrderStatus(orderId, newStatus);
            
            // Refresh the page to show updated status
            window.location.reload();
        });
    });
});

// ===== Helper Functions =====

// Family member functions
function initializeFamilyMember() {
    const familyMember = localStorage.getItem('familyMember') || 'Select Family Member';
    document.getElementById('currentFamilyMember').textContent = familyMember;
}

function setFamilyMember(member) {
    localStorage.setItem('familyMember', member);
    document.getElementById('currentFamilyMember').textContent = member;
}

function getFamilyMember() {
    return localStorage.getItem('familyMember');
}

// Cart functions
function getCart() {
    const cart = localStorage.getItem('cart');
    return cart ? JSON.parse(cart) : [];
}

function saveCart(cart) {
    localStorage.setItem('cart', JSON.stringify(cart));
    updateCartCount();
}

function addToCart(item) {
    const cart = getCart();
    
    // Check if item already exists in cart
    const existingItemIndex = cart.findIndex(cartItem => 
        cartItem.id === item.id && 
        JSON.stringify(cartItem.options) === JSON.stringify(item.options)
    );
    
    if (existingItemIndex !== -1) {
        // Update quantity
        cart[existingItemIndex].quantity += 1;
    } else {
        // Add new item
        cart.push(item);
    }
    
    saveCart(cart);
}

function removeFromCart(id) {
    const cart = getCart();
    const updatedCart = cart.filter(item => item.id !== id);
    saveCart(updatedCart);
}

function updateCartItemQuantity(id, quantity) {
    if (quantity < 1) return;
    
    const cart = getCart();
    const item = cart.find(item => item.id === id);
    
    if (item) {
        item.quantity = quantity;
        saveCart(cart);
        
        // Update subtotal on page
        const subtotalElement = document.querySelector(`.cart-item[data-id="${id}"] .item-subtotal`);
        if (subtotalElement) {
            subtotalElement.textContent = '// Modern Web App - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Modern Web App initialized');
    
    // Initialize AOS animation library
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });
    
    // Handle preloader
    setTimeout(function() {
        const preloader = document.querySelector('.preloader');
        if (preloader) {
            preloader.style.opacity = '0';
            setTimeout(function() {
                preloader.style.display = 'none';
            }, 500);
        }
    }, 500);
    
    // Initialize tooltips and popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    if (popoverTriggerList.length > 0) {
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
    
    // Back to top button
    const backToTopButton = document.getElementById('backToTop');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('active');
            } else {
                backToTopButton.classList.remove('active');
            }
        });
        
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Add active class to current nav item (in case the Jinja2 logic doesn't work)
    const currentLocation = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
    
    // Handle contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple form validation
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const messageInput = document.getElementById('message');
            
            if (nameInput.value.trim() === '' || emailInput.value.trim() === '' || messageInput.value.trim() === '') {
                alert('Please fill in all fields');
                return;
            }
            
            // Here you would normally send the form data to the server
            // For demo purposes, just show a success message
            const modalElement = document.getElementById('contactModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Show success toast or alert
            alert('Thank you for your message! We will get back to you soon.');
            
            // Reset form
            contactForm.reset();
        });
    }
    
    // Example of a reusable function for fetch API calls
    window.apiCall = async function(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(endpoint, options);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API call error:', error);
            return { error: error.message };
        }
    };
    
    // Handle API data loading with loading indicator
    const loadDataButton = document.getElementById('load-data');
    if (loadDataButton) {
        loadDataButton.addEventListener('click', async function() {
            // Show loading state
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            this.disabled = true;
            
            try {
                const data = await window.apiCall('/api/data');
                const responseDiv = document.getElementById('response-content');
                
                if (responseDiv) {
                    responseDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h6 class="alert-heading">${data.message}</h6>
                            <ul class="list-group mt-3">
                                ${data.items.map(item => `<li class="list-group-item">${item}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                    document.getElementById('api-response').classList.remove('d-none');
                }
            } catch (error) {
                console.error('Error:', error);
                
                const responseDiv = document.getElementById('response-content');
                if (responseDiv) {
                    responseDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <h6 class="alert-heading">Error</h6>
                            <p>${error.message || 'Something went wrong'}</p>
                        </div>
                    `;
                    document.getElementById('api-response').classList.remove('d-none');
                }
            } finally {
                // Reset button state
                this.innerHTML = 'Load API Data';
                this.disabled = false;
            }
        });
    }
    
    // Newsletter form handling
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            if (email.trim() === '') {
                alert('Please enter your email address');
                return;
            }
            
            // Here you would normally send the email to the server
            // For demo purposes, just show a success message
            alert('Thank you for subscribing to our newsletter!');
            this.reset();
        });
    }
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            if (href !== '#' && href.startsWith('#')) {
                e.preventDefault();
                
                const targetElement = document.querySelector(this.getAttribute('href'));
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});
 + (item.price * item.quantity).toFixed(2);
        }
        
        // Update cart total
        updateCartTotal();
    }
}

function updateCartCount() {
    const cart = getCart();
    const count = cart.reduce((total, item) => total + item.quantity, 0);
    
    const cartCountElements = document.querySelectorAll('.cart-count');
    cartCountElements.forEach(element => {
        element.textContent = count;
    });
}

function clearCart() {
    localStorage.removeItem('cart');
    updateCartCount();
}

function updateCartTotal() {
    const cart = getCart();
    const totalElement = document.getElementById('cart-total');
    
    if (totalElement) {
        const total = cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
        totalElement.textContent = '// Modern Web App - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Modern Web App initialized');
    
    // Initialize AOS animation library
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });
    
    // Handle preloader
    setTimeout(function() {
        const preloader = document.querySelector('.preloader');
        if (preloader) {
            preloader.style.opacity = '0';
            setTimeout(function() {
                preloader.style.display = 'none';
            }, 500);
        }
    }, 500);
    
    // Initialize tooltips and popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    if (popoverTriggerList.length > 0) {
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
    
    // Back to top button
    const backToTopButton = document.getElementById('backToTop');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('active');
            } else {
                backToTopButton.classList.remove('active');
            }
        });
        
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Add active class to current nav item (in case the Jinja2 logic doesn't work)
    const currentLocation = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
    
    // Handle contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple form validation
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const messageInput = document.getElementById('message');
            
            if (nameInput.value.trim() === '' || emailInput.value.trim() === '' || messageInput.value.trim() === '') {
                alert('Please fill in all fields');
                return;
            }
            
            // Here you would normally send the form data to the server
            // For demo purposes, just show a success message
            const modalElement = document.getElementById('contactModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Show success toast or alert
            alert('Thank you for your message! We will get back to you soon.');
            
            // Reset form
            contactForm.reset();
        });
    }
    
    // Example of a reusable function for fetch API calls
    window.apiCall = async function(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(endpoint, options);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API call error:', error);
            return { error: error.message };
        }
    };
    
    // Handle API data loading with loading indicator
    const loadDataButton = document.getElementById('load-data');
    if (loadDataButton) {
        loadDataButton.addEventListener('click', async function() {
            // Show loading state
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            this.disabled = true;
            
            try {
                const data = await window.apiCall('/api/data');
                const responseDiv = document.getElementById('response-content');
                
                if (responseDiv) {
                    responseDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h6 class="alert-heading">${data.message}</h6>
                            <ul class="list-group mt-3">
                                ${data.items.map(item => `<li class="list-group-item">${item}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                    document.getElementById('api-response').classList.remove('d-none');
                }
            } catch (error) {
                console.error('Error:', error);
                
                const responseDiv = document.getElementById('response-content');
                if (responseDiv) {
                    responseDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <h6 class="alert-heading">Error</h6>
                            <p>${error.message || 'Something went wrong'}</p>
                        </div>
                    `;
                    document.getElementById('api-response').classList.remove('d-none');
                }
            } finally {
                // Reset button state
                this.innerHTML = 'Load API Data';
                this.disabled = false;
            }
        });
    }
    
    // Newsletter form handling
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            if (email.trim() === '') {
                alert('Please enter your email address');
                return;
            }
            
            // Here you would normally send the email to the server
            // For demo purposes, just show a success message
            alert('Thank you for subscribing to our newsletter!');
            this.reset();
        });
    }
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            if (href !== '#' && href.startsWith('#')) {
                e.preventDefault();
                
                const targetElement = document.querySelector(this.getAttribute('href'));
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});
 + total.toFixed(2);
    }
}

function checkEmptyCart() {
    const cart = getCart();
    const emptyCartMessage = document.getElementById('empty-cart-message');
    const cartContent = document.getElementById('cart-content');
    
    if (emptyCartMessage && cartContent) {
        if (cart.length === 0) {
            emptyCartMessage.classList.remove('d-none');
            cartContent.classList.add('d-none');
        } else {
            emptyCartMessage.classList.add('d-none');
            cartContent.classList.remove('d-none');
        }
    }
}

// Order functions
function getOrders() {
    const orders = localStorage.getItem('orders');
    return orders ? JSON.parse(orders) : [];
}

function saveOrder(order) {
    const orders = getOrders();
    orders.push(order);
    localStorage.setItem('orders', JSON.stringify(orders));
}

function getOrderById(orderId) {
    const orders = getOrders();
    return orders.find(order => order.orderId === orderId);
}

function updateOrderStatus(orderId, newStatus) {
    const orders = getOrders();
    const order = orders.find(order => order.orderId === orderId);
    
    if (order) {
        order.status = newStatus;
        localStorage.setItem('orders', JSON.stringify(orders));
    }
}

function generateOrderId() {
    return 'ORD-' + Math.random().toString(36).substr(2, 9).toUpperCase();
}

// Utility functions
function showToast(message, type = 'success') {
    // Check if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        // Create toast element
        const toastEl = document.createElement('div');
        toastEl.className = `toast align-items-center text-white bg-${type} border-0`;
        toastEl.setAttribute('role', 'alert');
        toastEl.setAttribute('aria-live', 'assertive');
        toastEl.setAttribute('aria-atomic', 'true');
        
        toastEl.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        // Add to container or body
        let toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            toastContainer = document.createElement('div');
            toastContainer.className = 'toast-container position-fixed bottom-0 end-0 p-3';
            document.body.appendChild(toastContainer);
        }
        
        toastContainer.appendChild(toastEl);
        
        // Initialize and show toast
        const toast = new bootstrap.Toast(toastEl, { delay: 3000 });
        toast.show();
        
        // Remove from DOM after hiding
        toastEl.addEventListener('hidden.bs.toast', function() {
            toastEl.remove();
        });
    } else {
        // Fallback to alert
        alert(message);
    }
}// Modern Web App - Main JavaScript

document.addEventListener('DOMContentLoaded', function() {
    console.log('Modern Web App initialized');
    
    // Initialize AOS animation library
    AOS.init({
        duration: 800,
        easing: 'ease-in-out',
        once: true,
        mirror: false
    });
    
    // Handle preloader
    setTimeout(function() {
        const preloader = document.querySelector('.preloader');
        if (preloader) {
            preloader.style.opacity = '0';
            setTimeout(function() {
                preloader.style.display = 'none';
            }, 500);
        }
    }, 500);
    
    // Initialize tooltips and popovers
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    if (tooltipTriggerList.length > 0) {
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
    
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    if (popoverTriggerList.length > 0) {
        popoverTriggerList.map(function (popoverTriggerEl) {
            return new bootstrap.Popover(popoverTriggerEl);
        });
    }
    
    // Navbar scroll effect
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 50) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        });
    }
    
    // Back to top button
    const backToTopButton = document.getElementById('backToTop');
    if (backToTopButton) {
        window.addEventListener('scroll', function() {
            if (window.scrollY > 300) {
                backToTopButton.classList.add('active');
            } else {
                backToTopButton.classList.remove('active');
            }
        });
        
        backToTopButton.addEventListener('click', function(e) {
            e.preventDefault();
            window.scrollTo({
                top: 0,
                behavior: 'smooth'
            });
        });
    }
    
    // Add active class to current nav item (in case the Jinja2 logic doesn't work)
    const currentLocation = window.location.pathname;
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href') === currentLocation) {
            link.classList.add('active');
        }
    });
    
    // Handle contact form submission
    const contactForm = document.getElementById('contactForm');
    if (contactForm) {
        contactForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Simple form validation
            const nameInput = document.getElementById('name');
            const emailInput = document.getElementById('email');
            const messageInput = document.getElementById('message');
            
            if (nameInput.value.trim() === '' || emailInput.value.trim() === '' || messageInput.value.trim() === '') {
                alert('Please fill in all fields');
                return;
            }
            
            // Here you would normally send the form data to the server
            // For demo purposes, just show a success message
            const modalElement = document.getElementById('contactModal');
            const modal = bootstrap.Modal.getInstance(modalElement);
            modal.hide();
            
            // Show success toast or alert
            alert('Thank you for your message! We will get back to you soon.');
            
            // Reset form
            contactForm.reset();
        });
    }
    
    // Example of a reusable function for fetch API calls
    window.apiCall = async function(endpoint, method = 'GET', data = null) {
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(endpoint, options);
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('API call error:', error);
            return { error: error.message };
        }
    };
    
    // Handle API data loading with loading indicator
    const loadDataButton = document.getElementById('load-data');
    if (loadDataButton) {
        loadDataButton.addEventListener('click', async function() {
            // Show loading state
            this.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
            this.disabled = true;
            
            try {
                const data = await window.apiCall('/api/data');
                const responseDiv = document.getElementById('response-content');
                
                if (responseDiv) {
                    responseDiv.innerHTML = `
                        <div class="alert alert-success">
                            <h6 class="alert-heading">${data.message}</h6>
                            <ul class="list-group mt-3">
                                ${data.items.map(item => `<li class="list-group-item">${item}</li>`).join('')}
                            </ul>
                        </div>
                    `;
                    document.getElementById('api-response').classList.remove('d-none');
                }
            } catch (error) {
                console.error('Error:', error);
                
                const responseDiv = document.getElementById('response-content');
                if (responseDiv) {
                    responseDiv.innerHTML = `
                        <div class="alert alert-danger">
                            <h6 class="alert-heading">Error</h6>
                            <p>${error.message || 'Something went wrong'}</p>
                        </div>
                    `;
                    document.getElementById('api-response').classList.remove('d-none');
                }
            } finally {
                // Reset button state
                this.innerHTML = 'Load API Data';
                this.disabled = false;
            }
        });
    }
    
    // Newsletter form handling
    const newsletterForm = document.querySelector('.newsletter-form');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const email = this.querySelector('input[type="email"]').value;
            
            if (email.trim() === '') {
                alert('Please enter your email address');
                return;
            }
            
            // Here you would normally send the email to the server
            // For demo purposes, just show a success message
            alert('Thank you for subscribing to our newsletter!');
            this.reset();
        });
    }
    
    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            if (href !== '#' && href.startsWith('#')) {
                e.preventDefault();
                
                const targetElement = document.querySelector(this.getAttribute('href'));
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
});