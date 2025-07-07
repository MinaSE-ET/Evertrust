"""
URL configuration for insurance_system project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from certificates import views
from certificates.admin import admin_site

def redirect_to_custom_admin(request):
    """Redirect Django admin to our custom admin interface"""
    return redirect('certificates:admin_login')

urlpatterns = [
    path('admin/', redirect_to_custom_admin, name='django_admin_redirect'),  # Redirect to custom admin
    path('', views.index, name='index'),
    path('certificates/', include('certificates.urls')),
    path('verify/', views.verify_certificate, name='verify'),
    path('certificate/<uuid:certificate_id>/', views.certificate_detail, name='certificate_detail'),
    path('certificate/<uuid:certificate_id>/pdf/', views.certificate_pdf, name='generate_pdf'),
    path('certificate/<uuid:certificate_id>/html/', views.certificate_html, name='generate_html'),
    path('dashboard/', views.admin_dashboard, name='dashboard'),
    path('api/verify/<str:certificate_id>/', views.api_verify_certificate, name='api_verify'),
    path('export/', views.export_data, name='export_data'),
]

# Add custom admin dashboard
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
