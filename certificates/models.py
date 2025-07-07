from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import uuid
from decimal import Decimal
import random
import string

def generate_policy_number():
    prefix = 'POL'
    digits = ''.join(random.choices(string.digits, k=7))
    return f'{prefix}{digits}'

class Certificate(models.Model):
    CERTIFICATE_TYPES = [
        ('life', 'Life Insurance'),
        ('health', 'Health Insurance'),
        ('auto', 'Auto Insurance'),
        ('property', 'Property Insurance'),
        ('business', 'Business Insurance'),
        ('travel', 'Travel Insurance'),
        ('marine', 'Marine Insurance'),
        ('liability', 'Liability Insurance'),
        ('disability', 'Disability Insurance'),
        ('pet', 'Pet Insurance'),
    ]
    
    COVERAGE_LEVELS = [
        ('basic', 'Basic Coverage'),
        ('standard', 'Standard Coverage'),
        ('premium', 'Premium Coverage'),
        ('comprehensive', 'Comprehensive Coverage'),
        ('elite', 'Elite Coverage'),
    ]
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('suspended', 'Suspended'),
        ('pending', 'Pending'),
        ('renewed', 'Renewed'),
    ]
    
    # Primary identifier - Policy Number
    policy_number = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name="Policy Number", 
        default=generate_policy_number,
        primary_key=True
    )
    certificate_type = models.CharField(max_length=20, choices=CERTIFICATE_TYPES, verbose_name="Insurance Type")
    coverage_level = models.CharField(max_length=20, choices=COVERAGE_LEVELS, verbose_name="Coverage Level", default='basic')
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default='active', verbose_name="Status",
        error_messages={
            'required': 'Please select the certificate status.',
        },
        help_text="Set the current status of this certificate."
    )
    
    # Client Information (Unified - no separate member fields)
    client_name = models.CharField(
        max_length=200, verbose_name="Client Name",
        error_messages={
            'blank': 'Client name is required.',
            'required': 'Client name is required.'
        },
        help_text="Enter the full name of the client."
    )
    client_email = models.EmailField(
        verbose_name="Client Email",
        error_messages={
            'invalid': 'Please enter a valid email address.',
            'blank': 'Client email is required.',
            'required': 'Client email is required.'
        },
        help_text="Enter a valid email address for the client."
    )
    client_phone = models.CharField(
        max_length=20, verbose_name="Client Phone",
        error_messages={
            'blank': 'Client phone number is required.',
            'required': 'Client phone number is required.'
        },
        help_text="Enter the client's phone number."
    )
    client_address = models.TextField(verbose_name="Client Address", help_text="Enter the client's address.")
    client_id_number = models.CharField(
        max_length=50, verbose_name="Client ID Number",
        error_messages={
            'blank': 'Client ID number is required.',
            'required': 'Client ID number is required.'
        },
        help_text="Enter the client's government-issued ID number."
    )
    client_date_of_birth = models.DateField(verbose_name="Date of Birth", help_text="Select the client's date of birth.")
    client_bank_name = models.CharField(
        max_length=200, blank=True, verbose_name="Bank Name",
        help_text="Enter the client's bank name (optional)."
    )
    client_bank_account = models.CharField(
        max_length=50, blank=True, verbose_name="Bank Account Number",
        help_text="Enter the client's bank account number (optional)."
    )
    
    # Insurance Details - Clear distinction between amounts
    insured_amount = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Insured Amount",
        error_messages={
            'invalid': 'Please enter a valid insured amount.',
            'required': 'Insured amount is required.'
        },
        help_text="Total amount covered by this certificate (the maximum payout)."
    )
    premium_amount = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Premium Amount",
        error_messages={
            'invalid': 'Please enter a valid premium amount.',
            'required': 'Premium amount is required.'
        },
        help_text="Amount the client pays for this certificate (what they owe)."
    )
    total_premium = models.DecimalField(
        max_digits=15, decimal_places=2, verbose_name="Total Premium",
        help_text="Total premium including all fees and charges (internal calculation)."
    )
    net_contribution = models.DecimalField(max_digits=15, decimal_places=2, default=10000, verbose_name="Net Contribution")
    proportional_stamp = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="½ Proportional Stamp")
    dimensional_stamp = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="½ Dimensional Stamp")
    supervision_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Supervision Fees")
    insurance_fees = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Insurance Fees")
    total_premium_words = models.CharField(max_length=200, blank=True, verbose_name="Total Premium (words)")
    
    # Dates
    start_date = models.DateField(verbose_name="Start Date", help_text="Select the start date of coverage.")
    end_date = models.DateField(verbose_name="End Date", help_text="Select the end date of coverage.")
    issue_date = models.DateTimeField(auto_now_add=True, verbose_name="Issue Date")
    last_modified = models.DateTimeField(auto_now=True, verbose_name="Last Modified")
    
    # Additional Information
    description = models.TextField(blank=True, verbose_name="Description")
    terms_conditions = models.TextField(blank=True, verbose_name="Terms & Conditions")
    special_conditions = models.TextField(blank=True, verbose_name="Special Conditions")
    
    # Financial Status
    payment_status = models.CharField(max_length=20, choices=[
        ('paid', 'Paid'),
        ('pending', 'Pending'),
        ('overdue', 'Overdue'),
        ('installment', 'Installment'),
        ('cancelled', 'Cancelled'),
    ], default='pending', verbose_name="Payment Status")
    
    # Agent Information
    agent_name = models.CharField(max_length=200, blank=True, verbose_name="Agent Name")
    agent_id = models.CharField(max_length=50, blank=True, verbose_name="Agent ID")
    
    # Verification
    is_verified = models.BooleanField(default=False, verbose_name="Verified")
    verification_date = models.DateTimeField(null=True, blank=True, verbose_name="Verification Date")
    
    # Activity and Location Information
    location = models.CharField(max_length=255, verbose_name="Location", help_text="Where the insured activity takes place.")
    activity = models.CharField(max_length=255, verbose_name="Activity", help_text="What activity or business is being insured.")
    description_of_risk = models.TextField(default="This policy indemnifies the Insured against legal liability for bodily injury to third parties arising from the Insured's business activities.", verbose_name="Description of Risk", help_text="Description of the risks being covered.")
    period_from = models.DateField(verbose_name="Period From")
    period_to = models.DateField(verbose_name="Period To")
    
    def set_defaults_by_coverage(self):
        """Set default values based on coverage level"""
        if self.coverage_level == 'comprehensive':
            self.net_contribution = 10000
            self.proportional_stamp = 500
            self.dimensional_stamp = 2
            self.supervision_fees = 89.97
            self.insurance_fees = 58.03
            self.total_premium = 10650
            self.total_premium_words = "Ten Thousand Six Hundred Fifty US Dollars"
            # Set insured amount to a reasonable multiple of the liability
            self.insured_amount = 10000000  # 10M coverage
            # Set premium amount to total premium (what client pays)
            self.premium_amount = self.total_premium
        elif self.coverage_level == 'basic':
            self.net_contribution = 5000
            self.proportional_stamp = 0
            self.dimensional_stamp = 0
            self.supervision_fees = 0
            self.insurance_fees = 0
            self.total_premium = 5000
            self.total_premium_words = "Five Thousand US Dollars"
            self.insured_amount = 2000000  # 2M coverage
            self.premium_amount = self.total_premium
        elif self.coverage_level == 'standard':
            self.net_contribution = 7000
            self.proportional_stamp = 250
            self.dimensional_stamp = 1
            self.supervision_fees = 45
            self.insurance_fees = 30
            self.total_premium = 7326
            self.total_premium_words = "Seven Thousand Three Hundred Twenty-Six US Dollars"
            self.insured_amount = 5000000  # 5M coverage
            self.premium_amount = self.total_premium
        elif self.coverage_level == 'premium':
            self.net_contribution = 8500
            self.proportional_stamp = 350
            self.dimensional_stamp = 1.5
            self.supervision_fees = 60
            self.insurance_fees = 40
            self.total_premium = 8951.5
            self.total_premium_words = "Eight Thousand Nine Hundred Fifty-One and 50/100 US Dollars"
            self.insured_amount = 8000000  # 8M coverage
            self.premium_amount = self.total_premium
        elif self.coverage_level == 'elite':
            self.net_contribution = 20000
            self.proportional_stamp = 1000
            self.dimensional_stamp = 5
            self.supervision_fees = 150
            self.insurance_fees = 100
            self.total_premium = 21255
            self.total_premium_words = "Twenty-One Thousand Two Hundred Fifty-Five US Dollars"
            self.insured_amount = 20000000  # 20M coverage
            self.premium_amount = self.total_premium

    def calculate_total_premium(self):
        """Calculate total premium from components"""
        return (self.net_contribution + 
                self.proportional_stamp + 
                self.dimensional_stamp + 
                self.supervision_fees + 
                self.insurance_fees)

    def update_premium_amount(self):
        """Update premium amount to match total premium"""
        self.premium_amount = self.total_premium

    def save(self, *args, **kwargs):
        # Sync the date fields to maintain compatibility
        if not self.period_from:
            self.period_from = self.start_date
        if not self.period_to:
            self.period_to = self.end_date
        # Calculate total premium if not set
        if not self.total_premium:
            self.total_premium = self.calculate_total_premium()
        # Ensure premium amount matches total premium
        if self.premium_amount != self.total_premium:
            self.premium_amount = self.total_premium
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Insurance Certificate"
        verbose_name_plural = "Insurance Certificates"
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['policy_number']),
            models.Index(fields=['client_name']),
            models.Index(fields=['status']),
            models.Index(fields=['issue_date']),
        ]

    def __str__(self):
        return f"{self.policy_number} - {self.client_name}"

    @property
    def is_active(self):
        return self.status == 'active' and self.end_date >= timezone.now().date()

    @property
    def days_remaining(self):
        return (self.end_date - timezone.now().date()).days

    @property
    def total_paid_amount(self):
        return sum(payment.amount for payment in self.payments.filter(status='completed'))

    @property
    def remaining_amount(self):
        return self.premium_amount - self.total_paid_amount

    @property
    def certificate_title(self):
        """Generate certificate title based on type and coverage"""
        type_display = self.get_certificate_type_display()
        coverage_display = self.get_coverage_level_display()
        return f"{type_display} Certificate - {coverage_display}"

    def get_coverage_summary(self):
        """Get a summary of coverage details"""
        return {
            'insured_amount': self.insured_amount,
            'premium_amount': self.premium_amount,
            'total_premium': self.total_premium,
        }

class CertificateVerification(models.Model):
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='verifications', null=True, blank=True)
    verification_code = models.CharField(max_length=50, unique=True, verbose_name="Verification Code")
    status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending', verbose_name="Status")
    verified_at = models.DateTimeField(null=True, blank=True, verbose_name="Verified At")
    verified_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Verified By")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created At")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated At")
    
    class Meta:
        verbose_name = "Certificate Verification"
        verbose_name_plural = "Certificate Verifications"
        ordering = ['-verified_at']
        indexes = [
            models.Index(fields=['verification_code']),
            models.Index(fields=['status']),
            models.Index(fields=['verified_at']),
        ]

    def __str__(self):
        return f"Verification {self.verification_code} - {self.status}"

class Payment(models.Model):
    PAYMENT_METHODS = [
        ('cash', 'Cash'),
        ('bank_transfer', 'Bank Transfer'),
        ('credit_card', 'Credit Card'),
        ('debit_card', 'Debit Card'),
        ('check', 'Check'),
        ('online', 'Online Payment'),
        ('mobile_money', 'Mobile Money'),
        ('insurance_card', 'Insurance Card'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='payments', verbose_name="Certificate")
    payment_number = models.CharField(max_length=50, unique=True, verbose_name="Payment Number")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, verbose_name="Payment Method")
    status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending', verbose_name="Status")
    
    # Payment Details
    payment_date = models.DateTimeField(auto_now_add=True, verbose_name="Payment Date")
    due_date = models.DateField(verbose_name="Due Date")
    processed_date = models.DateTimeField(null=True, blank=True, verbose_name="Processed Date")
    
    # Transaction Details
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name="Transaction ID")
    reference_number = models.CharField(max_length=100, blank=True, verbose_name="Reference Number")
    
    # Additional Information
    description = models.TextField(blank=True, verbose_name="Description")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Processing Information
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Processed By")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP Address")
    
    class Meta:
        verbose_name = "Payment"
        verbose_name_plural = "Payments"
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['payment_number']),
            models.Index(fields=['certificate']),
            models.Index(fields=['status']),
            models.Index(fields=['payment_date']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Payment {self.payment_number} - {self.certificate.policy_number}"

class Installment(models.Model):
    INSTALLMENT_STATUS = [
        ('pending', 'Pending'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('defaulted', 'Defaulted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='installments', verbose_name="Certificate")
    installment_number = models.CharField(max_length=50, verbose_name="Installment Number")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    due_date = models.DateField(verbose_name="Due Date")
    status = models.CharField(max_length=20, choices=INSTALLMENT_STATUS, default='pending', verbose_name="Status")
    
    # Payment Information
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Paid Amount")
    paid_date = models.DateTimeField(null=True, blank=True, verbose_name="Paid Date")
    
    # Late Payment Information
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Late Fee")
    grace_period_days = models.IntegerField(default=15, verbose_name="Grace Period (Days)")
    
    # Additional Information
    description = models.TextField(blank=True, verbose_name="Description")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Installment"
        verbose_name_plural = "Installments"
        ordering = ['due_date']
        indexes = [
            models.Index(fields=['certificate']),
            models.Index(fields=['status']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Installment {self.installment_number} - {self.certificate.policy_number}"
    
    @property
    def is_overdue(self):
        if self.due_date is not None:
            return self.due_date < timezone.now().date() and self.status == 'pending'
        return False
    
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    @property
    def remaining_amount(self):
        amount = self.amount if self.amount is not None else Decimal('0.00')
        paid = self.paid_amount if self.paid_amount is not None else Decimal('0.00')
        return amount - paid

class Invoice(models.Model):
    INVOICE_STATUS = [
        ('draft', 'Draft'),
        ('sent', 'Sent'),
        ('paid', 'Paid'),
        ('overdue', 'Overdue'),
        ('cancelled', 'Cancelled'),
        ('disputed', 'Disputed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='invoices', verbose_name="Certificate")
    invoice_number = models.CharField(max_length=50, unique=True, verbose_name="Invoice Number")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Tax Amount")
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Total Amount")
    
    # Invoice Details
    issue_date = models.DateField(auto_now_add=True, verbose_name="Issue Date")
    due_date = models.DateField(verbose_name="Due Date")
    status = models.CharField(max_length=20, choices=INVOICE_STATUS, default='draft', verbose_name="Status")
    
    # Payment Information
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Paid Amount")
    paid_date = models.DateTimeField(null=True, blank=True, verbose_name="Paid Date")
    
    # Additional Information
    description = models.TextField(blank=True, verbose_name="Description")
    terms_conditions = models.TextField(blank=True, verbose_name="Terms & Conditions")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Billing Information
    billing_address = models.TextField(blank=True, verbose_name="Billing Address")
    billing_email = models.EmailField(blank=True, verbose_name="Billing Email")
    
    class Meta:
        verbose_name = "Invoice"
        verbose_name_plural = "Invoices"
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['invoice_number']),
            models.Index(fields=['certificate']),
            models.Index(fields=['status']),
            models.Index(fields=['issue_date']),
            models.Index(fields=['due_date']),
        ]

    def __str__(self):
        return f"Invoice {self.invoice_number} - {self.certificate.policy_number}"
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status in ['sent', 'overdue']
    
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    @property
    def remaining_amount(self):
        total = self.total_amount if self.total_amount is not None else Decimal('0.00')
        paid = self.paid_amount if self.paid_amount is not None else Decimal('0.00')
        return total - paid

class FinancialTransaction(models.Model):
    TRANSACTION_TYPES = [
        ('premium_payment', 'Premium Payment'),
        ('installment_payment', 'Installment Payment'),
        ('late_fee', 'Late Fee'),
        ('refund', 'Refund'),
        ('adjustment', 'Adjustment'),
        ('commission', 'Commission'),
        ('penalty', 'Penalty'),
        ('discount', 'Discount'),
    ]
    
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('reversed', 'Reversed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='transactions', verbose_name="Certificate")
    transaction_number = models.CharField(max_length=50, unique=True, verbose_name="Transaction Number")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="Transaction Type")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Amount")
    status = models.CharField(max_length=20, choices=TRANSACTION_STATUS, default='pending', verbose_name="Status")
    
    # Related Records
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Related Payment")
    installment = models.ForeignKey(Installment, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Related Installment")
    invoice = models.ForeignKey(Invoice, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Related Invoice")
    
    # Transaction Details
    transaction_date = models.DateTimeField(auto_now_add=True, verbose_name="Transaction Date")
    processed_date = models.DateTimeField(null=True, blank=True, verbose_name="Processed Date")
    
    # Additional Information
    description = models.TextField(blank=True, verbose_name="Description")
    reference = models.CharField(max_length=100, blank=True, verbose_name="Reference")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Processing Information
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Processed By")
    
    class Meta:
        verbose_name = "Financial Transaction"
        verbose_name_plural = "Financial Transactions"
        ordering = ['-transaction_date']
        indexes = [
            models.Index(fields=['transaction_number']),
            models.Index(fields=['certificate']),
            models.Index(fields=['transaction_type']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_date']),
        ]

    def __str__(self):
        return f"Transaction {self.transaction_number} - {self.certificate.policy_number}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_number:
            # Generate transaction number
            last_transaction = FinancialTransaction.objects.order_by('-transaction_date').first()
            if last_transaction:
                last_number = int(last_transaction.transaction_number.split('-')[-1])
                self.transaction_number = f"TXN-{timezone.now().strftime('%Y%m')}-{last_number + 1:06d}"
            else:
                self.transaction_number = f"TXN-{timezone.now().strftime('%Y%m')}-000001"
        super().save(*args, **kwargs)

class Claim(models.Model):
    CLAIM_STATUS = [
        ('filed', 'Filed'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('rejected', 'Rejected'),
        ('pending_documents', 'Pending Documents'),
        ('investigation', 'Under Investigation'),
    ]
    
    CLAIM_TYPES = [
        ('medical', 'Medical'),
        ('property', 'Property'),
        ('liability', 'Liability'),
        ('accident', 'Accident'),
        ('theft', 'Theft'),
        ('natural_disaster', 'Natural Disaster'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='claims', verbose_name="Certificate")
    claim_number = models.CharField(max_length=50, unique=True, verbose_name="Claim Number")
    claim_type = models.CharField(max_length=20, choices=CLAIM_TYPES, verbose_name="Claim Type")
    status = models.CharField(max_length=20, choices=CLAIM_STATUS, default='filed', verbose_name="Status")
    
    # Financial Information
    claimed_amount = models.DecimalField(max_digits=15, decimal_places=2, verbose_name="Claimed Amount")
    approved_amount = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True, verbose_name="Approved Amount")
    paid_amount = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Paid Amount")
    
    # Dates
    incident_date = models.DateField(verbose_name="Incident Date")
    filed_date = models.DateTimeField(auto_now_add=True, verbose_name="Filed Date")
    review_date = models.DateTimeField(null=True, blank=True, verbose_name="Review Date")
    approval_date = models.DateTimeField(null=True, blank=True, verbose_name="Approval Date")
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name="Payment Date")
    
    # Claim Details
    description = models.TextField(verbose_name="Claim Description")
    incident_location = models.CharField(max_length=255, verbose_name="Incident Location")
    police_report = models.CharField(max_length=100, blank=True, verbose_name="Police Report Number")
    
    # Additional Information
    claimant_name = models.CharField(max_length=200, verbose_name="Claimant Name")
    claimant_phone = models.CharField(max_length=20, verbose_name="Claimant Phone")
    claimant_email = models.EmailField(verbose_name="Claimant Email")
    
    # Processing Information
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Assigned To")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    class Meta:
        verbose_name = "Claim"
        verbose_name_plural = "Claims"
        ordering = ['-filed_date']
        indexes = [
            models.Index(fields=['claim_number']),
            models.Index(fields=['certificate']),
            models.Index(fields=['status']),
            models.Index(fields=['claim_type']),
            models.Index(fields=['filed_date']),
        ]

    def __str__(self):
        return f"Claim {self.claim_number} - {self.certificate.policy_number}"
    
    def save(self, *args, **kwargs):
        if not self.claim_number:
            # Generate claim number
            last_claim = Claim.objects.order_by('-filed_date').first()
            if last_claim:
                last_number = int(last_claim.claim_number.split('-')[-1])
                self.claim_number = f"CLM-{timezone.now().strftime('%Y%m')}-{last_number + 1:06d}"
            else:
                self.claim_number = f"CLM-{timezone.now().strftime('%Y%m')}-000001"
        super().save(*args, **kwargs)
    
    @property
    def is_approved(self):
        return self.status == 'approved' or self.status == 'paid'
    
    @property
    def is_paid(self):
        return self.status == 'paid'
    
    @property
    def remaining_amount(self):
        if self.approved_amount:
            return self.approved_amount - self.paid_amount
        return 0

class Commission(models.Model):
    COMMISSION_TYPES = [
        ('agent', 'Agent Commission'),
        ('broker', 'Broker Commission'),
        ('referral', 'Referral Commission'),
        ('bonus', 'Performance Bonus'),
        ('override', 'Override Commission'),
    ]
    
    COMMISSION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('paid', 'Paid'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='commissions', verbose_name="Certificate")
    commission_number = models.CharField(max_length=50, unique=True, verbose_name="Commission Number")
    commission_type = models.CharField(max_length=20, choices=COMMISSION_TYPES, verbose_name="Commission Type")
    status = models.CharField(max_length=20, choices=COMMISSION_STATUS, default='pending', verbose_name="Status")
    
    # Financial Information
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Commission Rate (%)")
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Commission Amount")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Paid Amount")
    
    # Recipient Information
    recipient_name = models.CharField(max_length=200, verbose_name="Recipient Name")
    recipient_id = models.CharField(max_length=50, verbose_name="Recipient ID")
    recipient_bank = models.CharField(max_length=200, blank=True, verbose_name="Bank Name")
    recipient_account = models.CharField(max_length=50, blank=True, verbose_name="Account Number")
    
    # Dates
    earned_date = models.DateTimeField(auto_now_add=True, verbose_name="Earned Date")
    approved_date = models.DateTimeField(null=True, blank=True, verbose_name="Approved Date")
    paid_date = models.DateTimeField(null=True, blank=True, verbose_name="Paid Date")
    
    # Additional Information
    description = models.TextField(blank=True, verbose_name="Description")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Processing Information
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Approved By")
    
    class Meta:
        verbose_name = "Commission"
        verbose_name_plural = "Commissions"
        ordering = ['-earned_date']
        indexes = [
            models.Index(fields=['commission_number']),
            models.Index(fields=['certificate']),
            models.Index(fields=['status']),
            models.Index(fields=['commission_type']),
            models.Index(fields=['earned_date']),
        ]

    def __str__(self):
        return f"Commission {self.commission_number} - {self.certificate.policy_number}"
    
    def save(self, *args, **kwargs):
        if not self.commission_number:
            # Generate commission number
            last_commission = Commission.objects.order_by('-earned_date').first()
            if last_commission:
                last_number = int(last_commission.commission_number.split('-')[-1])
                self.commission_number = f"COM-{timezone.now().strftime('%Y%m')}-{last_number + 1:06d}"
            else:
                self.commission_number = f"COM-{timezone.now().strftime('%Y%m')}-000001"
        super().save(*args, **kwargs)
    
    @property
    def is_paid(self):
        return self.status == 'paid'
    
    @property
    def remaining_amount(self):
        return self.commission_amount - self.paid_amount

class Fee(models.Model):
    FEE_TYPES = [
        ('processing', 'Processing Fee'),
        ('late_fee', 'Late Fee'),
        ('cancellation', 'Cancellation Fee'),
        ('reinstatement', 'Reinstatement Fee'),
        ('endorsement', 'Endorsement Fee'),
        ('renewal', 'Renewal Fee'),
        ('admin', 'Administrative Fee'),
        ('service', 'Service Fee'),
    ]
    
    FEE_STATUS = [
        ('pending', 'Pending'),
        ('charged', 'Charged'),
        ('paid', 'Paid'),
        ('waived', 'Waived'),
        ('cancelled', 'Cancelled'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    certificate = models.ForeignKey(Certificate, on_delete=models.CASCADE, related_name='fees', verbose_name="Certificate")
    fee_number = models.CharField(max_length=50, unique=True, verbose_name="Fee Number")
    fee_type = models.CharField(max_length=20, choices=FEE_TYPES, verbose_name="Fee Type")
    status = models.CharField(max_length=20, choices=FEE_STATUS, default='pending', verbose_name="Status")
    
    # Financial Information
    fee_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Fee Amount")
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0, verbose_name="Paid Amount")
    
    # Dates
    charged_date = models.DateTimeField(auto_now_add=True, verbose_name="Charged Date")
    due_date = models.DateField(verbose_name="Due Date")
    paid_date = models.DateTimeField(null=True, blank=True, verbose_name="Paid Date")
    
    # Additional Information
    description = models.TextField(blank=True, verbose_name="Description")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Processing Information
    charged_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Charged By")
    
    class Meta:
        verbose_name = "Fee"
        verbose_name_plural = "Fees"
        ordering = ['-charged_date']
        indexes = [
            models.Index(fields=['fee_number']),
            models.Index(fields=['certificate']),
            models.Index(fields=['status']),
            models.Index(fields=['fee_type']),
            models.Index(fields=['charged_date']),
        ]

    def __str__(self):
        return f"Fee {self.fee_number} - {self.certificate.policy_number}"
    
    def save(self, *args, **kwargs):
        if not self.fee_number:
            # Generate fee number
            last_fee = Fee.objects.order_by('-charged_date').first()
            if last_fee:
                last_number = int(last_fee.fee_number.split('-')[-1])
                self.fee_number = f"FEE-{timezone.now().strftime('%Y%m')}-{last_number + 1:06d}"
            else:
                self.fee_number = f"FEE-{timezone.now().strftime('%Y%m')}-000001"
        super().save(*args, **kwargs)
    
    @property
    def is_overdue(self):
        return self.due_date < timezone.now().date() and self.status in ['pending', 'charged']
    
    @property
    def days_overdue(self):
        if self.is_overdue:
            return (timezone.now().date() - self.due_date).days
        return 0
    
    @property
    def is_paid(self):
        return self.status == 'paid'
    
    @property
    def remaining_amount(self):
        return self.fee_amount - self.paid_amount

class FinancialReport(models.Model):
    REPORT_TYPES = [
        ('daily', 'Daily Report'),
        ('weekly', 'Weekly Report'),
        ('monthly', 'Monthly Report'),
        ('quarterly', 'Quarterly Report'),
        ('annual', 'Annual Report'),
        ('custom', 'Custom Report'),
    ]
    
    REPORT_STATUS = [
        ('draft', 'Draft'),
        ('generated', 'Generated'),
        ('sent', 'Sent'),
        ('archived', 'Archived'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    report_number = models.CharField(max_length=50, unique=True, verbose_name="Report Number")
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, verbose_name="Report Type")
    status = models.CharField(max_length=20, choices=REPORT_STATUS, default='draft', verbose_name="Status")
    
    # Report Period
    start_date = models.DateField(verbose_name="Start Date")
    end_date = models.DateField(verbose_name="End Date")
    
    # Financial Summary
    total_premiums = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total Premiums")
    total_payments = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total Payments")
    total_claims = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total Claims")
    total_commissions = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total Commissions")
    total_fees = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Total Fees")
    net_revenue = models.DecimalField(max_digits=15, decimal_places=2, default=0, verbose_name="Net Revenue")
    
    # Report Details
    title = models.CharField(max_length=200, verbose_name="Report Title")
    description = models.TextField(blank=True, verbose_name="Description")
    notes = models.TextField(blank=True, verbose_name="Notes")
    
    # Generation Information
    created_date = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    generated_date = models.DateTimeField(null=True, blank=True, verbose_name="Generated Date")
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Generated By")
    
    # File Information
    file_path = models.CharField(max_length=500, blank=True, verbose_name="File Path")
    file_size = models.IntegerField(default=0, verbose_name="File Size (bytes)")
    
    class Meta:
        verbose_name = "Financial Report"
        verbose_name_plural = "Financial Reports"
        ordering = ['-created_date']
        indexes = [
            models.Index(fields=['report_number']),
            models.Index(fields=['report_type']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date']),
            models.Index(fields=['end_date']),
        ]

    def __str__(self):
        return f"Report {self.report_number} - {self.title}"
    
    def save(self, *args, **kwargs):
        if not self.report_number:
            # Generate report number
            last_report = FinancialReport.objects.order_by('-created_date').first()
            if last_report:
                last_number = int(last_report.report_number.split('-')[-1])
                self.report_number = f"RPT-{timezone.now().strftime('%Y%m')}-{last_number + 1:06d}"
            else:
                self.report_number = f"RPT-{timezone.now().strftime('%Y%m')}-000001"
        super().save(*args, **kwargs)
    
    @property
    def is_generated(self):
        return self.status in ['generated', 'sent', 'archived']
    
    @property
    def report_period(self):
        return f"{self.start_date.strftime('%b %d, %Y')} - {self.end_date.strftime('%b %d, %Y')}"
