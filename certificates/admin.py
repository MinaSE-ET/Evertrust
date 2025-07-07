from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.db.models import Count, Sum, Q
from django.utils import timezone
from datetime import timedelta
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from .models import Certificate, CertificateVerification, FinancialTransaction, Payment, Installment, Invoice
from .models import generate_policy_number
from django.forms import DateInput, DateTimeInput
from django.db import models
from django.template.response import TemplateResponse
from django.urls import path
from .forms import CertificateForm

# Custom Admin Site
class EverTrustAdminSite(AdminSite):
    site_header = "EverTrust Insurance Management"
    site_title = "EverTrust Admin"
    index_title = "Insurance Management Dashboard"
    site_url = "/"
    
    def get_app_list(self, request):
        """Custom app list for the admin site"""
        app_list = []
        
        # Certificates App
        certificates_app = {
            'name': 'Certificate Management',
            'app_label': 'certificates',
            'app_url': reverse('admin:certificates_certificate_changelist'),
            'has_module_perms': True,
            'models': [
                {
                    'name': 'Certificates',
                    'object_name': 'certificate',
                    'admin_url': reverse('admin:certificates_certificate_changelist'),
                    'add_url': reverse('admin:certificates_certificate_add'),
                    'view_only': False,
                    'count': Certificate.objects.count(),
                },
                {
                    'name': 'Verifications',
                    'object_name': 'verification',
                    'admin_url': reverse('admin:certificates_certificateverification_changelist'),
                    'add_url': None,
                    'view_only': True,
                    'count': CertificateVerification.objects.count(),
                },
                {
                    'name': 'Financial Transactions',
                    'object_name': 'transaction',
                    'admin_url': reverse('admin:certificates_financialtransaction_changelist'),
                    'add_url': reverse('admin:certificates_financialtransaction_add'),
                    'view_only': False,
                    'count': FinancialTransaction.objects.count(),
                }
            ]
        }
        app_list.append(certificates_app)
        
        # System App
        system_app = {
            'name': 'System Management',
            'app_label': 'system',
            'app_url': '#',
            'has_module_perms': True,
            'models': [
                {
                    'name': 'Dashboard',
                    'object_name': 'dashboard',
                    'admin_url': reverse('admin:index'),
                    'add_url': None,
                    'view_only': True,
                },
                {
                    'name': 'Reports',
                    'object_name': 'reports',
                    'admin_url': reverse('admin:index') + 'reports/',
                    'add_url': None,
                    'view_only': True,
                },
                {
                    'name': 'Settings',
                    'object_name': 'settings',
                    'admin_url': reverse('admin:index') + 'settings/',
                    'add_url': None,
                    'view_only': True,
                }
            ]
        }
        app_list.append(system_app)
        
        return app_list

# Register the custom admin site
admin_site = EverTrustAdminSite(name='evertrust_admin')

# Enhanced Certificate Admin
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ('policy_number', 'client_name', 'coverage_level', 'net_contribution', 'total_premium')
    list_filter = [
        'certificate_type', 'coverage_level', 'status', 'payment_status',
        'start_date', 'end_date', 'issue_date', 'is_verified'
    ]
    search_fields = [
        'policy_number', 'client_name', 'client_email', 'client_phone',
        'client_id_number', 'agent_name', 'agent_id'
    ]
    readonly_fields = [
        'policy_number', 'issue_date', 'last_modified'
    ]
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']
    
    form = CertificateForm
    change_form_template = 'admin/certificates/certificate/change_form.html'
    
    fieldsets = (
        ('Policy Information', {
            'fields': ('policy_number', 'certificate_type', 'status', 'payment_status'),
            'description': 'Basic policy information. Policy number is auto-generated and read-only.'
        }),
        ('Insured Person', {
            'fields': ('client_name', 'client_id_number', 'client_date_of_birth', 'client_phone', 'client_email', 'client_address', 'client_bank_name', 'client_bank_account'),
            'description': 'Enter accurate client details. Email and phone are required. Bank information is optional.'
        }),
        ('Insurance Details', {
            'fields': (
                'coverage_level', 'insured_amount', 'premium_amount',
                'net_contribution', 'proportional_stamp', 'dimensional_stamp', 
                'supervision_fees', 'insurance_fees', 'total_premium', 'total_premium_words'
            ),
            'description': 'Coverage, liability, and premium details. Values update automatically based on coverage level.'
        }),
        ('Insurance Period', {
            'fields': ('period_from', 'period_to', 'start_date', 'end_date'),
            'description': 'Set the coverage period. Period dates sync with start/end dates.'
        }),
        ('Activity and Location Information', {
            'fields': ('location', 'activity', 'description_of_risk'),
            'description': 'Information about the insured activity and location.'
        }),
        ('Agent Information', {
            'fields': ('agent_name', 'agent_id'),
            'description': 'Agent details (optional).'
        }),
        ('Verification', {
            'fields': ('is_verified', 'verification_date'),
            'description': 'Certificate verification status.'
        }),
        ('Additional Information', {
            'fields': ('description', 'terms_conditions', 'special_conditions'),
            'classes': ('collapse',),
            'description': 'Optional additional information for the certificate.'
        }),
    )

    def colored_status(self, obj):
        color = 'success' if obj.status == 'active' else 'danger' if obj.status == 'expired' else 'warning'
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.get_status_display())
    colored_status.short_description = 'Status'
    colored_status.admin_order_field = 'status'

    def colored_payment_status(self, obj):
        color = 'success' if obj.payment_status == 'paid' else 'danger' if obj.payment_status == 'overdue' else 'warning'
        return format_html('<span class="badge bg-{}">{}</span>', color, obj.get_payment_status_display())
    colored_payment_status.short_description = 'Payment Status'
    colored_payment_status.admin_order_field = 'payment_status'

    def colored_verified(self, obj):
        color = 'success' if obj.is_verified else 'secondary'
        label = 'Verified' if obj.is_verified else 'Not Verified'
        return format_html('<span class="badge bg-{}">{}</span>', color, label)
    colored_verified.short_description = 'Verified'
    colored_verified.admin_order_field = 'is_verified'

    def save_model(self, request, obj, form, change):
        # Ensure policy number is always auto-generated and not editable
        if not obj.policy_number:
            new_policy = generate_policy_number()
            while Certificate.objects.filter(policy_number=new_policy).exists():
                new_policy = generate_policy_number()
            obj.policy_number = new_policy
        if 'is_verified' in form.changed_data and obj.is_verified:
            obj.verification_date = timezone.now()
        elif 'is_verified' in form.changed_data and not obj.is_verified:
            obj.verification_date = None
        super().save_model(request, obj, form, change)

    formfield_overrides = {
        models.DateField: {'widget': DateInput(attrs={'type': 'date'})},
        models.DateTimeField: {'widget': DateTimeInput(attrs={'type': 'datetime-local'})},
    }

# Enhanced Certificate Verification Admin
@admin.register(CertificateVerification)
class CertificateVerificationAdmin(admin.ModelAdmin):
    list_display = [
        'verification_code', 'certificate', 'status', 'verified_at', 'verified_by'
    ]
    list_filter = ['status', 'verified_at']
    search_fields = ['verification_code', 'certificate__policy_number', 'certificate__client_name']
    readonly_fields = ['id', 'verification_code', 'verified_at', 'ip_address', 'user_agent']
    date_hierarchy = 'verified_at'
    ordering = ['-verified_at']

# Enhanced Financial Transaction Admin
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_number', 'certificate', 'amount', 'payment_method', 
        'status', 'payment_date', 'due_date'
    ]
    list_filter = [
        'payment_method', 'status', 'payment_date', 'due_date'
    ]
    search_fields = [
        'payment_number', 'certificate__policy_number', 'certificate__client_name',
        'transaction_id', 'reference_number'
    ]
    readonly_fields = ['id', 'payment_number', 'payment_date', 'processed_date']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('id', 'payment_number', 'certificate', 'amount', 'payment_method', 'status')
        }),
        ('Dates', {
            'fields': ('payment_date', 'due_date', 'processed_date')
        }),
        ('Transaction Details', {
            'fields': ('transaction_id', 'reference_number')
        }),
        ('Additional Information', {
            'fields': ('description', 'notes')
        }),
        ('Processing Information', {
            'fields': ('processed_by', 'ip_address'),
            'classes': ('collapse',)
        }),
    )

@admin.register(Installment)
class InstallmentAdmin(admin.ModelAdmin):
    list_display = [
        'installment_number', 'certificate', 'amount', 'paid_amount', 
        'status', 'due_date', 'days_overdue_display'
    ]
    list_filter = ['status', 'due_date']
    search_fields = [
        'installment_number', 'certificate__policy_number', 'certificate__client_name'
    ]
    readonly_fields = ['id', 'days_overdue', 'remaining_amount']
    date_hierarchy = 'due_date'
    ordering = ['due_date']
    
    fieldsets = (
        ('Installment Information', {
            'fields': ('id', 'installment_number', 'certificate', 'amount', 'status')
        }),
        ('Payment Information', {
            'fields': ('paid_amount', 'paid_date', 'remaining_amount')
        }),
        ('Due Date Information', {
            'fields': ('due_date', 'days_overdue', 'late_fee', 'grace_period_days')
        }),
        ('Additional Information', {
            'fields': ('description', 'notes')
        }),
    )
    
    def days_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">{} days overdue</span>', obj.days_overdue)
        return "On time"
    days_overdue_display.short_description = "Overdue Status"

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = [
        'invoice_number', 'certificate', 'amount', 'tax_amount', 'total_amount',
        'status', 'issue_date', 'due_date', 'days_overdue_display'
    ]
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = [
        'invoice_number', 'certificate__policy_number', 'certificate__client_name'
    ]
    readonly_fields = ['id', 'invoice_number', 'issue_date', 'days_overdue', 'remaining_amount']
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']
    
    fieldsets = (
        ('Invoice Information', {
            'fields': ('id', 'invoice_number', 'certificate', 'status')
        }),
        ('Amounts', {
            'fields': ('amount', 'tax_amount', 'total_amount', 'paid_amount', 'remaining_amount')
        }),
        ('Dates', {
            'fields': ('issue_date', 'due_date', 'paid_date', 'days_overdue')
        }),
        ('Billing Information', {
            'fields': ('billing_address', 'billing_email')
        }),
        ('Additional Information', {
            'fields': ('description', 'terms_conditions', 'notes')
        }),
    )
    
    def days_overdue_display(self, obj):
        if obj.is_overdue:
            return format_html('<span style="color: red;">{} days overdue</span>', obj.days_overdue)
        return "On time"
    days_overdue_display.short_description = "Overdue Status"

@admin.register(FinancialTransaction)
class FinancialTransactionAdmin(admin.ModelAdmin):
    list_display = [
        'transaction_number', 'certificate', 'transaction_type', 'amount', 
        'status', 'transaction_date', 'processed_date'
    ]
    list_filter = [
        'transaction_type', 'status', 'transaction_date', 'processed_date'
    ]
    search_fields = [
        'transaction_number', 'certificate__policy_number', 'certificate__client_name',
        'reference', 'description'
    ]
    readonly_fields = ['id', 'transaction_number', 'transaction_date', 'processed_date']
    date_hierarchy = 'transaction_date'
    ordering = ['-transaction_date']
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('id', 'transaction_number', 'certificate', 'transaction_type', 'amount', 'status')
        }),
        ('Related Records', {
            'fields': ('payment', 'installment', 'invoice')
        }),
        ('Dates', {
            'fields': ('transaction_date', 'processed_date')
        }),
        ('Additional Information', {
            'fields': ('description', 'reference', 'notes')
        }),
        ('Processing Information', {
            'fields': ('processed_by',),
            'classes': ('collapse',)
        }),
    )

# Register models with custom admin site
admin_site.register(Certificate, CertificateAdmin)
admin_site.register(CertificateVerification, CertificateVerificationAdmin)
admin_site.register(Payment, PaymentAdmin)
admin_site.register(Installment, InstallmentAdmin)
admin_site.register(Invoice, InvoiceAdmin)
admin_site.register(FinancialTransaction, FinancialTransactionAdmin)

# Admin Actions
@admin.action(description="Mark selected certificates as verified")
def mark_as_verified(modeladmin, request, queryset):
    queryset.update(is_verified=True)
    modeladmin.message_user(request, f"{queryset.count()} certificates marked as verified.")

@admin.action(description="Mark selected certificates as inactive")
def mark_as_inactive(modeladmin, request, queryset):
    queryset.update(status='cancelled')
    modeladmin.message_user(request, f"{queryset.count()} certificates marked as inactive.")

@admin.action(description="Generate PDF for selected certificates")
def generate_pdfs(modeladmin, request, queryset):
    # This would integrate with your PDF generation logic
    for certificate in queryset:
        # Generate PDF logic here
        pass
    modeladmin.message_user(request, f"PDF generation initiated for {queryset.count()} certificates.")

# Add actions to CertificateAdmin
CertificateAdmin.actions = [mark_as_verified, mark_as_inactive, generate_pdfs]

def get_admin_dashboard_context():
    """Get context data for admin dashboard"""
    now = timezone.now().date()
    start_of_month = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_day = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Certificate statistics
    total_certificates = Certificate.objects.count()
    active_certificates = Certificate.objects.filter(status='active', end_date__gte=now).count()
    valid_certificates = Certificate.objects.filter(status='active', end_date__gte=now).count()
    verified_certificates = Certificate.objects.filter(is_verified=True).count()
    
    # Verification statistics
    total_verifications = CertificateVerification.objects.filter(verified_at__gte=start_of_day).count()
    
    # Financial statistics
    total_revenue = FinancialTransaction.objects.filter(
        transaction_type='premium_payment'
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    # Monthly statistics
    monthly_stats = {
        'certificates_created': Certificate.objects.filter(issue_date__gte=start_of_month).count(),
        'verifications': CertificateVerification.objects.filter(verified_at__gte=start_of_month).count(),
        'transactions': FinancialTransaction.objects.filter(transaction_date__gte=start_of_month).count(),
    }
    
    # Recent activity
    recent_certificates = Certificate.objects.order_by('-issue_date')[:5]
    recent_verifications = CertificateVerification.objects.order_by('-verified_at')[:5]
    recent_transactions = FinancialTransaction.objects.order_by('-transaction_date')[:5]
    
    return {
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'valid_certificates': valid_certificates,
        'verified_certificates': verified_certificates,
        'total_verifications': total_verifications,
        'total_revenue': total_revenue,
        'monthly_stats': monthly_stats,
        'recent_certificates': recent_certificates,
        'recent_verifications': recent_verifications,
        'recent_transactions': recent_transactions,
    }

@admin.action(description="Export selected certificates to CSV")
def export_to_csv(modeladmin, request, queryset):
    """Export selected certificates to CSV"""
    import csv
    from django.http import HttpResponse
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="certificates_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Certificate ID', 'Policy Number', 'Client Name', 'Certificate Type',
        'Coverage Level', 'Status', 'Premium Amount', 'Start Date', 'End Date'
    ])
    
    for obj in queryset:
        writer.writerow([
            obj.certificate_id,
            obj.policy_number,
            obj.client_name,
            obj.get_certificate_type_display(),
            obj.get_coverage_level_display(),
            obj.get_status_display(),
            obj.premium_amount,
            obj.start_date,
            obj.end_date,
        ])
    
    return response

# Add export action to CertificateAdmin
CertificateAdmin.actions.append(export_to_csv)

# Enhanced Admin Dashboard View
def custom_admin_dashboard(request):
    from .models import Certificate, CertificateVerification, FinancialTransaction
    from django.db.models import Sum
    now = timezone.now().date()
    total_certificates = Certificate.objects.count()
    active_certificates = Certificate.objects.filter(status='active', end_date__gte=now).count()
    verified_certificates = Certificate.objects.filter(is_verified=True).count()
    total_revenue = FinancialTransaction.objects.filter(transaction_type='premium_payment').aggregate(total=Sum('amount'))['total'] or 0
    recent_certificates = Certificate.objects.order_by('-issue_date')[:5]
    recent_verifications = CertificateVerification.objects.order_by('-verified_at')[:5]
    recent_transactions = FinancialTransaction.objects.order_by('-transaction_date')[:5]
    context = {
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'verified_certificates': verified_certificates,
        'total_revenue': total_revenue,
        'recent_certificates': recent_certificates,
        'recent_verifications': recent_verifications,
        'recent_transactions': recent_transactions,
        'title': 'EverTrust Admin Dashboard',
    }
    return TemplateResponse(request, 'admin/custom_dashboard.html', context)

def admin_root_redirect(request):
    return redirect('admin:custom_admin_dashboard')

# Register the custom dashboard URL as the default admin root
original_get_urls = admin.site.get_urls

def get_urls():
    urls = original_get_urls()
    custom_urls = [
        path('', admin_root_redirect, name='index'),  # Redirect /admin/ to dashboard
        path('dashboard/', custom_admin_dashboard, name='custom_admin_dashboard'),
    ]
    return custom_urls + urls

admin.site.get_urls = get_urls
