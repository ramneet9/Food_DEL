// Main JavaScript for JustEat Technology

$(document).ready(function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);

    // Add to cart functionality
    $('.add-to-cart-btn').on('click', function(e) {
        e.preventDefault();
        
        const button = $(this);
        const menuItemId = button.data('menu-item-id');
        const quantity = parseInt($('#quantity-' + menuItemId).val()) || 1;
        
        // Show loading state
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin"></i> Adding...');
        
        $.ajax({
            url: '/customer/add-to-cart',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                menu_item_id: menuItemId,
                quantity: quantity
            }),
            success: function(response) {
                if (response.success) {
                    showToast('success', response.message);
                    updateCartCount(response.cart_count);
                } else {
                    showToast('error', response.message);
                }
            },
            error: function() {
                showToast('error', 'An error occurred while adding item to cart');
            },
            complete: function() {
                // Reset button state
                button.prop('disabled', false);
                button.html('<i class="fas fa-cart-plus"></i> Add to Cart');
            }
        });
    });

    // Remove from cart functionality
    $('.remove-from-cart-btn').on('click', function(e) {
        e.preventDefault();
        
        const button = $(this);
        const cartItemId = button.data('cart-item-id');
        
        if (confirm('Are you sure you want to remove this item from your cart?')) {
            // Show loading state
            button.prop('disabled', true);
            button.html('<i class="fas fa-spinner fa-spin"></i>');
            
            $.ajax({
                url: '/customer/remove-from-cart',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({
                    cart_item_id: cartItemId
                }),
                success: function(response) {
                    if (response.success) {
                        showToast('success', response.message);
                        updateCartCount(response.cart_count);
                        updateCartSummary(response.subtotal_amount, response.discount_amount, response.total_amount);
                        // Remove the cart item from DOM
                        button.closest('.cart-item').fadeOut(300, function() {
                            $(this).remove();
                        });
                    } else {
                        showToast('error', response.message);
                    }
                },
                error: function() {
                    showToast('error', 'An error occurred while removing item from cart');
                },
                complete: function() {
                    // Reset button state
                    button.prop('disabled', false);
                    button.html('<i class="fas fa-trash"></i>');
                }
            });
        }
    });

    // Place order functionality
    $('#place-order-btn').on('click', function(e) {
        e.preventDefault();
        
        const button = $(this);
        
        if (confirm('Are you sure you want to place this order?')) {
            // Show loading state
            button.prop('disabled', true);
            button.html('<i class="fas fa-spinner fa-spin"></i> Placing Order...');
            
            $.ajax({
                url: '/customer/place-order',
                method: 'POST',
                contentType: 'application/json',
                data: JSON.stringify({}),
                success: function(response) {
                    if (response.success) {
                        showToast('success', response.message);
                        // Redirect to orders page after a short delay
                        setTimeout(function() {
                            window.location.href = '/customer/orders';
                        }, 2000);
                    } else {
                        showToast('error', response.message);
                    }
                },
                error: function() {
                    showToast('error', 'An error occurred while placing order');
                },
                complete: function() {
                    // Reset button state
                    button.prop('disabled', false);
                    button.html('<i class="fas fa-check"></i> Place Order');
                }
            });
        }
    });

    // Update order status (for restaurant owners)
    $('.update-order-status').on('change', function() {
        const select = $(this);
        const orderId = select.data('order-id');
        const status = select.val();
        
        $.ajax({
            url: '/restaurant/update-order-status',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({
                order_id: orderId,
                status: status
            }),
            success: function(response) {
                if (response.success) {
                    showToast('success', response.message);
                } else {
                    showToast('error', response.message);
                }
            },
            error: function() {
                showToast('error', 'An error occurred while updating order status');
            }
        });
    });

    // Add menu item (for restaurant owners)
    $('#add-menu-item-form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(form[0]);
        const data = Object.fromEntries(formData);
        
        // Convert boolean values
        data.is_vegetarian = data.is_vegetarian === 'on';
        data.is_vegan = data.is_vegan === 'on';
        data.is_gluten_free = data.is_gluten_free === 'on';
        data.is_special = data.is_special === 'on';
        data.is_deal_of_day = data.is_deal_of_day === 'on';
        
        $.ajax({
            url: '/restaurant/add-menu-item',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                if (response.success) {
                    showToast('success', response.message);
                    form[0].reset();
                    // Reload the page to show the new item
                    setTimeout(function() {
                        location.reload();
                    }, 1000);
                } else {
                    showToast('error', response.message);
                }
            },
            error: function() {
                showToast('error', 'An error occurred while adding menu item');
            }
        });
    });

    // Update profile
    $('#update-profile-form').on('submit', function(e) {
        e.preventDefault();
        
        const form = $(this);
        const formData = new FormData(form[0]);
        const data = Object.fromEntries(formData);
        
        $.ajax({
            url: '/customer/update-profile',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify(data),
            success: function(response) {
                if (response.success) {
                    showToast('success', response.message);
                } else {
                    showToast('error', response.message);
                }
            },
            error: function() {
                showToast('error', 'An error occurred while updating profile');
            }
        });
    });

    // Search functionality
    $('#search-form').on('submit', function(e) {
        e.preventDefault();
        const searchTerm = $('#search-input').val().trim();
        if (searchTerm) {
            window.location.href = $(this).attr('action') + '?search=' + encodeURIComponent(searchTerm);
        }
    });

    // Filter functionality
    $('.filter-select').on('change', function() {
        const form = $(this).closest('form');
        if (form.length) {
            form.submit();
        }
    });

    // Quantity controls (generic input increment/decrement)
    $('.quantity-btn').on('click', function() {
        const button = $(this);
        const input = button.siblings('input[type="number"]');
        const currentValue = parseInt(input.val()) || 1;
        if (button.hasClass('quantity-increase')) {
            input.val(currentValue + 1);
        } else if (button.hasClass('quantity-decrease') && currentValue > 1) {
            input.val(currentValue - 1);
        }
    });

    // Cart page: live update quantity via API
    $(document).on('click', '.cart-item .quantity-btn', function() {
        const container = $(this).closest('.cart-item');
        const input = container.find('input[type="number"]');
        const cartItemId = container.find('.remove-from-cart-btn').data('cart-item-id');
        const quantity = parseInt(input.val()) || 1;
        $.ajax({
            url: '/customer/update-cart-quantity',
            method: 'POST',
            contentType: 'application/json',
            data: JSON.stringify({ cart_item_id: cartItemId, quantity: quantity }),
            success: function(response) {
                if (response.success) {
                    // Update cart badge count
                    updateCartCount(response.cart_count);
                    // Update unit price if discounted
                    if (typeof response.line_unit_price !== 'undefined') {
                        const unit = parseFloat(response.line_unit_price);
                        const unitSpan = container.find('.price-per-unit');
                        unitSpan.text(formatCurrency(unit));
                        unitSpan.attr('data-unit', unit.toFixed(2));
                    }
                    // Update line total within the row
                    if (typeof response.line_total !== 'undefined') {
                        container.find('.line-total').text(formatCurrency(response.line_total));
                    }
                    // Update summary totals
                    updateCartSummary(response.subtotal_amount, response.discount_amount, response.total_amount);
                } else {
                    showToast('error', response.message);
                }
            },
            error: function() {
                showToast('error', 'An error occurred while updating cart');
            }
        });
    });
});

// Utility Functions
function showToast(type, message) {
    const toastHtml = `
        <div class="toast align-items-center text-white bg-${type === 'error' ? 'danger' : type} border-0" role="alert">
            <div class="d-flex">
                <div class="toast-body">
                    <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'} me-2"></i>
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        </div>
    `;
    
    // Create toast container if it doesn't exist
    if (!$('.toast-container').length) {
        $('body').append('<div class="toast-container"></div>');
    }
    
    const toast = $(toastHtml);
    $('.toast-container').append(toast);
    
    const bsToast = new bootstrap.Toast(toast[0]);
    bsToast.show();
    
    // Remove toast element after it's hidden
    toast.on('hidden.bs.toast', function() {
        $(this).remove();
    });
}

function updateCartCount(count) {
    $('#cart-count').text(count);
}

function updateCartTotal(total) {
    const formatted = formatCurrency(total);
    $('#cart-total').text(formatted);
    $('#cart-subtotal').text(formatted);
}

function updateCartSummary(subtotal, discount, total) {
    $('#cart-subtotal').text(formatCurrency(subtotal));
    $('#cart-discount').text('-' + formatCurrency(discount));
    $('#cart-total').text(formatCurrency(total));
}

function showLoading() {
    if (!$('.loading-overlay').length) {
        $('body').append(`
            <div class="loading-overlay">
                <div class="loading-spinner">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                    <p class="mt-2">Loading...</p>
                </div>
            </div>
        `);
    }
}

function hideLoading() {
    $('.loading-overlay').remove();
}

// Form validation
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;
    
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    
    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            field.classList.add('is-invalid');
            isValid = false;
        } else {
            field.classList.remove('is-invalid');
        }
    });
    
    return isValid;
}

// Format currency
function formatCurrency(amount) {
    return '₹' + parseFloat(amount).toFixed(2);
}

// Format date
function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

// Debounce function for search
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Location selection functionality
$(document).ready(function() {
    // Handle location selection
    $('.location-option').on('click', function(e) {
        e.preventDefault();
        const location = $(this).data('location');
        $('#selected-location').text(location);
        
        // Also update hero location if it exists
        if ($('#hero-location').length) {
            $('#hero-location').text(location);
        }
        
        // Store location in localStorage
        localStorage.setItem('selectedLocation', location);
        
        // Show toast notification
        showToast('success', `Location changed to ${location}`);
        
        // Close dropdown
        $('.dropdown-menu').removeClass('show');

        // Reorder restaurants if on listing page
        try { reorderRestaurantsByLocation(location); } catch (_) {}
    });
    
    // Load saved location on page load
    const savedLocation = localStorage.getItem('selectedLocation');
    if (savedLocation) {
        $('#selected-location').text(savedLocation);
        try { reorderRestaurantsByLocation(savedLocation, true); } catch (_) {}
    }
    
    // Add fade-in animation to cards
    $('.card').addClass('fade-in-up');
    
    // Initialize any page-specific functionality
    if (typeof initPage === 'function') {
        initPage();
    }

    // Navbar color change on scroll
    const navbar = document.querySelector('.site-navbar');
    const toggleNavbarBg = () => {
        if (!navbar) return;
        if (window.scrollY > 10) {
            navbar.classList.add('scrolled');
        } else {
            navbar.classList.remove('scrolled');
        }
    };
    toggleNavbarBg();
    window.addEventListener('scroll', toggleNavbarBg);

    // Horizontal scroll buttons for food categories
    $(document).on('click', '.scroll-btn', function() {
        const target = $($(this).data('target'));
        const amount = 300;
        if ($(this).hasClass('left')) {
            target.animate({ scrollLeft: target.scrollLeft() - amount }, 250);
        } else {
            target.animate({ scrollLeft: target.scrollLeft() + amount }, 250);
        }
    });
});

// Reorder restaurants by chosen location with smooth animation
function reorderRestaurantsByLocation(location, isInitial=false) {
    const grid = $('#restaurants-grid');
    if (!grid.length) return;
    const cards = grid.children('[data-location]');
    if (!cards.length) return;

    const match = [];
    const rest = [];
    cards.each(function() {
        (($(this).data('location') || '').toString().toLowerCase() === (location || '').toString().toLowerCase())
            ? match.push(this)
            : rest.push(this);
    });

    if (!match.length) return;

    if (!isInitial) grid.css('opacity', 0.0);

    const fragment = $(document.createDocumentFragment());
    $(match).each(function() { fragment.append(this); });
    $(rest).each(function() { fragment.append(this); });
    grid.append(fragment);

    if (!isInitial) grid.animate({ opacity: 1.0 }, 200);
}
