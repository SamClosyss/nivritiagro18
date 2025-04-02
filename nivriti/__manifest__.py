{
    'name': 'Nivriti',
    'author': 'Closyss Technologies',
    'depends': ['stock', 'sale', 'account', 'mrp','purchase', 'product', 'sale_stock','crm'],
    'data': [
        'security/ir.model.access.csv',
        'security/data.xml',
        'views/stock.xml',
        'views/sale.xml',
        'views/account.xml',
        'pdf/bg_tax_invoice_report.xml',
        'pdf/bg_dc_report.xml',
        'pdf/sale_quotation.xml',
        'pdf/purchase_report_with_logo.xml',
        'pdf/header_footer.xml',
        'views/product_partner.xml',
        'wizard/delivery_email.xml',
        # 'wizard/sale_line.xml',
        'data/data.xml',
    ],
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
