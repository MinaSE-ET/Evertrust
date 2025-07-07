from django import forms
from django.contrib.auth.models import User
from .models import Certificate, Payment, Installment, Invoice, FinancialTransaction
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import datetime

class CertificateForm(forms.ModelForm):
    """Form for creating and editing certificates"""
    
    # Override some fields for better UX
    client_date_of_birth = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select the client's date of birth"
    )
    
    start_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select the start date of coverage"
    )
    
    end_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select the end date of coverage"
    )
    
    period_from = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select the period start date"
    )
    
    period_to = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        help_text="Select the period end date"
    )
    
    insured_amount = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Total amount covered by this certificate (maximum payout)"
    )
    
    premium_amount = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Amount the client pays for this certificate (what they owe)"
    )
    
    total_premium = forms.DecimalField(
        min_value=Decimal('0.01'),
        max_digits=15,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Total premium including all fees and charges (internal calculation)"
    )
    
    net_contribution = forms.DecimalField(
        min_value=Decimal('0.00'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Net contribution for claims"
    )
    
    proportional_stamp = forms.DecimalField(
        min_value=Decimal('0.00'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Proportional stamp for claims"
    )
    
    dimensional_stamp = forms.DecimalField(
        min_value=Decimal('0.00'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Dimensional stamp for claims"
    )
    
    supervision_fees = forms.DecimalField(
        min_value=Decimal('0.00'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Supervision fees for claims"
    )
    
    insurance_fees = forms.DecimalField(
        min_value=Decimal('0.00'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
        help_text="Insurance fees for claims"
    )
    
    total_premium_words = forms.CharField(
        max_length=100,
        help_text="Total premium in words"
    )
    
    class Meta:
        model = Certificate
        fields = [
            # Policy Information
            'policy_number', 'certificate_type', 'status', 'payment_status',
            
            # Client Information
            'client_name', 'client_id_number', 'client_date_of_birth', 'client_phone', 'client_email', 'client_address', 'client_bank_name', 'client_bank_account',
            
            # Insurance Details
            'coverage_level', 'insured_amount', 'premium_amount', 'total_premium', 'net_contribution', 'proportional_stamp', 'dimensional_stamp', 'supervision_fees', 'insurance_fees', 'total_premium_words',
            
            # Insurance Period
            'period_from', 'period_to', 'start_date', 'end_date',
            
            # Activity and Location Information
            'location', 'activity', 'description_of_risk',
            
            # Agent Information
            'agent_name', 'agent_id',
            
            # Verification
            'is_verified', 'verification_date',
            
            # Additional Information
            'description', 'terms_conditions', 'special_conditions',
        ]
        widgets = {
            'period_from': forms.DateInput(attrs={'type': 'date'}),
            'period_to': forms.DateInput(attrs={'type': 'date'}),
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'client_date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'verification_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        coverage = self.initial.get('coverage_level', self.data.get('coverage_level', 'comprehensive'))
        
        # Set sensible date defaults
        today = datetime.date.today()
        if 'period_from' in self.fields:
            self.fields['period_from'].initial = today
        if 'period_to' in self.fields:
            self.fields['period_to'].initial = today.replace(year=today.year + 1)
        if 'start_date' in self.fields:
            self.fields['start_date'].initial = today
        if 'end_date' in self.fields:
            self.fields['end_date'].initial = today.replace(year=today.year + 1)
            
        # Set defaults for all levels
        defaults = {
            'comprehensive': {
                'insured_amount': 10000000,  # 10M coverage
                'net_contribution': 10000,
                'proportional_stamp': 500,
                'dimensional_stamp': 2,
                'supervision_fees': 89.97,
                'insurance_fees': 58.03,
                'total_premium': 10650,
                'premium_amount': 10650,  # Same as total premium
                'total_premium_words': "Ten Thousand Six Hundred Fifty US Dollars",
            },
            'basic': {
                'insured_amount': 2000000,  # 2M coverage
                'net_contribution': 5000,
                'proportional_stamp': 0,
                'dimensional_stamp': 0,
                'supervision_fees': 0,
                'insurance_fees': 0,
                'total_premium': 5000,
                'premium_amount': 5000,  # Same as total premium
                'total_premium_words': "Five Thousand US Dollars",
            },
            'standard': {
                'insured_amount': 5000000,  # 5M coverage
                'net_contribution': 7000,
                'proportional_stamp': 250,
                'dimensional_stamp': 1,
                'supervision_fees': 45,
                'insurance_fees': 30,
                'total_premium': 7326,
                'premium_amount': 7326,  # Same as total premium
                'total_premium_words': "Seven Thousand Three Hundred Twenty-Six US Dollars",
            },
            'premium': {
                'insured_amount': 8000000,  # 8M coverage
                'net_contribution': 8500,
                'proportional_stamp': 350,
                'dimensional_stamp': 1.5,
                'supervision_fees': 60,
                'insurance_fees': 40,
                'total_premium': 8951.5,
                'premium_amount': 8951.5,  # Same as total premium
                'total_premium_words': "Eight Thousand Nine Hundred Fifty-One and 50/100 US Dollars",
            },
            'elite': {
                'insured_amount': 20000000,  # 20M coverage
                'net_contribution': 20000,
                'proportional_stamp': 1000,
                'dimensional_stamp': 5,
                'supervision_fees': 150,
                'insurance_fees': 100,
                'total_premium': 21255,
                'premium_amount': 21255,  # Same as total premium
                'total_premium_words': "Twenty-One Thousand Two Hundred Fifty-Five US Dollars",
            },
        }
        if coverage in defaults:
            for field, value in defaults[coverage].items():
                if field in self.fields:
                    self.fields[field].initial = value
    
    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        period_from = cleaned_data.get('period_from')
        period_to = cleaned_data.get('period_to')
        
        if start_date and end_date:
            if start_date >= end_date:
                raise forms.ValidationError("End date must be after start date.")
            
            if start_date < datetime.date.today():
                raise forms.ValidationError("Start date cannot be in the past.")
        
        if period_from and period_to:
            if period_from >= period_to:
                raise forms.ValidationError("Period end date must be after period start date.")
        
        return cleaned_data
    
    def clean_client_date_of_birth(self):
        """Validate client date of birth"""
        dob = self.cleaned_data.get('client_date_of_birth')
        if dob and dob > datetime.date.today():
            raise forms.ValidationError("Date of birth cannot be in the future.")
        return dob
    
    def clean_insured_amount(self):
        """Validate insured amount"""
        amount = self.cleaned_data.get('insured_amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Insured amount must be greater than zero.")
        return amount
    
    def clean_premium_amount(self):
        """Validate premium amount"""
        amount = self.cleaned_data.get('premium_amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Premium amount must be greater than zero.")
        return amount

    def clean_total_premium(self):
        """Validate total premium amount"""
        amount = self.cleaned_data.get('total_premium')
        if amount and amount <= 0:
            raise forms.ValidationError("Total premium must be greater than zero.")
        return amount

class CertificateSearchForm(forms.Form):
    """Form for searching certificates"""
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by policy number, client name, or email...'
        })
    )
    
    certificate_type = forms.ChoiceField(
        choices=[('', 'All Types')] + Certificate.CERTIFICATE_TYPES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    status = forms.ChoiceField(
        choices=[('', 'All Statuses')] + Certificate.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    payment_status = forms.ChoiceField(
        choices=[('', 'All Payment Statuses')] + [
            ('paid', 'Paid'),
            ('pending', 'Pending'),
            ('overdue', 'Overdue'),
            ('installment', 'Installment'),
            ('cancelled', 'Cancelled'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

class CertificateVerificationForm(forms.Form):
    """Form for certificate verification"""
    policy_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter Policy Number (e.g., POL1234567)',
            'autocomplete': 'off'
        }),
        help_text="Enter the policy number to verify the certificate"
    )
    
    def clean_policy_number(self):
        policy_number = self.cleaned_data.get('policy_number')
        if policy_number:
            policy_number = policy_number.strip().upper()
        return policy_number

class PaymentForm(forms.ModelForm):
    """Form for payment creation"""
    
    payment_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        initial=datetime.datetime.now()
    )
    
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today()
    )
    
    class Meta:
        model = Payment
        fields = [
            'amount',
            'payment_method',
            'status',
            'due_date',
            'transaction_id',
            'reference_number',
            'description',
            'notes',
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'payment_method': forms.Select(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'transaction_id': forms.TextInput(attrs={'class': 'form-control'}),
            'reference_number': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Payment amount must be greater than zero.")
        return amount

class InstallmentForm(forms.ModelForm):
    """Form for installment creation"""
    
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today()
    )
    
    class Meta:
        model = Installment
        fields = [
            'installment_number',
            'amount',
            'due_date',
            'status',
            'description',
            'notes',
        ]
        widgets = {
            'installment_number': forms.TextInput(attrs={'class': 'form-control'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Installment amount must be greater than zero.")
        return amount

class InvoiceForm(forms.ModelForm):
    """Form for invoice creation"""
    
    due_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date'}),
        initial=datetime.date.today()
    )
    
    class Meta:
        model = Invoice
        fields = [
            'amount',
            'tax_amount',
            'total_amount',
            'due_date',
            'status',
            'description',
            'terms_conditions',
            'notes',
            'billing_address',
            'billing_email',
        ]
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'tax_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'total_amount': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'terms_conditions': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'billing_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'billing_email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    
    def clean_amount(self):
        amount = self.cleaned_data.get('amount')
        if amount and amount <= 0:
            raise forms.ValidationError("Invoice amount must be greater than zero.")
        return amount 