// Main JavaScript file for the vulnerable e-commerce app

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips if Bootstrap is available
    if (typeof bootstrap !== 'undefined') {
        var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }

    // Handle quantity changes in cart
    const quantityInputs = document.querySelectorAll('.quantity-input');
    if (quantityInputs) {
        quantityInputs.forEach(input => {
            input.addEventListener('change', function() {
                const form = this.closest('form');
                if (form) {
                    form.submit();
                }
            });
        });
    }

    // Search form
    const searchForm = document.getElementById('search-form');
    if (searchForm) {
        searchForm.addEventListener('submit', function(e) {
            const searchInput = document.getElementById('search-input');
            if (searchInput && searchInput.value.trim() === '') {
                e.preventDefault();
                alert('Please enter a search term');
            }
        });
    }

    // Add to cart confirmation
    const addToCartBtns = document.querySelectorAll('.add-to-cart-btn');
    if (addToCartBtns) {
        addToCartBtns.forEach(btn => {
            btn.addEventListener('click', function() {
                const productName = this.getAttribute('data-product-name');
                if (productName) {
                    setTimeout(() => {
                        alert(`${productName} added to cart!`);
                    }, 500);
                }
            });
        });
    }

    // Star rating system for reviews
    const ratingInputs = document.querySelectorAll('.rating-input');
    const ratingValue = document.getElementById('rating-value');
    
    if (ratingInputs.length && ratingValue) {
        ratingInputs.forEach(input => {
            input.addEventListener('click', function() {
                ratingValue.value = this.value;
                
                // Visual feedback - highlight selected stars
                ratingInputs.forEach(star => {
                    if (star.value <= this.value) {
                        star.nextElementSibling.classList.add('text-warning');
                    } else {
                        star.nextElementSibling.classList.remove('text-warning');
                    }
                });
            });
        });
    }

    // Command injection demo in profile update
    const profilePictureInput = document.getElementById('profile-picture');
    const commandWarning = document.getElementById('command-warning');
    
    if (profilePictureInput && commandWarning) {
        profilePictureInput.addEventListener('input', function() {
            if (this.value.includes(';') || this.value.includes('|') || this.value.includes('&')) {
                commandWarning.classList.remove('d-none');
            } else {
                commandWarning.classList.add('d-none');
            }
        });
    }
});
