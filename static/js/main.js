// Main JavaScript for EverChat

document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips and popovers
    initializeBootstrapComponents();
    
    // Handle like buttons
    initializeLikeButtons();
    
    // Handle image preview for file uploads
    initializeImagePreview();
    
    // Handle comment toggles
    initializeCommentToggles();
});

function initializeBootstrapComponents() {
    // Initialize Bootstrap tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Initialize Bootstrap popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
}

function initializeLikeButtons() {
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', function() {
            const postId = this.getAttribute('data-post-id');
            const heartIcon = this.querySelector('i');
            const likeCount = document.querySelector(`.like-count-${postId}`);
            
            // Add loading state
            this.disabled = true;
            heartIcon.classList.add('fa-spin');
            
            fetch(`/like_post/${postId}`)
                .then(response => response.json())
                .then(data => {
                    // Update heart icon
                    if (data.action === 'liked') {
                        heartIcon.className = 'fas fa-heart fa-lg text-danger';
                        this.classList.add('liked');
                    } else {
                        heartIcon.className = 'far fa-heart fa-lg';
                        this.classList.remove('liked');
                    }
                    
                    // Update like count
                    likeCount.textContent = data.like_count;
                })
                .catch(error => {
                    console.error('Error:', error);
                    showNotification('Error liking post', 'error');
                })
                .finally(() => {
                    // Remove loading state
                    this.disabled = false;
                    heartIcon.classList.remove('fa-spin');
                });
        });
    });
}

function initializeImagePreview() {
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    
    imageInputs.forEach(input => {
        input.addEventListener('change', function(event) {
            const file = event.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    // Create or update preview
                    let preview = document.getElementById('image-preview');
                    if (!preview) {
                        preview = document.createElement('div');
                        preview.id = 'image-preview';
                        preview.className = 'mt-3';
                        input.parentNode.appendChild(preview);
                    }
                    
                    preview.innerHTML = `
                        <div class="position-relative d-inline-block">
                            <img src="${e.target.result}" class="img-thumbnail" style="max-width: 200px; max-height: 200px;">
                            <button type="button" class="btn btn-sm btn-danger position-absolute top-0 end-0" onclick="removeImagePreview()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    `;
                };
                reader.readAsDataURL(file);
            }
        });
    });
}

function removeImagePreview() {
    const preview = document.getElementById('image-preview');
    const fileInput = document.querySelector('input[type="file"][accept*="image"]');
    
    if (preview) {
        preview.remove();
    }
    if (fileInput) {
        fileInput.value = '';
    }
}

function initializeCommentToggles() {
    window.toggleComments = function(postId) {
        const commentsSection = document.getElementById(`comments-${postId}`);
        if (commentsSection) {
            if (commentsSection.style.display === 'none') {
                commentsSection.style.display = 'block';
            } else {
                commentsSection.style.display = 'none';
            }
        }
    };
}

function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    notification.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
    notification.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    document.body.appendChild(notification);
    
    // Auto remove after 5 seconds
    setTimeout(() => {
        if (notification.parentNode) {
            notification.remove();
        }
    }, 5000);
}

// Smooth scrolling for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Handle form submissions with loading states
document.querySelectorAll('form').forEach(form => {
    form.addEventListener('submit', function() {
        const submitButton = this.querySelector('button[type="submit"]');
        if (submitButton) {
            submitButton.disabled = true;
            submitButton.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Loading...';
        }
    });
});

// Auto-resize textareas
document.querySelectorAll('textarea').forEach(textarea => {
    textarea.addEventListener('input', function() {
        this.style.height = 'auto';
        this.style.height = (this.scrollHeight) + 'px';
    });
});

// Infinite scroll for posts (future enhancement)
let isLoading = false;
let currentPage = 1;

function loadMorePosts() {
    if (isLoading) return;
    
    isLoading = true;
    // Implementation for infinite scroll would go here
    // For now, this is just a placeholder
    
    setTimeout(() => {
        isLoading = false;
    }, 1000);
}

// Handle scroll events for infinite loading
window.addEventListener('scroll', function() {
    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight - 1000) {
        // Load more posts when near bottom
        // loadMorePosts();
    }
});

// Handle escape key to close modals
document.addEventListener('keydown', function(event) {
    if (event.key === 'Escape') {
        // Close any open modals or overlays
        const activeModal = document.querySelector('.modal.show');
        if (activeModal) {
            const modal = bootstrap.Modal.getInstance(activeModal);
            if (modal) {
                modal.hide();
            }
        }
    }
});

// Handle click outside to close dropdowns
document.addEventListener('click', function(event) {
    const dropdowns = document.querySelectorAll('.dropdown-menu.show');
    dropdowns.forEach(dropdown => {
        if (!dropdown.contains(event.target) && !dropdown.previousElementSibling.contains(event.target)) {
            dropdown.classList.remove('show');
        }
    });
});

// Performance optimization: Lazy load images
function initializeLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
}

// Initialize lazy loading if supported
if ('IntersectionObserver' in window) {
    initializeLazyLoading();
}
