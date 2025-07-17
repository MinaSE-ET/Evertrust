from django.urls import path, re_path
from . import views

app_name = 'certificates'

urlpatterns = [
    # Public URLs
    path('', views.index, name='index'),
    path('verify/', views.verify_certificate, name='verify'),
    path('certificates/', views.certificate_list, name='certificate_list'),
    path('certificate/create/', views.create_certificate, name='create_certificate'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/$', views.certificate_detail, name='certificate_detail'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/print/$', views.printable_certificate, name='printable_certificate'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/pdf/$', views.certificate_pdf, name='certificate_pdf'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/html/$', views.certificate_html, name='certificate_html'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/qr/$', views.certificate_qr, name='certificate_qr'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/edit/$', views.edit_certificate, name='edit_certificate'),
    
    # Payment Management URLs
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/payment/$', views.manage_payment, name='manage_payment'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/payments/$', views.payment_history, name='payment_history'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/mark-paid/$', views.mark_as_paid, name='mark_as_paid'),
    re_path(r'^certificate/(?P<policy_number>POL[0-9]{7})/mark-overdue/$', views.mark_as_overdue, name='mark_as_overdue'),
    
    # Claims Management URLs
    path('claims/', views.claim_list, name='claim_list'),
    path('claims/create/', views.claim_create, name='claim_create'),
    path('claims/<uuid:claim_id>/', views.claim_detail, name='claim_detail'),
    path('claims/<uuid:claim_id>/edit/', views.claim_edit, name='claim_edit'),
    
    # Commissions Management URLs
    path('commissions/', views.commission_list, name='commission_list'),
    path('commissions/create/', views.commission_create, name='commission_create'),
    path('commissions/<uuid:commission_id>/', views.commission_detail, name='commission_detail'),
    path('commissions/<uuid:commission_id>/edit/', views.commission_edit, name='commission_edit'),
    
    # Fees Management URLs
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/create/', views.fee_create, name='fee_create'),
    path('fees/<uuid:fee_id>/', views.fee_detail, name='fee_detail'),
    path('fees/<uuid:fee_id>/edit/', views.fee_edit, name='fee_edit'),
    
    # Financial Reports URLs
    path('reports/', views.financial_report_list, name='financial_report_list'),
    path('reports/create/', views.financial_report_create, name='financial_report_create'),
    path('reports/<uuid:report_id>/', views.financial_report_detail, name='financial_report_detail'),
    path('reports/<uuid:report_id>/generate/', views.financial_report_generate, name='financial_report_generate'),
    
    # API endpoints
    path('api/verify/', views.api_verify_certificate, name='api_verify'),
    
    # Admin URLs (require login)
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('export/', views.export_data, name='export_data'),
    path('financial-dashboard/', views.financial_dashboard, name='financial_dashboard'),

    path('manage/', views.manage_certificates, name='manage_certificates'),
    path('manage/new/', views.certificate_form, name='certificate_create'),
    path('manage/<str:pk>/edit/', views.certificate_form, name='certificate_edit'),
    path('dashboard/', views.dashboard_home, name='dashboard_home'),
    path('dashboard/users/', views.dashboard_users, name='dashboard_users'),
    path('dashboard/users/create/', views.dashboard_user_create, name='dashboard_user_create'),
    path('dashboard/users/<int:user_id>/edit/', views.dashboard_user_edit, name='dashboard_user_edit'),
    path('dashboard/users/<int:user_id>/toggle/', views.dashboard_user_toggle_status, name='dashboard_user_toggle_status'),
    path('dashboard/financials/', views.dashboard_financials, name='dashboard_financials'),
    path('dashboard/financials/export/', views.dashboard_financial_export, name='dashboard_financial_export'),
    path('admin/', views.admin_login, name='admin_login'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/logout/', views.admin_logout, name='admin_logout'),
    path('certificate/<str:policy_number>/pdf/', views.certificate_pdf, name='certificate_pdf'),
    path('certificate/<str:policy_number>/pdf-professional/', views.certificate_pdf_professional, name='certificate_pdf_professional'),

    # Financial Transaction URLs
    path('financial-transactions/', views.financial_transaction_list, name='financial_transaction_list'),
    path('financial-transactions/create/', views.financial_transaction_create, name='financial_transaction_create'),
    path('financial-transactions/<uuid:transaction_id>/', views.financial_transaction_detail, name='financial_transaction_detail'),
    path('financial-transactions/<uuid:transaction_id>/edit/', views.financial_transaction_edit, name='financial_transaction_edit'),
    path('financial-transactions/<uuid:transaction_id>/delete/', views.financial_transaction_delete, name='financial_transaction_delete'),

    # Financial Management URLs
    path('financials/', views.financial_dashboard, name='financial_dashboard'),
    path('financials/export/', views.dashboard_financial_export, name='dashboard_financial_export'),
    # Add QR verification by policy number in path
    path('verify/<str:policy_number>/', views.verify_qr, name='verify_qr'),
] 