# EverTrust Insurance Management System

A comprehensive Django-based insurance certificate management and verification system with professional PDF generation capabilities.

## 🚀 Features

### Admin Panel
- **Secure Admin Login**: Protected admin interface for certificate management
- **Certificate Creation**: Complete certificate management with all required fields
- **Financial Tracking**: Comprehensive financial transaction management
- **PDF Generation**: Automatic professional PDF certificate generation
- **Dashboard**: Real-time statistics and monitoring
- **Verification Logs**: Track all certificate verification attempts

### User Panel
- **Certificate Verification**: Public verification system
- **Real-time Validation**: Instant certificate status checking
- **Professional Display**: Beautiful certificate detail pages
- **Mobile Responsive**: Works perfectly on all devices

### Technical Features
- **Django 5.2.3**: Latest Django framework
- **SQLite Database**: Lightweight and portable
- **ReportLab PDF**: Professional PDF generation
- **Bootstrap 5**: Modern responsive UI
- **Font Awesome**: Beautiful icons
- **Custom CSS/JS**: Enhanced user experience

## 📋 Requirements

- Python 3.8+
- Django 5.2.3
- ReportLab 4.4.2
- Pillow 11.2.1

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <repository-url>
cd Ever-Trust
```

### 2. Create Virtual Environment
```bash
python -m venv venv
```

### 3. Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**macOS/Linux:**
```bash
source venv/bin/activate
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Run Database Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Admin User
```bash
python manage.py setup_admin
```

### 7. Run Development Server
```bash
python manage.py runserver
```

## 🔐 Default Admin Credentials

- **Username**: `admin`
- **Password**: `admin123`

**⚠️ Important**: Change the password after first login!

## 📁 Project Structure

```
Ever-Trust/
├── insurance_system/          # Django project settings
│   ├── models.py             # Database models
│   ├── views.py              # View functions
│   ├── admin.py              # Admin interface
│   ├── utils.py              # PDF generation utilities
│   └── urls.py               # URL routing
├── templates/                # HTML templates
│   ├── base.html             # Base template
│   └── certificates/         # Certificate templates
├── static/                   # Static files
│   ├── css/style.css         # Custom styles
│   └── js/main.js            # JavaScript functionality
├── manage.py                 # Django management script
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🎯 Usage Guide

### For Administrators

1. **Access Admin Panel**
   - Navigate to `http://localhost:8000/admin/`
   - Login with admin credentials

2. **Create Certificate**
   - Go to "Certificates" section
   - Click "Add Certificate"
   - Fill in all required fields:
     - Member Information
     - Insurance Details
     - Period of Insurance
     - Limit of Liability
     - Contribution Calculation
     - Bank Details

3. **Generate PDF**
   - After creating a certificate
   - Click "Download PDF" button
   - Professional certificate will be generated

4. **Monitor Dashboard**
   - View real-time statistics
   - Track verification attempts
   - Monitor certificate status

### For Users

1. **Verify Certificate**
   - Visit the home page
   - Enter certificate ID
   - Click "Verify Certificate"

2. **View Certificate Details**
   - Valid certificates show complete details
   - Invalid certificates show error messages

## 📊 Database Models

### Certificate Model
- Certificate ID (auto-generated)
- Member Information (name, address, phone, email)
- Insurance Details (location, activity, risk description)
- Insurance Period (start/end dates)
- Limit of Liability
- Contribution Calculation (net contribution, stamps, fees, total premium)
- Bank Details
- Status tracking (active, verified, valid)

### CertificateVerification Model
- Tracks all verification attempts
- IP address logging
- Success/failure status
- Timestamp recording

### FinancialTransaction Model
- Transaction type (premium payment, refund, etc.)
- Amount and currency
- Reference numbers
- Description and timestamps

## 🔧 Configuration

### Environment Variables
Create a `.env` file for production:

```env
SECRET_KEY=your-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-domain.com
DATABASE_URL=your-database-url
```

### Database Configuration
The system uses SQLite by default. For production, configure PostgreSQL:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'your_db_name',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🚀 Deployment

### Production Setup

1. **Set Environment Variables**
   ```bash
   export SECRET_KEY="your-secret-key"
   export DEBUG="False"
   export ALLOWED_HOSTS="your-domain.com"
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic
   ```

3. **Configure Web Server**
   - Use Gunicorn or uWSGI
   - Configure Nginx as reverse proxy
   - Set up SSL certificates

4. **Database Migration**
   ```bash
   python manage.py migrate
   ```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN python manage.py collectstatic --noinput
RUN python manage.py migrate

EXPOSE 8000
CMD ["gunicorn", "insurance_system.wsgi:application", "--bind", "0.0.0.0:8000"]
```

## 🔒 Security Features

- **CSRF Protection**: All forms protected against CSRF attacks
- **SQL Injection Prevention**: Django ORM prevents SQL injection
- **XSS Protection**: Template auto-escaping
- **Admin Authentication**: Secure admin login system
- **Input Validation**: Comprehensive form validation
- **IP Logging**: Track verification attempts

## 📱 API Endpoints

### Certificate Verification API
```
POST /api/verify/
Content-Type: application/json

{
    "certificate_id": "CERT12345"
}
```

**Response:**
```json
{
    "success": true,
    "certificate": {
        "id": "CERT12345",
        "member_name": "John Doe",
        "location": "New York",
        "activity": "Business Travel",
        "period_start": "2024-01-01",
        "period_end": "2024-12-31",
        "limit_of_liability": "100000.00",
        "total_premium": "1500.00"
    }
}
```

## 🐛 Troubleshooting

### Common Issues

1. **Migration Errors**
   ```bash
   python manage.py makemigrations --empty certificates
   python manage.py migrate
   ```

2. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic
   ```

3. **PDF Generation Issues**
   - Ensure ReportLab is installed
   - Check file permissions
   - Verify template syntax

4. **Database Issues**
   ```bash
   python manage.py dbshell
   ```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support and questions:
- Email: support@evertrust.com
- Phone: +1 (234) 567-8900
- Documentation: [Link to documentation]

## 🔄 Version History

- **v1.0.0** - Initial release with basic functionality
- **v1.1.0** - Added PDF generation and enhanced UI
- **v1.2.0** - Added dashboard and verification tracking

---

**EverTrust Insurance Management System** - Professional insurance certificate management made simple. 