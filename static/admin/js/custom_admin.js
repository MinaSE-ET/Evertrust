// Custom Admin JavaScript for EverTrust Insurance Management

document.addEventListener('DOMContentLoaded', function() {
    initializeAdminInterface();
    setupAdminEventListeners();
    setupAdminAnimations();
    setupAdminCharts();
    setupAdminNotifications();
});

// Initialize admin interface
function initializeAdminInterface() {
    console.log('🚀 EverTrust Admin Interface Initialized');
    
    // Add admin-specific classes
    document.body.classList.add('admin-interface');
    
    // Initialize tooltips
    initializeAdminTooltips();
    
    // Setup auto-refresh for dashboard
    setupAutoRefresh();
    
    // Initialize search functionality
    initializeAdminSearch();
    
    // Setup bulk actions
    setupBulkActions();
}

// Setup admin event listeners
function setupAdminEventListeners() {
    // Dashboard card interactions
    const dashboardCards = document.querySelectorAll('.stat-card, .dashboard-card');
    dashboardCards.forEach(card => {
        card.addEventListener('click', handleCardClick);
        card.addEventListener('mouseenter', handleCardHover);
        card.addEventListener('mouseleave', handleCardLeave);
    });
    
    // Table row interactions
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach(row => {
        row.addEventListener('click', handleRowClick);
        row.addEventListener('dblclick', handleRowDoubleClick);
    });
    
    // Form enhancements
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', handleFormSubmit);
        form.addEventListener('input', handleFormInput);
    });
    
    // Button enhancements
    const buttons = document.querySelectorAll('.btn, .admin-btn');
    buttons.forEach(button => {
        button.addEventListener('click', createRippleEffect);
        button.addEventListener('mouseenter', handleButtonHover);
        button.addEventListener('mouseleave', handleButtonHover);
    });
    
    // Quick actions
    const quickActions = document.querySelectorAll('.quick-actions a');
    quickActions.forEach(action => {
        action.addEventListener('click', handleQuickAction);
    });
}

// Admin animations
function setupAdminAnimations() {
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
    
    // Observe admin elements
    const adminElements = document.querySelectorAll('.stat-card, .dashboard-card, .module, .quick-actions');
    adminElements.forEach(el => {
        observer.observe(el);
    });
    
    // Parallax effect for admin header
    const adminHeader = document.querySelector('#header');
    if (adminHeader) {
        window.addEventListener('scroll', () => {
            const scrolled = window.pageYOffset;
            const rate = scrolled * -0.3;
            adminHeader.style.transform = `translateY(${rate}px)`;
        });
    }
}

// Admin charts setup
function setupAdminCharts() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initializeDashboardCharts();
    }
}

// Initialize dashboard charts
function initializeDashboardCharts() {
    // Certificate Status Chart
    const statusCtx = document.getElementById('statusChart');
    if (statusCtx) {
        new Chart(statusCtx, {
            type: 'doughnut',
            data: {
                labels: ['Active', 'Expired', 'Pending', 'Cancelled'],
                datasets: [{
                    data: [65, 15, 15, 5],
                    backgroundColor: [
                        '#059669',
                        '#dc2626',
                        '#d97706',
                        '#64748b'
                    ],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom',
                        labels: {
                            padding: 20,
                            usePointStyle: true
                        }
                    }
                }
            }
        });
    }
    
    // Revenue Chart
    const revenueCtx = document.getElementById('revenueChart');
    if (revenueCtx) {
        new Chart(revenueCtx, {
            type: 'line',
            data: {
                labels: ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
                datasets: [{
                    label: 'Revenue',
                    data: [12000, 19000, 15000, 25000, 22000, 30000],
                    borderColor: '#2563eb',
                    backgroundColor: 'rgba(37, 99, 235, 0.1)',
                    tension: 0.4,
                    fill: true
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        grid: {
                            color: 'rgba(0, 0, 0, 0.1)'
                        }
                    },
                    x: {
                        grid: {
                            display: false
                        }
                    }
                }
            }
        });
    }
}

// Admin notifications
function setupAdminNotifications() {
    // Create notification container if it doesn't exist
    if (!document.getElementById('admin-notification-container')) {
        const container = document.createElement('div');
        container.id = 'admin-notification-container';
        container.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 9999;
            display: flex;
            flex-direction: column;
            gap: 10px;
        `;
        document.body.appendChild(container);
    }
}

// Show admin notification
function showAdminNotification(message, type = 'info', duration = 5000) {
    const notification = document.createElement('div');
    notification.className = `admin-notification admin-notification-${type}`;
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
    
    const container = document.getElementById('admin-notification-container');
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

// Get notification icon
function getNotificationIcon(type) {
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    return icons[type] || icons.info;
}

// Get notification color
function getNotificationColor(type) {
    const colors = {
        success: '#059669',
        error: '#dc2626',
        warning: '#d97706',
        info: '#0891b2'
    };
    return colors[type] || colors.info;
}

// Card interactions
function handleCardClick(event) {
    const card = event.currentTarget;
    const cardType = card.dataset.type;
    
    if (cardType === 'certificates') {
        window.location.href = '/admin/certificates/certificate/';
    } else if (cardType === 'verifications') {
        window.location.href = '/admin/certificates/certificateverification/';
    } else if (cardType === 'transactions') {
        window.location.href = '/admin/certificates/financialtransaction/';
    } else if (cardType === 'revenue') {
        showAdminNotification('Revenue details will be displayed here', 'info');
    }
}

function handleCardHover(event) {
    const card = event.currentTarget;
    card.style.transform = 'translateY(-5px) scale(1.02)';
    card.style.boxShadow = '0 15px 35px rgba(0, 0, 0, 0.15)';
}

function handleCardLeave(event) {
    const card = event.currentTarget;
    card.style.transform = 'translateY(0) scale(1)';
    card.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
}

// Row interactions
function handleRowClick(event) {
    const row = event.currentTarget;
    row.classList.toggle('selected');
    
    // Update bulk action buttons
    updateBulkActions();
}

function handleRowDoubleClick(event) {
    const row = event.currentTarget;
    const editLink = row.querySelector('a[href*="change"]');
    if (editLink) {
        window.location.href = editLink.href;
    }
}

// Form handling
function handleFormSubmit(event) {
    const form = event.target;
    const submitButton = form.querySelector('button[type="submit"]');
    
    if (submitButton) {
        const originalText = submitButton.innerHTML;
        submitButton.innerHTML = '<span class="admin-loading"></span> Processing...';
        submitButton.disabled = true;
        
        // Reset button after 3 seconds
        setTimeout(() => {
            submitButton.innerHTML = originalText;
            submitButton.disabled = false;
        }, 3000);
    }
    
    showAdminNotification('Form submitted successfully!', 'success');
}

function handleFormInput(event) {
    const field = event.target;
    
    // Auto-save functionality
    if (field.dataset.autosave) {
        debounce(() => {
            saveFormData(field.form);
        }, 1000)();
    }
    
    // Real-time validation
    validateField(field);
}

// Button interactions
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

// Quick actions
function handleQuickAction(event) {
    const action = event.currentTarget;
    const actionType = action.dataset.action;
    
    switch (actionType) {
        case 'add_certificate':
            window.location.href = '/admin/certificates/certificate/add/';
            break;
        case 'view_certificates':
            window.location.href = '/admin/certificates/certificate/';
            break;
        case 'view_verifications':
            window.location.href = '/admin/certificates/certificateverification/';
            break;
        case 'view_transactions':
            window.location.href = '/admin/certificates/financialtransaction/';
            break;
        case 'export_data':
            showExportModal();
            break;
        default:
            showAdminNotification('Action not implemented yet', 'warning');
    }
}

// Bulk actions
function setupBulkActions() {
    const bulkActionForm = document.querySelector('#changelist-form');
    if (bulkActionForm) {
        const checkboxes = bulkActionForm.querySelectorAll('input[type="checkbox"]');
        checkboxes.forEach(checkbox => {
            checkbox.addEventListener('change', updateBulkActions);
        });
    }
}

function updateBulkActions() {
    const selectedRows = document.querySelectorAll('tbody tr.selected');
    const bulkActionButtons = document.querySelectorAll('.bulk-action-btn');
    
    bulkActionButtons.forEach(button => {
        button.disabled = selectedRows.length === 0;
    });
    
    // Update counter
    const counter = document.querySelector('.selected-count');
    if (counter) {
        counter.textContent = selectedRows.length;
    }
}

// Auto refresh
function setupAutoRefresh() {
    const refreshInterval = 30000; // 30 seconds
    
    setInterval(() => {
        // Only refresh if user is on dashboard
        if (window.location.pathname === '/admin/' || window.location.pathname.includes('dashboard')) {
            refreshDashboardStats();
        }
    }, refreshInterval);
}

function refreshDashboardStats() {
    // Fetch updated stats via AJAX
    fetch('/admin/api/dashboard-stats/')
        .then(response => response.json())
        .then(data => {
            updateDashboardStats(data);
        })
        .catch(error => {
            console.error('Error refreshing dashboard stats:', error);
        });
}

function updateDashboardStats(data) {
    // Update stat cards
    Object.keys(data).forEach(key => {
        const element = document.querySelector(`[data-stat="${key}"]`);
        if (element) {
            element.textContent = data[key];
        }
    });
}

// Admin search
function initializeAdminSearch() {
    const searchInput = document.querySelector('.search-input');
    if (searchInput) {
        searchInput.addEventListener('input', debounce(performAdminSearch, 300));
    }
}

function performAdminSearch(event) {
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

// Export modal
function showExportModal() {
    const modal = document.createElement('div');
    modal.className = 'admin-modal-overlay';
    modal.innerHTML = `
        <div class="admin-modal">
            <div class="admin-modal-header">
                <h3>Export Data</h3>
            </div>
            <div class="admin-modal-body">
                <div class="form-group">
                    <label>Data Type</label>
                    <select id="exportType">
                        <option value="certificates">Certificates</option>
                        <option value="verifications">Verifications</option>
                        <option value="transactions">Transactions</option>
                    </select>
                </div>
                <div class="form-group">
                    <label>Format</label>
                    <select id="exportFormat">
                        <option value="csv">CSV</option>
                        <option value="json">JSON</option>
                    </select>
                </div>
            </div>
            <div class="admin-modal-footer">
                <button class="admin-btn admin-btn-secondary" onclick="closeExportModal()">Cancel</button>
                <button class="admin-btn" onclick="exportData()">Export</button>
            </div>
        </div>
    `;
    
    modal.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0, 0, 0, 0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;
    
    document.body.appendChild(modal);
}

function closeExportModal() {
    const modal = document.querySelector('.admin-modal-overlay');
    if (modal) {
        modal.remove();
    }
}

function exportData() {
    const type = document.getElementById('exportType').value;
    const format = document.getElementById('exportFormat').value;
    
    const url = `/certificates/export/?model=${type}&format=${format}`;
    window.open(url, '_blank');
    
    closeExportModal();
    showAdminNotification('Export started successfully!', 'success');
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

function validateField(field) {
    const value = field.value.trim();
    const fieldName = field.name;
    clearFieldError(field);
    // Validation rules
    const rules = {
        'email': {
            pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
            message: 'Please enter a valid email address'
        },
        'amount': {
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
    if (rule.pattern && !rule.pattern.test(value)) {
        showFieldError(field, rule.message);
    }
}

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

function clearFieldError(field) {
    const errorDiv = field.parentNode.querySelector('.field-error');
    if (errorDiv) {
        errorDiv.remove();
        field.classList.remove('is-invalid');
    }
}

function saveFormData(form) {
    const formData = new FormData(form);
    const data = Object.fromEntries(formData);
    
    localStorage.setItem(`admin_form_${form.id || 'default'}`, JSON.stringify(data));
    showAdminNotification('Form data auto-saved', 'info', 2000);
}

// Initialize admin tooltips
function initializeAdminTooltips() {
    const tooltipElements = document.querySelectorAll('[data-tooltip]');
    tooltipElements.forEach(element => {
        element.addEventListener('mouseenter', showTooltip);
        element.addEventListener('mouseleave', hideTooltip);
    });
}

function showTooltip(event) {
    const element = event.target;
    const tooltipText = element.dataset.tooltip;
    
    const tooltip = document.createElement('div');
    tooltip.className = 'admin-tooltip-text';
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

// Export functions for global access
window.EverTrustAdmin = {
    showNotification: showAdminNotification,
    exportData,
    refreshDashboardStats,
    validateField
}; 