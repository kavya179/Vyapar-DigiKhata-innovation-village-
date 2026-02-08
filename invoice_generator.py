"""
Invoice Generator Module
Generates PDF invoices for transactions

Installation required:
pip install reportlab
"""

from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
from datetime import datetime
import io

def generate_invoice_pdf(invoice_data):
    """
    Generate PDF invoice
    
    invoice_data = {
        'invoice_number': 'INV001',
        'date': '2024-12-05',
        'shop_name': 'Kavya General Store',
        'shop_address': '123 Main St, Ahmedabad',
        'shop_phone': '9876543210',
        'shop_gst': 'Optional GST Number',
        'customer_name': 'John Doe',
        'customer_phone': '9876543210',
        'customer_address': '456 Customer St',
        'items': [
            {'name': 'Rice 1kg', 'quantity': 5, 'price': 60.00, 'total': 300.00},
            {'name': 'Oil 1L', 'quantity': 2, 'price': 180.00, 'total': 360.00}
        ],
        'subtotal': 660.00,
        'tax_percent': 0,  # Optional
        'tax_amount': 0.00,
        'total': 660.00
    }
    """
    
    # Create PDF in memory
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, topMargin=0.5*inch, bottomMargin=0.5*inch)
    
    # Container for PDF elements
    elements = []
    
    # Styles
    styles = getSampleStyleSheet()
    
    # Title Style
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1E3A8A'),
        spaceAfter=30,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    # Header styles
    header_style = ParagraphStyle(
        'Header',
        parent=styles['Normal'],
        fontSize=12,
        fontName='Helvetica-Bold',
        spaceAfter=6
    )
    
    normal_style = ParagraphStyle(
        'CustomNormal',
        parent=styles['Normal'],
        fontSize=10,
        spaceAfter=4
    )
    
    # Title
    title = Paragraph("<b>INVOICE</b>", title_style)
    elements.append(title)
    elements.append(Spacer(1, 0.2*inch))
    
    # Shop and Customer Info Table
    info_data = [
        [
            Paragraph(f"<b>{invoice_data['shop_name']}</b>", header_style),
            Paragraph(f"<b>Invoice #:</b> {invoice_data['invoice_number']}", normal_style)
        ],
        [
            Paragraph(f"{invoice_data['shop_address']}", normal_style),
            Paragraph(f"<b>Date:</b> {invoice_data['date']}", normal_style)
        ],
        [
            Paragraph(f"<b>Phone:</b> {invoice_data['shop_phone']}", normal_style),
            ''
        ]
    ]
    
    if invoice_data.get('shop_gst'):
        info_data.append([
            Paragraph(f"<b>GSTIN:</b> {invoice_data['shop_gst']}", normal_style),
            ''
        ])
    
    info_table = Table(info_data, colWidths=[3.5*inch, 3*inch])
    info_table.setStyle(TableStyle([
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('ALIGN', (1, 0), (1, -1), 'RIGHT'),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    
    elements.append(info_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Bill To Section
    elements.append(Paragraph("<b>Bill To:</b>", header_style))
    elements.append(Paragraph(f"<b>{invoice_data['customer_name']}</b>", normal_style))
    elements.append(Paragraph(f"Phone: {invoice_data.get('customer_phone', 'N/A')}", normal_style))
    if invoice_data.get('customer_address'):
        elements.append(Paragraph(f"{invoice_data['customer_address']}", normal_style))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Items Table
    items_data = [
        ['#', 'Item Description', 'Qty', 'Price', 'Total']
    ]
    
    for idx, item in enumerate(invoice_data['items'], 1):
        items_data.append([
            str(idx),
            item['name'],
            str(item['quantity']),
            f"₹{item['price']:.2f}",
            f"₹{item['total']:.2f}"
        ])
    
    items_table = Table(items_data, colWidths=[0.5*inch, 3*inch, 0.8*inch, 1.2*inch, 1.5*inch])
    items_table.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1E3A8A')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 11),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        
        # Body
        ('ALIGN', (0, 1), (0, -1), 'CENTER'),  # Serial number
        ('ALIGN', (2, 1), (2, -1), 'CENTER'),  # Quantity
        ('ALIGN', (3, 1), (-1, -1), 'RIGHT'),  # Price and Total
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 10),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#F3F4F6')]),
        
        # Grid
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#E5E7EB')),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING', (0, 1), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 1), (-1, -1), 8),
    ]))
    
    elements.append(items_table)
    elements.append(Spacer(1, 0.3*inch))
    
    # Totals Section
    totals_data = [
        ['', '', '', 'Subtotal:', f"₹{invoice_data['subtotal']:.2f}"]
    ]
    
    if invoice_data.get('tax_percent', 0) > 0:
        totals_data.append([
            '', '', '', f"Tax ({invoice_data['tax_percent']}%):", f"₹{invoice_data['tax_amount']:.2f}"
        ])
    
    totals_data.append([
        '', '', '', 'Total:', f"₹{invoice_data['total']:.2f}"
    ])
    
    totals_table = Table(totals_data, colWidths=[0.5*inch, 3*inch, 0.8*inch, 1.2*inch, 1.5*inch])
    totals_table.setStyle(TableStyle([
        ('ALIGN', (3, 0), (-1, -1), 'RIGHT'),
        ('FONTNAME', (3, 0), (-1, -2), 'Helvetica'),
        ('FONTNAME', (3, -1), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (3, 0), (-1, -1), 11),
        ('LINEABOVE', (3, -1), (-1, -1), 2, colors.HexColor('#1E3A8A')),
        ('TOPPADDING', (3, -1), (-1, -1), 10),
    ]))
    
    elements.append(totals_table)
    elements.append(Spacer(1, 0.5*inch))
    
    # Footer
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.grey,
        alignment=TA_CENTER
    )
    
    elements.append(Paragraph("<b>Thank you for your business!</b>", footer_style))
    elements.append(Spacer(1, 0.1*inch))
    elements.append(Paragraph("This is a computer generated invoice.", footer_style))
    
    # Build PDF
    doc.build(elements)
    
    # Get PDF data
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data

def get_next_invoice_number(user_id):
    """Generate next invoice number for user"""
    import database as db
    
    # Get all transactions to find last invoice number
    # Format: INV-USERID-0001
    transactions = db.get_transactions(user_id)
    
    if not transactions:
        return f"INV-{user_id:03d}-0001"
    
    # Find highest invoice number
    max_num = 0
    prefix = f"INV-{user_id:03d}-"
    
    for trans in transactions:
        desc = trans.get('description', '')
        if desc.startswith(prefix):
            try:
                num = int(desc.split('-')[-1])
                max_num = max(max_num, num)
            except:
                pass
    
    next_num = max_num + 1
    return f"{prefix}{next_num:04d}"