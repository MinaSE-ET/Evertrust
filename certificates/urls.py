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
] 