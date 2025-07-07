// Enhanced EverTrust Insurance Management System JavaScript

// Global variables
let currentTheme = 'light';
let animationsEnabled = true;

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    initializeApp();
    setupEventListeners();
    setupAnimations();
    setupFormValidation();
    setupInteractiveElements();
    setupThemeToggle();
    setupNotifications();
});

// Main initialization function
function initializeApp() {
    console.log('🚀 EverTrust Insurance System Initialized');
    
    // Add loading animation to body
    document.body.classList.add('fade-in');
    
    // Initialize tooltips
    initializeTooltips();
    
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeCharts();
    }
    
    // Setup auto-save for forms
    setupAutoSave();
    
    // Initialize search functionality
    initializeSearch();
}

// Setup event listeners
function setupEventListeners() {
    // Form submission handling
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
        form.addEventListener('input', handleFormInput);
    });
    
    // Coverage level change handling
    setupCoverageLevelHandler();
    
    // Button click effects
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRippleEffect);
        button.addEventListener('mouseenter', handleButtonHover);
        button.addEventListener('mouseleave', handleButtonLeave);
    });
    
    // Card hover effects
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', handleCardHover);
        card.addEventListener('mouseleave', handleCardLeave);
    });
    
    // Table row interactions
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', handleRowClick);
        row.addEventListener('mouseenter', handleRowHover);
    });
    
    // Navigation smooth scrolling
    const navLinks = document.querySelectorAll('a[href^="#"]');
    navLinks.forEach(link => {
        link.addEventListener('click', handleSmoothScroll);
    });
    
    // Print functionality
    const printButtons = document.querySelectorAll('.btn-print');
    printButtons.forEach(button => {
        button.addEventListener('click', handlePrint);
    });
    
    // Copy to clipboard functionality
    const copyButtons = document.querySelectorAll('.btn-copy');
    copyButtons.forEach(button => {
        button.addEventListener('click', handleCopyToClipboard);
    });
}

// Enhanced form validation
function setupFormValidation() {
    const inputs = document.querySelectorAll('input, select, textarea');
    
    inputs.forEach(input => {
        // Real-time validation
        input.addEventListener('blur', validateField);
        input.addEventListener('input', clearFieldError);
        
        // Auto-formatting for specific fields
        if (input.type === 'tel') {
            input.addEventListener('input', formatPhoneNumber);
        }
        
        if (input.type === 'email') {
            input.addEventListener('input', validateEmail);
        }
    });
}

// Field validation
function validateField(event) {
    const field = event.target;
    const value = field.value.trim();
    const fieldName = field.name;
    
    // Remove existing error
    clearFieldError(event);
    
    // Validation rules
    const rules = {
        'email': {
            required: true,
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Please enter a valid email address'
        },
        'phone': {
            required: true,
            pattern: /^[\+]?([0-9]{1,3})?([0-9]{7,15})$/,
            message: 'Please enter a valid phone number'
        },
        'amount': {
            required: true,
            pattern: /^\d+(\.\d{1,2})?$/,
            message: 'Please enter a valid amount'
        }
    };
    
    // Only require certificate_id to be non-empty
    if (fieldName === 'certificate_id') {
        if (!value) {
            showFieldError(field, 'This field is required');
        }
        return;
    }
    
    const rule = rules[fieldName];
    if (!rule) return;
    
    if (rule.required && !value) {
        showFieldError(field, 'This field is required');
        return;
    }
    
    if (rule.pattern && !rule.pattern.test(value)) {
        showFieldError(field, rule.message);
        return;
    }
}

// Show field error
function showFieldError(field, message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'field-error';
    errorDiv.textContent = message;
    errorDiv.style.cssText = `
        color: #dc2626;
        font-size: 0.875rem;
        margin-top: 0.5rem;
        padding: 0.5rem;
        background: #fee2e2;
        border-radius: 0.5rem;
        border-left: 4px solid #dc2626;
        animation: slideIn 0.3s ease-out;
    `;
    
    field.parentNode.appendChild(errorDiv);
    field.classList.add('is-invalid');
}

// Clear field error
function clearFieldError(event) {
    const field = event.target;
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
        field.classList.remove('is-invalid');
    }
}

// Format phone number
function formatPhoneNumber(event) {
    let value = event.target.value.replace(/\D/g, '');
    if (value.length > 0) {
        value = value.match(/(\d{0,3})(\d{0,3})(\d{0,4})/);
        event.target.value = !value[2] ? value[1] : `(${value[1]}) ${value[2]}${value[3] ? `-${value[3]}` : ''}`;
    }
}

// Validate email
function validateEmail(event) {
    const email = event.target.value;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    
    if (email && !emailRegex.test(email)) {
        showFieldError(event.target, 'Please enter a valid email address');
    }
}

// Enhanced form submission
function handleFormSubmit(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    // Show loading state
    if (submitButton) {
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="loading"></span> Processing...';
        submitButton.disabled = true;
        
        // Reset button after 3 seconds (for demo purposes)
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }, 3000);
    }
    
    // Validate all fields
    const inputs = form.querySelectorAll('input, select, textarea');
    let isValid = true;
    
    inputs.forEach(input => {
        input.dispatchEvent(new Event('blur'));
        if (input.classList.contains('is-invalid')) {
            isValid = false;
        }
    });
    
    if (!isValid) {
        event.preventDefault();
        showNotification('Please correct the errors in the form', 'error');
        return;
    }
    
    // Show success notification
    showNotification('Form submitted successfully!', 'success');
}

// Form input handling
function handleFormInput(event) {
    const field = event.target;
    const value = field.value;
    
    // Auto-save functionality
    if (field.dataset.autosave) {
        debounce(() => {
            saveFormData(field.form);
        }, 1000)();
    }
}

// Auto-save functionality
function setupAutoSave() {
    const forms = document.querySelectorAll('form[data-autosave]');
    forms.forEach(form => {
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.dataset.autosave = 'true';
        });
    });
}

// Save form data
function saveFormData(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    // Save to localStorage
    localStorage.setItem(`form_${form.id || 'default'}`, JSON.stringify(data));
    
    // Show auto-save notification
    showNotification('Form data auto-saved', 'info', 2000);
}

// Enhanced animations
function setupAnimations() {
    if (!animationsEnabled) return;
    
    // Intersection Observer for scroll animations
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, observerOptions);
    
    // Observe elements for animation
    const animateElements = document.querySelectorAll('.card, .btn, .table-row');
    animateElements.forEach(el => {
        observer.observe(el);
    });
    
    // Parallax effect for hero section
    const heroSection = document.querySelector('.hero-section');
    if (heroSection) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.5;
            heroSection.style.transform = `translateY(${rate}px)`;
        });
    }
}

// Interactive elements setup
function setupInteractiveElements() {
    // Tooltip initialization
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
    
    // Modal functionality
    const modalTriggers = document.querySelectorAll('[data-modal]');
    modalTriggers.forEach(trigger => {
        trigger.addEventListener('click', openModal);
    });
    
    // Close modal on backdrop click
    document.addEventListener('click', (event) => {
        if (event.target.classList.contains('modal')) {
            closeModal(event.target);
        }
    });
    
    // Close modal on escape key
    document.addEventListener('keydown', (event) => {
        if (event.key === 'Escape') {
            const openModal = document.querySelector('.modal.show');
            if (openModal) {
                closeModal(openModal);
            }
        }
    });
}

// Tooltip functionality
function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.dataset.tooltip;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'custom-tooltip';
    tooltip.textContent = tooltipText;
    tooltip.style.cssText = `
        position: absolute;
        background: #1e293b;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.5rem;
        font-size: 0.875rem;
        z-index: 1000;
        pointer-events: none;
        opacity: 0;
        transform: translateY(10px);
        transition: all 0.3s ease;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
    `;
    
    document.body.appendChild(tooltip);
    
    const rect = element.getBoundingClientRect();
    tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
    tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
    
    setTimeout(() => {
        tooltip.style.opacity = '1';
        tooltip.style.transform = 'translateY(0)';
    }, 10);
    
    element.tooltip = tooltip;
}

function hideTooltip(event) {
    const element = event.target;
    if (element.tooltip) {
        element.tooltip.remove();
        element.tooltip = null;
    }
}

// Modal functionality
function openModal(event) {
    const modalId = event.target.dataset.modal;
    const modal = document.getElementById(modalId);
    
    if (modal) {
        modal.classList.add('show');
        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
        
        // Focus first input in modal
        const firstInput = modal.querySelector('input, select, textarea');
        if (firstInput) {
            firstInput.focus();
        }
    }
}

function closeModal(modal) {
    modal.classList.remove('show');
    modal.style.display = 'none';
    document.body.style.overflow = '';
}

// Theme toggle functionality
function setupThemeToggle() {
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.addEventListener('click', toggleTheme);
    }
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme') || 'light';
    setTheme(savedTheme);
}

function toggleTheme() {
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    localStorage.setItem('theme', newTheme);
}

function setTheme(theme) {
    currentTheme = theme;
    document.documentElement.setAttribute('data-theme', theme);
    
    // Update theme toggle button
    const themeToggle = document.querySelector('.theme-toggle');
    if (themeToggle) {
        themeToggle.innerHTML = theme === 'light' ? '🌙' : '☀️';
    }
}

// Notification system
function setupNotifications() {
    // Create notification container
    const notificationContainer = document.createElement('div');
    notificationContainer.id = 'notification-container';
    notificationContainer.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        z-index: 9999;
        display: flex;
        flex-direction: column;
        gap: 10px;
    `;
    document.body.appendChild(notificationContainer);
}

function showNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <span class="notification-icon">${getNotificationIcon(type)}</span>
            <span class="notification-message">${message}</span>
            <button class="notification-close" onclick="this.parentElement.parentElement.remove()">×</button>
        </div>
    `;
    
    notification.style.cssText = `
        background: white;
        border-radius: 1rem;
        padding: 1rem 1.5rem;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
        border-left: 4px solid ${getNotificationColor(type)};
        transform: translateX(100%);
        opacity: 0;
        transition: all 0.3s ease;
        min-width: 300px;
    `;
    
    const container = document.getElementById('notification-container');
    container.appendChild(notification);
    
    // Animate in
    setTimeout(() => {
        notification.style.transform = 'translateX(0)';
        notification.style.opacity = '1';
    }, 10);
    
    // Auto remove
    if (duration > 0) {
        setTimeout(() => {
            notification.style.transform = 'translateX(100%)';
            notification.style.opacity = '0';
            setTimeout(() => {
                notification.remove();
            }, 300);
        }, duration);
    }
}

function getNotificationIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

function getNotificationColor(type) {
    const colors = {
        success: '#059669',
        error: '#dc2626',
        warning: '#d97706',
        info: '#0891b2'
    };
    return colors[type] || colors.info;
}

// Button effects
function createRippleEffect(event) {
    const button = event.currentTarget;
    const ripple = document.createElement('span');
    const rect = button.getBoundingClientRect();
    const size = Math.max(rect.width, rect.height);
    const x = event.clientX - rect.left - size / 2;
    const y = event.clientY - rect.top - size / 2;
    
    ripple.style.cssText = `
        position: absolute;
        width: ${size}px;
        height: ${size}px;
        left: ${x}px;
        top: ${y}px;
        background: rgba(255, 255, 255, 0.3);
        border-radius: 50%;
        transform: scale(0);
        animation: ripple 0.6s linear;
        pointer-events: none;
    `;
    
    button.appendChild(ripple);
    
    setTimeout(() => {
        ripple.remove();
    }, 600);
}

function handleButtonHover(event) {
    const button = event.currentTarget;
    button.style.transform = 'translateY(-2px) scale(1.05)';
}

function handleButtonLeave(event) {
    const button = event.currentTarget;
    button.style.transform = 'translateY(0) scale(1)';
}

// Card effects
function handleCardHover(event) {
    const card = event.currentTarget;
    card.style.transform = 'translateY(-8px) scale(1.02)';
    card.style.boxShadow = '0 20px 40px rgba(0, 0, 0, 0.15)';
}

function handleCardLeave(event) {
    const card = event.currentTarget;
    card.style.transform = 'translateY(0) scale(1)';
    card.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
}

// Table row effects
function handleRowClick(event) {
    const row = event.currentTarget;
    row.classList.toggle('selected');
}

function handleRowHover(event) {
    const row = event.currentTarget;
    row.style.transform = 'scale(1.01)';
}

// Smooth scrolling
function handleSmoothScroll(event) {
    event.preventDefault();
    const targetId = event.currentTarget.getAttribute('href');
    const targetElement = document.querySelector(targetId);
    
    if (targetElement) {
        targetElement.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// Print functionality
function handlePrint(event) {
    event.preventDefault();
    window.print();
}

// Copy to clipboard
function handleCopyToClipboard(event) {
    event.preventDefault();
    const button = event.currentTarget;
    const textToCopy = button.dataset.copy || button.textContent;
    
    navigator.clipboard.writeText(textToCopy).then(() => {
        const originalText = button.innerHTML;
        button.innerHTML = '✅ Copied!';
        button.style.background = '#059669';
        
        setTimeout(() => {
            button.innerHTML = originalText;
            button.style.background = '';
        }, 2000);
        
        showNotification('Copied to clipboard!', 'success', 2000);
    }).catch(() => {
        showNotification('Failed to copy to clipboard', 'error');
    });
}

// Search functionality
function initializeSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performSearch, 300));
    }
}

function performSearch(event) {
    const searchTerm = event.target.value.toLowerCase();
    const searchableElements = document.querySelectorAll('[data-search]');
    
    searchableElements.forEach(element => {
        const searchText = element.dataset.search.toLowerCase();
        const isMatch = searchText.includes(searchTerm);
        
        element.style.display = isMatch ? '' : 'none';
        
        if (isMatch) {
            element.classList.add('search-highlight');
        } else {
            element.classList.remove('search-highlight');
        }
    });
}

// Utility functions
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

function initializeTooltips() {
    // Bootstrap tooltips if available
    if (typeof bootstrap !== 'undefined' && bootstrap.Tooltip) {
        const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
        tooltipTriggerList.map(function (tooltipTriggerEl) {
            return new bootstrap.Tooltip(tooltipTriggerEl);
        });
    }
}

function initializeCharts() {
    // Initialize charts if Chart.js is available
    const chartElements = document.querySelectorAll('canvas[data-chart]');
    chartElements.forEach(canvas => {
        const ctx = canvas.getContext('2d');
        const chartType = canvas.dataset.chart;
        const chartData = JSON.parse(canvas.dataset.chartData || '{}');
        
        new Chart(ctx, {
            type: chartType,
            data: chartData,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'top',
                    }
                }
            }
        });
    });
}

// Setup coverage level change handler
function setupCoverageLevelHandler() {
    const coverageLevelSelect = document.querySelector('select[name="coverage_level"]');
    if (coverageLevelSelect) {
        coverageLevelSelect.addEventListener('change', handleCoverageLevelChange);
        
        // Set initial values based on current selection
        handleCoverageLevelChange({ target: coverageLevelSelect });
    }
}

// Handle coverage level changes
function handleCoverageLevelChange(event) {
    const coverageLevel = event.target.value;
    const defaults = getCoverageDefaults(coverageLevel);
    
    // Update form fields with new defaults
    Object.keys(defaults).forEach(fieldName => {
        const field = document.querySelector(`[name="${fieldName}"]`);
        if (field) {
            field.value = defaults[fieldName];
            
            // Trigger change event to update any dependent fields
            const changeEvent = new Event('change', { bubbles: true });
            field.dispatchEvent(changeEvent);
        }
    });
    
    // Show notification
    showNotification(`Coverage level changed to ${event.target.options[event.target.selectedIndex].text}`, 'info', 3000);
}

// Get coverage defaults based on level
function getCoverageDefaults(level) {
    const defaults = {
        'comprehensive': {
            'insured_amount': '10000000',
            'liability_per_person': '5000000',
            'liability_per_occurrence': '5000000',
            'liability_aggregate': '5000000',
            'net_contribution': '10000',
            'proportional_stamp': '500',
            'dimensional_stamp': '2',
            'supervision_fees': '89.97',
            'insurance_fees': '58.03',
            'total_premium': '10650',
            'premium_amount': '10650',
            'total_premium_words': 'Ten Thousand Six Hundred Fifty US Dollars'
        },
        'basic': {
            'insured_amount': '2000000',
            'liability_per_person': '100000',
            'liability_per_occurrence': '500000',
            'liability_aggregate': '1000000',
            'net_contribution': '5000',
            'proportional_stamp': '0',
            'dimensional_stamp': '0',
            'supervision_fees': '0',
            'insurance_fees': '0',
            'total_premium': '5000',
            'premium_amount': '5000',
            'total_premium_words': 'Five Thousand US Dollars'
        },
        'standard': {
            'insured_amount': '5000000',
            'liability_per_person': '500000',
            'liability_per_occurrence': '1500000',
            'liability_aggregate': '2500000',
            'net_contribution': '7000',
            'proportional_stamp': '250',
            'dimensional_stamp': '1',
            'supervision_fees': '45',
            'insurance_fees': '30',
            'total_premium': '7326',
            'premium_amount': '7326',
            'total_premium_words': 'Seven Thousand Three Hundred Twenty-Six US Dollars'
        },
        'premium': {
            'insured_amount': '8000000',
            'liability_per_person': '1000000',
            'liability_per_occurrence': '3000000',
            'liability_aggregate': '4000000',
            'net_contribution': '8500',
            'proportional_stamp': '350',
            'dimensional_stamp': '1.5',
            'supervision_fees': '60',
            'insurance_fees': '40',
            'total_premium': '8951.5',
            'premium_amount': '8951.5',
            'total_premium_words': 'Eight Thousand Nine Hundred Fifty-One and 50/100 US Dollars'
        },
        'elite': {
            'insured_amount': '20000000',
            'liability_per_person': '10000000',
            'liability_per_occurrence': '10000000',
            'liability_aggregate': '10000000',
            'net_contribution': '20000',
            'proportional_stamp': '1000',
            'dimensional_stamp': '5',
            'supervision_fees': '150',
            'insurance_fees': '100',
            'total_premium': '21255',
            'premium_amount': '21255',
            'total_premium_words': 'Twenty-One Thousand Two Hundred Fifty-Five US Dollars'
        }
    };
    
    return defaults[level] || defaults['basic'];
}

// Export functions for global access
window.EverTrust = {
    showNotification,
    toggleTheme,
    validateField,
    formatPhoneNumber,
    formatCertificateId,
    openModal,
    closeModal,
    handleCoverageLevelChange,
    getCoverageDefaults
};

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(4);
            opacity: 0;
        }
    }
    
    .search-highlight {
        background: yellow;
        animation: highlight 0.5s ease;
    }
    
    @keyframes highlight {
        0% { background: yellow; }
        100% { background: transparent; }
    }
    
    .selected {
        background: rgba(37, 99, 235, 0.1) !important;
        border-left: 4px solid #2563eb;
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.75rem;
    }
    
    .notification-icon {
        font-size: 1.2rem;
    }
    
    .notification-message {
        flex: 1;
        font-weight: 500;
    }
    
    .notification-close {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        color: #64748b;
        padding: 0;
        line-height: 1;
    }
    
    .notification-close:hover {
        color: #1e293b;
    }
    
    .field-error {
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-5px); }
        75% { transform: translateX(5px); }
    }
    
    .is-invalid {
        border-color: #dc2626 !important;
        box-shadow: 0 0 0 4px rgba(220, 38, 38, 0.1) !important;
    }
`;
document.head.appendChild(style); 