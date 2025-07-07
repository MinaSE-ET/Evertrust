from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas
from io import BytesIO
from django.template.loader import render_to_string
from django.utils import timezone
import os
from docx import Document
from docx.shared import Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.shared import OxmlElement, qn
from docx2pdf import convert
import tempfile
import json

def generate_certificate_pdf(certificate):
    """Generate PDF certificate using HTML template with background image"""
    try:
        # Use WeasyPrint for better HTML to PDF conversion with background support
        from weasyprint import HTML, CSS
        from django.conf import settings
        
        # Render the HTML template
        html_content = render_to_string('certificates/certificate_pdf.html', {
            'certificate': certificate
        })
        
        # Create PDF from HTML
        html = HTML(string=html_content)
        pdf_content = html.write_pdf()
        
        return pdf_content
        
    except ImportError:
        # Fallback to ReportLab if WeasyPrint is not available
        return generate_certificate_pdf_reportlab(certificate)

def generate_certificate_pdf_reportlab(certificate):
    """Generate PDF certificate using ReportLab (fallback method)"""
    
    # Create buffer for PDF
    buffer = BytesIO()
    
    # Create PDF document
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    story = []
    
    # Get styles
    styles = getSampleStyleSheet()
    
    # Custom styles
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=18,
        spaceAfter=30,
        alignment=TA_CENTER,
        textColor=colors.darkblue
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        spaceAfter=12,
        spaceBefore=20,
        textColor=colors.darkblue
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=6
    )
    
    # Header
    story.append(Paragraph("EVER TRUST", title_style))
    story.append(Paragraph(certificate.certificate_title, heading_style))
    story.append(Spacer(1, 20))
    
    # Policy Number
    story.append(Paragraph(f"<b>Policy Number:</b> {certificate.policy_number}", normal_style))
    story.append(Paragraph(f"<b>Issue Date:</b> {certificate.issue_date.strftime('%B %d, %Y')}", normal_style))
    story.append(Spacer(1, 20))
    
    # Client Information
    story.append(Paragraph("CLIENT INFORMATION", heading_style))
    story.append(Paragraph(f"<b>Name:</b> {certificate.client_name}", normal_style))
    story.append(Paragraph(f"<b>Address:</b> {certificate.client_address}", normal_style))
    story.append(Paragraph(f"<b>Phone:</b> {certificate.client_phone}", normal_style))
    if certificate.client_email:
        story.append(Paragraph(f"<b>Email:</b> {certificate.client_email}", normal_style))
    story.append(Paragraph(f"<b>ID Number:</b> {certificate.client_id_number}", normal_style))
    story.append(Paragraph(f"<b>Date of Birth:</b> {certificate.client_date_of_birth.strftime('%B %d, %Y')}", normal_style))
    if certificate.client_bank_name:
        story.append(Paragraph(f"<b>Bank Name:</b> {certificate.client_bank_name}", normal_style))
    if certificate.client_bank_account:
        story.append(Paragraph(f"<b>Bank Account:</b> {certificate.client_bank_account}", normal_style))
    
    # Insurance Details
    story.append(Paragraph("INSURANCE DETAILS", heading_style))
    story.append(Paragraph(f"<b>Insurance Type:</b> {certificate.get_certificate_type_display()}", normal_style))
    story.append(Paragraph(f"<b>Coverage Level:</b> {certificate.get_coverage_level_display()}", normal_style))
    story.append(Paragraph(f"<b>Insured Amount:</b> ${certificate.insured_amount:,.2f}", normal_style))
    story.append(Paragraph(f"<b>Premium Amount:</b> ${certificate.premium_amount:,.2f}", normal_style))
    story.append(Paragraph(f"<b>Total Premium:</b> ${certificate.total_premium:,.2f}", normal_style))
    
    # Insurance Period
    story.append(Paragraph("INSURANCE PERIOD", heading_style))
    story.append(Paragraph(f"<b>Start Date:</b> {certificate.start_date.strftime('%B %d, %Y')}", normal_style))
    story.append(Paragraph(f"<b>End Date:</b> {certificate.end_date.strftime('%B %d, %Y')}", normal_style))
    story.append(Paragraph(f"<b>Days Remaining:</b> {certificate.days_remaining} days", normal_style))
    
    # Financial Information
    story.append(Paragraph("FINANCIAL INFORMATION", heading_style))
    story.append(Paragraph(f"<b>Total Paid Amount:</b> ${certificate.total_paid_amount:,.2f}", normal_style))
    story.append(Paragraph(f"<b>Remaining Amount:</b> ${certificate.remaining_amount:,.2f}", normal_style))
    story.append(Paragraph(f"<b>Payment Status:</b> {certificate.get_payment_status_display()}", normal_style))
    
    # Agent Information
    if certificate.agent_name or certificate.agent_id:
        story.append(Paragraph("AGENT INFORMATION", heading_style))
        if certificate.agent_name:
            story.append(Paragraph(f"<b>Agent Name:</b> {certificate.agent_name}", normal_style))
        if certificate.agent_id:
            story.append(Paragraph(f"<b>Agent ID:</b> {certificate.agent_id}", normal_style))
    
    # Additional Information
    if certificate.description:
        story.append(Paragraph("DESCRIPTION", heading_style))
        story.append(Paragraph(certificate.description, normal_style))
    
    if certificate.terms_conditions:
        story.append(Paragraph("TERMS & CONDITIONS", heading_style))
        story.append(Paragraph(certificate.terms_conditions, normal_style))
    
    if certificate.special_conditions:
        story.append(Paragraph("SPECIAL CONDITIONS", heading_style))
        story.append(Paragraph(certificate.special_conditions, normal_style))
    
    # Certificate Status
    story.append(Paragraph("CERTIFICATE STATUS", heading_style))
    status_text = "ACTIVE" if certificate.is_active else "INACTIVE"
    status_color = colors.green if certificate.is_active else colors.red
    status_style = ParagraphStyle(
        'Status',
        parent=normal_style,
        textColor=status_color,
        fontSize=12,
        alignment=TA_CENTER
    )
    story.append(Paragraph(f"<b>Status: {status_text}</b>", status_style))
    
    # Footer
    story.append(Spacer(1, 30))
    footer_style = ParagraphStyle(
        'Footer',
        parent=normal_style,
        fontSize=8,
        alignment=TA_CENTER,
        textColor=colors.grey
    )
    story.append(Paragraph("This certificate is generated electronically by EverTrust Management System", footer_style))
    story.append(Paragraph(f"Generated on: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", footer_style))
    
    # Build PDF
    doc.build(story)
    
    # Get PDF content
    pdf_content = buffer.getvalue()
    buffer.close()
    
    return pdf_content

def fill_certificate_docx_template(certificate, template_path, output_path):
    doc = Document(template_path)
    # Replace placeholders in the DOCX template with certificate data
    mapping = {
        '{{policy_number}}': certificate.policy_number,
        '{{issue_date}}': certificate.issue_date.strftime('%d/%m/%Y') if certificate.issue_date else '',
        '{{client_name}}': certificate.client_name,
        '{{location}}': certificate.location,
        '{{activity}}': certificate.activity,
        '{{period_from}}': certificate.period_from.strftime('%d/%m/%Y') if certificate.period_from else '',
        '{{period_to}}': certificate.period_to.strftime('%d/%m/%Y') if certificate.period_to else '',
        '{{liability_per_person}}': f"{certificate.liability_per_person:,.2f} USD",
        '{{liability_per_occurrence}}': f"{certificate.liability_per_occurrence:,.2f} USD",
        '{{liability_aggregate}}': f"{certificate.liability_aggregate:,.2f} USD",
        '{{net_contribution}}': f"{certificate.net_contribution:,.2f}",
        '{{proportional_stamp}}': f"{certificate.proportional_stamp:,.2f}",
        '{{dimensional_stamp}}': f"{certificate.dimensional_stamp:,.2f}",
        '{{supervision_fees}}': f"{certificate.supervision_fees:,.2f}",
        '{{insurance_fees}}': f"{certificate.insurance_fees:,.2f}",
        '{{total_premium}}': f"{certificate.total_premium:,.2f}",
        '{{total_premium_words}}': certificate.total_premium_words,
        '{{coverage_level}}': certificate.coverage_level.title(),
        '{{certificate_title}}': certificate.certificate_title,
        '{{description_of_risk}}': "This policy indemnifies the Insured against legal liability for bodily injury to third parties arising from the Insured's business activities.",
        '{{client_bank_name}}': certificate.client_bank_name or '',
        '{{client_bank_account}}': certificate.client_bank_account or '',
    }
    for p in doc.paragraphs:
        for key, value in mapping.items():
            if key in p.text:
                p.text = p.text.replace(key, str(value))
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for key, value in mapping.items():
                    if key in cell.text:
                        cell.text = cell.text.replace(key, str(value))
    doc.save(output_path)

def docx_to_pdf(docx_path, pdf_path):
    """Convert DOCX file to PDF"""
    try:
        convert(docx_path, pdf_path)
        return True
    except Exception as e:
        print(f"Error converting DOCX to PDF: {e}")
        return False

def generate_certificate_from_template(certificate, template_path):
    """Generate certificate PDF from DOCX template"""
    try:
        # Prepare data for template
        data = {
            'POLICY_NUMBER': certificate.policy_number,
            'CLIENT_NAME': certificate.client_name,
            'CLIENT_EMAIL': certificate.client_email or 'N/A',
            'CLIENT_PHONE': certificate.client_phone,
            'CLIENT_ADDRESS': certificate.client_address,
            'CLIENT_ID_NUMBER': certificate.client_id_number,
            'CLIENT_DATE_OF_BIRTH': certificate.client_date_of_birth.strftime('%B %d, %Y'),
            'INSURANCE_TYPE': certificate.get_certificate_type_display(),
            'COVERAGE_LEVEL': certificate.get_coverage_level_display(),
            'INSURED_AMOUNT': f"${certificate.insured_amount:,.2f}",
            'PREMIUM_AMOUNT': f"${certificate.premium_amount:,.2f}",
            'DEDUCTIBLE_AMOUNT': f"${certificate.deductible_amount:,.2f}",

            'START_DATE': certificate.start_date.strftime('%B %d, %Y'),
            'END_DATE': certificate.end_date.strftime('%B %d, %Y'),
            'ISSUE_DATE': certificate.issue_date.strftime('%B %d, %Y'),
            'STATUS': certificate.get_status_display(),
            'PAYMENT_STATUS': certificate.get_payment_status_display(),
            'AGENT_NAME': certificate.agent_name or 'N/A',
            'AGENT_ID': certificate.agent_id or 'N/A',
            'DESCRIPTION': certificate.description or 'N/A',
            'TERMS_CONDITIONS': certificate.terms_conditions or 'N/A',
            'SPECIAL_CONDITIONS': certificate.special_conditions or 'N/A',
            'TOTAL_PAID': f"${certificate.total_paid_amount:,.2f}",
            'REMAINING_AMOUNT': f"${certificate.remaining_amount:,.2f}",
            'DAYS_REMAINING': f"{certificate.days_remaining} days" if certificate.days_remaining > 0 else "Expired",
            'GENERATED_DATE': timezone.now().strftime('%B %d, %Y at %I:%M %p'),
        }
        
        # Fill the template
        filled_doc = fill_certificate_docx_template(certificate, template_path, output_path)
        if not filled_doc:
            return None
        
        # Save filled document to temporary file
        with tempfile.NamedTemporaryFile(suffix='.docx', delete=False) as temp_docx:
            filled_doc.save(temp_docx.name)
            temp_docx_path = temp_docx.name
        
        # Convert to PDF
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as temp_pdf:
            temp_pdf_path = temp_pdf.name
        
        if docx_to_pdf(temp_docx_path, temp_pdf_path):
            # Read PDF content
            with open(temp_pdf_path, 'rb') as pdf_file:
                pdf_content = pdf_file.read()
            
            # Clean up temporary files
            os.unlink(temp_docx_path)
            os.unlink(temp_pdf_path)
            
            return pdf_content
        else:
            # Clean up temporary files
            if os.path.exists(temp_docx_path):
                os.unlink(temp_docx_path)
            return None
            
    except Exception as e:
        print(f"Error generating certificate from template: {e}")
        return None

def generate_certificate_html(certificate):
    """Generate HTML version of certificate"""
    context = {
        'certificate': certificate,
        'generated_date': timezone.now(),
    }
    
    return render_to_string('certificates/certificate_template.html', context) 