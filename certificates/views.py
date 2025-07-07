from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.admin.views.decorators import staff_member_required
from django.template.loader import render_to_string
from django.utils import timezone
from django.db import transaction
from django.db.models import Count, Sum, Q
from datetime import timedelta
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from io import BytesIO
import json
import re
import os
from .models import Certificate, CertificateVerification, FinancialTransaction
from .utils import generate_certificate_pdf, generate_certificate_from_template
from .forms import CertificateForm, CertificateSearchForm, CertificateVerificationForm, PaymentForm, InstallmentForm, InvoiceForm
from .admin import get_admin_dashboard_context
import uuid
import qrcode
from django.contrib.auth import get_user_model
from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from weasyprint import HTML, CSS
from weasyprint.text.fonts import FontConfiguration
from django.urls import reverse
from django.conf import settings
import base64
import tempfile

# Only staff can access
staff_required = user_passes_test(lambda u: u.is_staff)

def index(request):
    """Home page view"""
    return render(request, 'certificates/index.html')

def verify_certificate(request):
    """Certificate verification view"""
    certificate = None
    verification = None
    error = None
    policy_number = ''
    
    if request.method == 'POST':
        form = CertificateVerificationForm(request.POST)
        if form.is_valid():
            policy_number = form.cleaned_data['policy_number']
            try:
                certificate = Certificate.objects.get(policy_number=policy_number)
                verification = CertificateVerification.objects.create(
                    certificate=certificate,
                    verification_code=str(uuid.uuid4()),
                    status='verified' if certificate.is_active else 'expired',
                    verified_at=timezone.now(),
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
            except Certificate.DoesNotExist:
                error = 'Certificate not found. Please check the policy number and try again.'
    else:
        form = CertificateVerificationForm()
    
    return render(request, 'certificates/verify.html', {
        'certificate': certificate,
        'verification': verification,
        'error': error,
        'policy_number': policy_number,
        'form': form
    })

def certificate_detail(request, policy_number):
    """Certificate detail view"""
    certificate = get_object_or_404(Certificate, policy_number=policy_number)
    
    # Get coverage summary to show the relationship between amounts
    coverage_summary = certificate.get_coverage_summary()
    
    return render(request, 'certificates/certificate_detail.html', {
        'certificate': certificate,
        'coverage_summary': coverage_summary,
        # All new fields are accessible via certificate object
    })

def printable_certificate(request, policy_number):
    """Printable certificate view"""
    certificate = get_object_or_404(Certificate, policy_number=policy_number)
    return render(request, 'certificates/printable_certificate.html', {
        'certificate': certificate,
        # All new fields are accessible via certificate object
    })

@staff_member_required
def certificate_pdf(request, policy_number):
    """Generate PDF for certificate"""
    certificate = get_object_or_404(Certificate, policy_number=policy_number)
    
    # Create the HttpResponse object with PDF headers
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{certificate.policy_number}.pdf"'
    
    # Try to use DOCX template if available
    template_path = 'EverTrust_Travel_Insurance_Template.docx'
    if os.path.exists(template_path):
        pdf_content = generate_certificate_from_template(certificate, template_path)
        if pdf_content:
            response.write(pdf_content)
            return response
    
    # Fallback to ReportLab PDF generation
    pdf_content = generate_certificate_pdf(certificate)
    response.write(pdf_content)
    return response

@staff_member_required
def certificate_html(request, policy_number):
    """Generate HTML version of certificate for PDF conversion"""
    certificate = get_object_or_404(Certificate, policy_number=policy_number)
    return render(request, 'certificates/certificate_template.html', {
        'certificate': certificate
    })

@staff_member_required
def create_certificate(request):
    """Create new certificate view"""
    if request.method == 'POST':
        form = CertificateForm(request.POST)
        if form.is_valid():
            certificate = form.save()
            messages.success(request, f'Certificate created successfully! Policy Number: {certificate.policy_number}')
            return redirect('certificates:certificate_detail', policy_number=certificate.policy_number)
    else:
        form = CertificateForm()
    
    return render(request, 'certificates/create_certificate.html', {
        'form': form,
        'title': 'Create New Certificate'
    })

@staff_member_required
def edit_certificate(request, policy_number):
    """Edit certificate view"""
    certificate = get_object_or_404(Certificate, policy_number=policy_number)
    
    if request.method == 'POST':
        form = CertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            certificate = form.save()
            messages.success(request, f'Certificate updated successfully! Policy Number: {certificate.policy_number}')
            return redirect('certificates:certificate_detail', policy_number=certificate.policy_number)
    else:
        form = CertificateForm(instance=certificate)
    
    return render(request, 'certificates/create_certificate.html', {
        'form': form,
        'certificate': certificate,
        'title': 'Edit Certificate'
    })

@staff_member_required
def certificate_list(request):
    """List all certificates with search and filtering"""
    certificates = Certificate.objects.all().order_by('-issue_date')
    
    if request.method == 'GET':
        form = CertificateSearchForm(request.GET)
        if form.is_valid():
            search = form.cleaned_data.get('search')
            certificate_type = form.cleaned_data.get('certificate_type')
            status = form.cleaned_data.get('status')
            payment_status = form.cleaned_data.get('payment_status')
            date_from = form.cleaned_data.get('date_from')
            date_to = form.cleaned_data.get('date_to')
            
            if search:
                certificates = certificates.filter(
                    Q(policy_number__icontains=search) |
                    Q(client_name__icontains=search) |
                    Q(client_email__icontains=search)
                )
            
            if certificate_type:
                certificates = certificates.filter(certificate_type=certificate_type)
            
            if status:
                certificates = certificates.filter(status=status)
            
            if payment_status:
                certificates = certificates.filter(payment_status=payment_status)
            
            if date_from:
                certificates = certificates.filter(issue_date__gte=date_from)
            
            if date_to:
                certificates = certificates.filter(issue_date__lte=date_to)
    else:
        form = CertificateSearchForm()
    
    # Pagination
    paginator = Paginator(certificates, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'certificates/certificate_list.html', {
        'page_obj': page_obj,
        'form': form,
        'total_certificates': certificates.count()
    })

@login_required
def dashboard(request):
    """Admin dashboard view"""
    if not request.user.is_staff:
        return redirect('admin:login')
    
    # Get dashboard context
    context = get_admin_dashboard_context()
    
    return render(request, 'certificates/dashboard.html', context)

def api_verify_certificate(request):
    """API endpoint for certificate verification"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            policy_number = data.get('policy_number', '').strip().upper()
            
            try:
                certificate = Certificate.objects.get(policy_number=policy_number)
                
                # Create verification record
                verification = CertificateVerification.objects.create(
                    certificate=certificate,
                    verification_code=str(uuid.uuid4()),
                    status='verified' if certificate.is_active else 'expired',
                    verified_at=timezone.now(),
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': True,
                    'valid': certificate.is_active,
                    'certificate': {
                        'policy_number': certificate.policy_number,
                        'client_name': certificate.client_name,
                        'certificate_type': certificate.get_certificate_type_display(),
                        'status': certificate.get_status_display(),
                        'start_date': certificate.start_date.strftime('%Y-%m-%d'),
                        'end_date': certificate.end_date.strftime('%Y-%m-%d'),
                        'premium_amount': str(certificate.premium_amount),
                    }
                })
                
            except Certificate.DoesNotExist:
                # Create verification record for failed attempt
                CertificateVerification.objects.create(
                    verification_code=policy_number,
                    status='rejected',
                    ip_address=request.META.get('REMOTE_ADDR', ''),
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
                
                return JsonResponse({
                    'success': False,
                    'error': 'Certificate not found'
                })
                
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            })
    
    return JsonResponse({
        'success': False,
        'error': 'Method not allowed'
    })

@staff_member_required
def admin_dashboard(request):
    """Main admin dashboard - replaces Django admin"""
    if not request.user.is_staff:
        messages.error(request, 'Access denied. Staff privileges required.')
        return redirect('certificates:admin_login')
    
    # Get statistics for admin dashboard
    from .models import Certificate, FinancialTransaction
    User = get_user_model()
    
    # Certificate statistics
    total_certificates = Certificate.objects.count()
    active_certificates = Certificate.objects.filter(status='active').count()
    pending_certificates = Certificate.objects.filter(status='pending').count()
    
    # User statistics
    total_users = User.objects.count()
    active_users = User.objects.filter(is_active=True).count()
    staff_users = User.objects.filter(is_staff=True).count()
    
    # Financial statistics
    total_premium = FinancialTransaction.objects.filter(transaction_type='premium').aggregate(
        total=Sum('amount')
    )['total'] or 0
    total_claims = FinancialTransaction.objects.filter(transaction_type='claim').aggregate(
        total=Sum('amount')
    )['total'] or 0
    net_revenue = total_premium - total_claims
    
    # Recent activities
    recent_certificates = Certificate.objects.all().order_by('-issue_date')[:5]
    recent_users = User.objects.all().order_by('-date_joined')[:5]
    recent_transactions = FinancialTransaction.objects.all().order_by('-transaction_date')[:5]
    
    context = {
        'total_certificates': total_certificates,
        'active_certificates': active_certificates,
        'pending_certificates': pending_certificates,
        'total_users': total_users,
        'active_users': active_users,
        'staff_users': staff_users,
        'total_premium': total_premium,
        'total_claims': total_claims,
        'net_revenue': net_revenue,
        'recent_certificates': recent_certificates,
        'recent_users': recent_users,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'admin/dashboard.html', context)

def get_recent_actions():
    """Get recent system actions"""
    recent_certificates = Certificate.objects.order_by('-issue_date')[:5]
    recent_verifications = CertificateVerification.objects.order_by('-verified_at')[:5]
    recent_transactions = FinancialTransaction.objects.order_by('-transaction_date')[:5]
    
    actions = []
    
    for cert in recent_certificates:
        actions.append({
            'type': 'certificate_created',
            'timestamp': cert.issue_date,
            'content': f'Certificate {cert.certificate_id} was created for {cert.client_name}',
            'url': f'/admin/certificates/certificate/{cert.certificate_id}/change/'
        })
    
    for verif in recent_verifications:
        if verif.verified_at:
            actions.append({
                'type': 'verification',
                'timestamp': verif.verified_at,
                'content': f'Certificate {verif.verification_code} was verified',
                'url': f'/admin/certificates/certificateverification/{verif.id}/change/'
            })
    
    for trans in recent_transactions:
        actions.append({
            'type': 'transaction',
            'timestamp': trans.transaction_date,
            'content': f'Transaction {trans.transaction_number} processed for {trans.amount}',
            'url': f'/admin/certificates/financialtransaction/{trans.id}/change/'
        })
    
    # Sort by timestamp
    actions.sort(key=lambda x: x['timestamp'], reverse=True)
    return actions[:10]

def get_system_stats():
    """Get system statistics"""
    now = timezone.now()
    thirty_days_ago = now - timedelta(days=30)
    
    stats = {
        'total_certificates': Certificate.objects.count(),
        'active_certificates': Certificate.objects.filter(status='active').count(),
        'expired_certificates': Certificate.objects.filter(status='expired').count(),
        'pending_payments': Certificate.objects.filter(payment_status='pending').count(),
        'overdue_payments': Certificate.objects.filter(payment_status='overdue').count(),
        'total_verifications': CertificateVerification.objects.count(),
        'recent_verifications': CertificateVerification.objects.filter(
            verified_at__gte=thirty_days_ago
        ).count(),
        'total_transactions': FinancialTransaction.objects.count(),
        'recent_transactions': FinancialTransaction.objects.filter(
            transaction_date__gte=thirty_days_ago
        ).count(),
        'total_revenue': FinancialTransaction.objects.filter(
            status='completed'
        ).aggregate(total=Sum('amount'))['total'] or 0,
        'monthly_revenue': FinancialTransaction.objects.filter(
            status='completed',
            transaction_date__gte=thirty_days_ago
        ).aggregate(total=Sum('amount'))['total'] or 0,
    }
    
    return stats

@staff_member_required
def export_data(request):
    """Export data to CSV or JSON"""
    model_type = request.GET.get('model', 'certificate')
    format_type = request.GET.get('format', 'csv')
    
    if model_type == 'certificate':
        queryset = Certificate.objects.all()
        filename = 'certificates'
    elif model_type == 'verification':
        queryset = CertificateVerification.objects.all()
        filename = 'verifications'
    elif model_type == 'transaction':
        queryset = FinancialTransaction.objects.all()
        filename = 'transactions'
    else:
        return HttpResponse('Invalid model type', status=400)
    
    if format_type == 'csv':
        return export_to_csv(queryset, filename, model_type)
    elif format_type == 'json':
        return export_to_json(queryset, filename, model_type)
    else:
        return HttpResponse('Invalid format type', status=400)

def export_to_csv(queryset, filename, model_type):
    """Export queryset to CSV"""
    import csv
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{filename}.csv"'
    
    writer = csv.writer(response)
    
    if model_type == 'certificate':
        writer.writerow([
            'Policy Number', 'Client Name', 'Certificate Type',
            'Coverage Level', 'Status', 'Premium Amount', 'Start Date', 'End Date'
        ])
        for obj in queryset:
            writer.writerow([
                obj.policy_number,
                obj.client_name,
                obj.get_certificate_type_display(),
                obj.get_coverage_level_display(),
                obj.get_status_display(),
                obj.premium_amount,
                obj.start_date,
                obj.end_date,
            ])
    elif model_type == 'verification':
        writer.writerow([
            'Verification Code', 'Certificate', 'Status', 'Verified At', 'IP Address'
        ])
        for obj in queryset:
            writer.writerow([
                obj.verification_code,
                obj.certificate.policy_number if obj.certificate else 'N/A',
                obj.get_status_display(),
                obj.verified_at,
                obj.ip_address,
            ])
    elif model_type == 'transaction':
        writer.writerow([
            'Transaction Number', 'Certificate', 'Type', 'Amount', 'Status', 'Date'
        ])
        for obj in queryset:
            writer.writerow([
                obj.transaction_number,
                obj.certificate.policy_number,
                obj.get_transaction_type_display(),
                obj.amount,
                obj.get_status_display(),
                obj.transaction_date,
            ])
    
    return response

def export_to_json(queryset, filename, model_type):
    """Export queryset to JSON"""
    import json
    
    data = []
    
    if model_type == 'certificate':
        for obj in queryset:
            data.append({
                'policy_number': obj.policy_number,
                'client_name': obj.client_name,
                'certificate_type': obj.get_certificate_type_display(),
                'coverage_level': obj.get_coverage_level_display(),
                'status': obj.get_status_display(),
                'premium_amount': str(obj.premium_amount),
                'start_date': obj.start_date.strftime('%Y-%m-%d'),
                'end_date': obj.end_date.strftime('%Y-%m-%d'),
            })
    elif model_type == 'verification':
        for obj in queryset:
            data.append({
                'verification_code': obj.verification_code,
                'certificate': obj.certificate.policy_number if obj.certificate else None,
                'status': obj.get_status_display(),
                'verified_at': obj.verified_at.strftime('%Y-%m-%d %H:%M:%S') if obj.verified_at else None,
                'ip_address': obj.ip_address,
            })
    elif model_type == 'transaction':
        for obj in queryset:
            data.append({
                'transaction_number': obj.transaction_number,
                'certificate': obj.certificate.policy_number,
                'transaction_type': obj.get_transaction_type_display(),
                'amount': str(obj.amount),
                'status': obj.get_status_display(),
                'transaction_date': obj.transaction_date.strftime('%Y-%m-%d %H:%M:%S'),
            })
    
    response = HttpResponse(json.dumps(data, indent=2), content_type='application/json')
    response['Content-Disposition'] = f'attachment; filename="{filename}.json"'
    return response

@login_required
def financial_dashboard(request):
    """Financial dashboard view"""
    if not request.user.is_staff:
        return redirect('admin:login')
    
    # Get financial data
    transactions = FinancialTransaction.objects.all().order_by('-created_at')[:50]
    total_premium = FinancialTransaction.objects.filter(transaction_type='premium').aggregate(
        total=Sum('amount')
    )['total'] or 0
    total_claims = FinancialTransaction.objects.filter(transaction_type='claim').aggregate(
        total=Sum('amount')
    )['total'] or 0
    
    context = {
        'transactions': transactions,
        'total_premium': total_premium,
        'total_claims': total_claims,
        'net_revenue': total_premium - total_claims,
    }
    
    return render(request, 'certificates/financial_dashboard.html', context)

def certificate_qr(request, policy_number):
    """Generate and serve a QR code image for the certificate verification URL."""
    from django.urls import reverse
    from django.conf import settings
    # Build the absolute verification URL
    verify_url = request.build_absolute_uri(reverse('certificates:certificate_detail', args=[policy_number]))
    # Generate QR code
    qr = qrcode.QRCode(box_size=8, border=2)
    qr.add_data(verify_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return FileResponse(buffer, content_type='image/png')

@staff_required
def manage_certificates(request):
    certificates = Certificate.objects.all().order_by('-issue_date')
    query = request.GET.get('q')
    if query:
        certificates = certificates.filter(
            client_name__icontains=query
        )
    return render(request, 'certificates/manage_certificates.html', {
        'certificates': certificates,
        'query': query or '',
    })

@staff_required
def certificate_form(request, pk=None):
    if pk:
        certificate = get_object_or_404(Certificate, pk=pk)
    else:
        certificate = None
    if request.method == 'POST':
        form = CertificateForm(request.POST, instance=certificate)
        if form.is_valid():
            form.save()
            return redirect('certificates:manage_certificates')
    else:
        form = CertificateForm(instance=certificate)
    return render(request, 'certificates/certificate_form.html', {
        'form': form,
        'certificate': certificate,
    })

@staff_required
def dashboard_home(request):
    from .models import Certificate, FinancialTransaction
    User = get_user_model()
    cert_count = Certificate.objects.count()
    user_count = User.objects.filter(is_active=True).count()
    total_premium = FinancialTransaction.objects.filter(transaction_type='premium').aggregate(total=Sum('amount'))['total'] or 0
    total_claims = FinancialTransaction.objects.filter(transaction_type='claim').aggregate(total=Sum('amount'))['total'] or 0
    net_revenue = total_premium - total_claims
    return render(request, 'dashboard/dashboard_home.html', {
        'cert_count': cert_count,
        'user_count': user_count,
        'total_premium': total_premium,
        'total_claims': total_claims,
        'net_revenue': net_revenue,
    })

@staff_required
def dashboard_users(request):
    """User management dashboard view"""
    User = get_user_model()
    users = User.objects.all().order_by('-date_joined')
    query = request.GET.get('q')
    if query:
        users = users.filter(
            Q(username__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query) |
            Q(email__icontains=query)
        )
    return render(request, 'dashboard/users.html', {
        'users': users,
        'query': query or '',
    })

@staff_required
def dashboard_user_create(request):
    """Create new user"""
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = request.POST.get('is_staff') == 'on'
            user.is_superuser = request.POST.get('is_superuser') == 'on'
            user.save()
            messages.success(request, f'User {user.username} created successfully.')
            return redirect('certificates:dashboard_users')
    else:
        form = UserCreationForm()
    return render(request, 'dashboard/user_form.html', {
        'form': form,
        'action': 'Create',
    })

@staff_required
def dashboard_user_edit(request, user_id):
    """Edit existing user"""
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f'User {user.username} updated successfully.')
            return redirect('certificates:dashboard_users')
    else:
        form = UserChangeForm(instance=user)
    return render(request, 'dashboard/user_form.html', {
        'form': form,
        'user': user,
        'action': 'Edit',
    })

@staff_required
def dashboard_user_toggle_status(request, user_id):
    """Toggle user active status"""
    User = get_user_model()
    user = get_object_or_404(User, id=user_id)
    user.is_active = not user.is_active
    user.save()
    status = 'activated' if user.is_active else 'deactivated'
    messages.success(request, f'User {user.username} {status} successfully.')
    return redirect('certificates:dashboard_users')

@staff_required
def dashboard_financials(request):
    """Financial analysis dashboard view"""
    from datetime import datetime, timedelta
    from django.db.models import Sum, Count, Avg
    
    # Get date range from request or default to last 30 days
    days = int(request.GET.get('days', 30))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    # Financial statistics
    total_premium = FinancialTransaction.objects.filter(
        transaction_type='premium',
        transaction_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_claims = FinancialTransaction.objects.filter(
        transaction_type='claim',
        transaction_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    total_commission = FinancialTransaction.objects.filter(
        transaction_type='commission',
        transaction_date__range=[start_date, end_date]
    ).aggregate(total=Sum('amount'))['total'] or 0
    
    net_revenue = total_premium - total_claims - total_commission
    
    # Transaction counts
    premium_count = FinancialTransaction.objects.filter(
        transaction_type='premium',
        transaction_date__range=[start_date, end_date]
    ).count()
    
    claims_count = FinancialTransaction.objects.filter(
        transaction_type='claim',
        transaction_date__range=[start_date, end_date]
    ).count()
    
    # Recent transactions
    recent_transactions = FinancialTransaction.objects.filter(
        transaction_date__range=[start_date, end_date]
    ).order_by('-transaction_date')[:20]
    
    # Monthly breakdown for charts
    monthly_data = FinancialTransaction.objects.filter(
        transaction_date__range=[start_date, end_date]
    ).extra(
        select={'month': "strftime('%%Y-%%m', transaction_date)"}
    ).values('month', 'transaction_type').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('month')
    
    context = {
        'total_premium': total_premium,
        'total_claims': total_claims,
        'total_commission': total_commission,
        'net_revenue': net_revenue,
        'premium_count': premium_count,
        'claims_count': claims_count,
        'recent_transactions': recent_transactions,
        'monthly_data': monthly_data,
        'start_date': start_date,
        'end_date': end_date,
        'days': days,
    }
    
    return render(request, 'dashboard/financials.html', context)

@staff_required
def dashboard_financial_export(request):
    """Export financial data"""
    format_type = request.GET.get('format', 'csv')
    days = int(request.GET.get('days', 30))
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    transactions = FinancialTransaction.objects.filter(
        transaction_date__range=[start_date, end_date]
    ).order_by('-transaction_date')
    
    if format_type == 'csv':
        return export_to_csv(transactions, f'financial_report_{days}days', 'transaction')
    elif format_type == 'json':
        return export_to_json(transactions, f'financial_report_{days}days', 'transaction')
    else:
        return HttpResponse('Invalid format type', status=400)

# Custom Admin Views
def admin_login(request):
    """Custom admin login that replaces Django's default admin"""
    if request.user.is_authenticated and request.user.is_staff:
        return redirect('certificates:admin_dashboard')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None and user.is_staff:
                login(request, user)
                messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
                return redirect('certificates:admin_dashboard')
            else:
                messages.error(request, 'Invalid credentials or insufficient permissions.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'admin/login.html', {'form': form})

def admin_logout(request):
    """Custom admin logout"""
    logout(request)
    messages.success(request, 'You have been successfully logged out.')
    return redirect('certificates:admin_login')

def image_to_data_url(path):
    with open(path, 'rb') as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
        ext = path.split('.')[-1].lower()
        return f"data:image/{'png' if ext == 'png' else 'jpeg'};base64,{encoded}"

@staff_member_required
def certificate_pdf_professional(request, policy_number):
    """Generate a professional PDF certificate using WeasyPrint"""
    certificate = get_object_or_404(Certificate, policy_number=policy_number)
    
    # Build the absolute URL to the QR code view
    qr_code_url = request.build_absolute_uri(reverse('certificates:certificate_qr', args=[policy_number]))

    # Convert static images to data URLs
    logo_path = os.path.join(settings.STATIC_ROOT, 'images/Evertrust-logo.png')
    seal_path = os.path.join(settings.STATIC_ROOT, 'images/seal evertrust.png')
    signature_path = os.path.join(settings.STATIC_ROOT, 'images/signature.png')

    context = {
        'certificate': certificate,
        'qr_code_path': qr_code_url,
        'logo_data_url': image_to_data_url(logo_path),
        'seal_data_url': image_to_data_url(seal_path),
        'signature_data_url': image_to_data_url(signature_path),
        'current_date': timezone.now().strftime('%B %d, %Y'),
    }
    
    # Render HTML template for PDF
    html_string = render_to_string('certificates/certificate_pdf_template.html', context)
    
    # Create PDF with custom CSS
    font_config = FontConfiguration()
    css_string = '''
        @page {
            size: A4;
            margin: 1cm;
            @top-center {
                content: "EverTrust Insurance Certificate";
                font-size: 10pt;
                color: #2563eb;
            }
            @bottom-center {
                content: "Page " counter(page) " of " counter(pages);
                font-size: 10pt;
                color: #64748b;
            }
        }
        
        body {
            font-family: 'Times New Roman', serif;
            line-height: 1.6;
            color: #1e293b;
            background: white;
        }
        
        .certificate-container {
            max-width: 800px;
            margin: 0 auto;
            padding: 2cm;
            border: 3px solid #2563eb;
            border-radius: 15px;
            background: linear-gradient(135deg, #f8fafc 0%, #ffffff 100%);
            position: relative;
        }
        
        .certificate-container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse"><circle cx="10" cy="10" r="1" fill="%232563eb" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23dots)"/></svg>');
            border-radius: 15px;
            z-index: -1;
        }
        
        .header {
            text-align: center;
            margin-bottom: 2cm;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 1cm;
        }
        
        .logo {
            width: 120px;
            height: auto;
            margin-bottom: 1cm;
        }
        
        .company-name {
            font-size: 28pt;
            font-weight: bold;
            color: #2563eb;
            margin-bottom: 0.5cm;
            text-transform: uppercase;
            letter-spacing: 2px;
        }
        
        .certificate-title {
            font-size: 24pt;
            font-weight: bold;
            color: #1e293b;
            margin-bottom: 0.5cm;
            text-transform: uppercase;
        }
        
        .certificate-subtitle {
            font-size: 14pt;
            color: #64748b;
            margin-bottom: 1cm;
        }
        
        .certificate-number {
            font-size: 12pt;
            color: #64748b;
            margin-bottom: 1cm;
        }
        
        .main-content {
            margin: 2cm 0;
        }
        
        .policy-info {
            background: #f1f5f9;
            padding: 1cm;
            border-radius: 10px;
            margin-bottom: 1.5cm;
            border-left: 5px solid #2563eb;
        }
        
        .info-row {
            display: flex;
            justify-content: space-between;
            margin-bottom: 0.5cm;
            align-items: center;
        }
        
        .info-label {
            font-weight: bold;
            color: #374151;
            min-width: 150px;
        }
        
        .info-value {
            color: #1e293b;
            text-align: right;
        }
        
        .coverage-details {
            background: #fef3c7;
            padding: 1cm;
            border-radius: 10px;
            margin-bottom: 1.5cm;
            border-left: 5px solid #f59e0b;
        }
        
        .coverage-title {
            font-size: 16pt;
            font-weight: bold;
            color: #92400e;
            margin-bottom: 0.5cm;
        }
        
        .coverage-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 0.5cm;
        }
        
        .coverage-item {
            display: flex;
            justify-content: space-between;
            padding: 0.3cm 0;
            border-bottom: 1px solid #fde68a;
        }
        
        .coverage-label {
            font-weight: bold;
            color: #92400e;
        }
        
        .coverage-amount {
            color: #1e293b;
            font-weight: bold;
        }
        
        .terms-section {
            background: #f0f9ff;
            padding: 1cm;
            border-radius: 10px;
            margin-bottom: 1.5cm;
            border-left: 5px solid #0ea5e9;
        }
        
        .terms-title {
            font-size: 16pt;
            font-weight: bold;
            color: #0c4a6e;
            margin-bottom: 0.5cm;
        }
        
        .terms-list {
            list-style: none;
            padding: 0;
        }
        
        .terms-list li {
            margin-bottom: 0.3cm;
            padding-left: 1cm;
            position: relative;
        }
        
        .terms-list li::before {
            content: '•';
            color: #0ea5e9;
            font-weight: bold;
            position: absolute;
            left: 0;
        }
        
        .footer {
            margin-top: 2cm;
            text-align: center;
            border-top: 2px solid #2563eb;
            padding-top: 1cm;
        }
        
        .qr-section {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-top: 1cm;
        }
        
        .qr-code {
            width: 100px;
            height: 100px;
        }
        
        .verification-info {
            text-align: right;
            font-size: 10pt;
            color: #64748b;
        }
        
        .signature-section {
            display: flex;
            justify-content: space-between;
            margin-top: 2cm;
        }
        
        .signature-box {
            text-align: center;
            flex: 1;
            margin: 0 1cm;
        }
        
        .signature-line {
            border-top: 2px solid #2563eb;
            margin-top: 1cm;
            padding-top: 0.5cm;
        }
        
        .signature-name {
            font-weight: bold;
            color: #2563eb;
        }
        
        .signature-title {
            font-size: 10pt;
            color: #64748b;
        }
        
        .watermark {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%) rotate(-45deg);
            font-size: 48pt;
            color: rgba(37, 99, 235, 0.1);
            font-weight: bold;
            z-index: -1;
        }
        
        .security-features {
            position: absolute;
            top: 1cm;
            right: 1cm;
            font-size: 8pt;
            color: #64748b;
        }
        
        .certificate-seal {
            position: absolute;
            bottom: 1cm;
            right: 1cm;
            width: 80px;
            height: 80px;
            border: 2px solid #2563eb;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
            color: white;
            font-weight: bold;
            font-size: 8pt;
            text-align: center;
        }
    '''
    
    # Render HTML template for PDF
    html = HTML(string=html_string)
    css = CSS(string=css_string, font_config=font_config)
    
    # Create PDF
    pdf = html.write_pdf(stylesheets=[css], font_config=font_config)
    
    # Return PDF response
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="certificate_{policy_number}.pdf"'
    return response


